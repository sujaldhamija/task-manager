import hashlib
import json
import random
import string
from flask import Flask, request
from mysql_con import mycursor
import datetime

app = Flask(__name__)


# this function handle dates to convert them to string
def default(o):
    if type(o) is datetime.date or type(o) is datetime.datetime:
        return o.isoformat()


# this function handles all the responses of apis to send them back in json form
def response(code, message, data=''):
    res = {'code': code, 'message': message}
    if data:
        res['data'] = data
    return json.dumps(res, default=default)


# this function is used for user authentication in every api
def user_auth(token):
    query = "SELECT id, auth_token_expiry FROM users WHERE auth_token = %s"
    mycursor.execute(query, (token,))
    data = mycursor.fetchone()
    if not data:
        raise Exception('User not found or the token is expired')
    if data['auth_token_expiry'] < datetime.datetime.now():
        raise Exception('Token expired so please create a new one by logging in')
    return data['id']


# generates auth token and if given username then updates the auth token for the user
def generate_auth_token(username=None):
    auth_token = ''.join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(30))
    if username is not None:
        expiry = datetime.datetime.now() + datetime.timedelta(days=1)
        query = "UPDATE users SET auth_token = %s, auth_token_expiry = %s WHERE username = %s"
        mycursor.execute(query, (auth_token, expiry, username))
    return auth_token


# this function handles user signup
def user_sign_up(username, password):
    password = hashlib.md5(password.encode()).hexdigest()
    query = "INSERT INTO users (username, password, auth_token, auth_token_expiry) VALUES (%s, %s, %s, %s)"
    auth_token = ''.join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(30))
    expiry = datetime.datetime.now() + datetime.timedelta(days=1)
    mycursor.execute(query, (username, password, auth_token, expiry))
    return mycursor.rowcount


# this function handles user login
def user_login(username, password):
    password = hashlib.md5(password.encode()).hexdigest()
    query = "SELECT username, auth_token,auth_token_expiry FROM users WHERE username = %s AND password = %s"
    mycursor.execute(query, (username, password))
    e = mycursor.fetchone()
    if not e:
        return False
    if e['auth_token_expiry'] < datetime.datetime.now():
        e['auth_token'] = generate_auth_token(username)
    del e['auth_token_expiry']  # was giving some error and it was unnecessary to return so removed it
    return e


def check_task_access(user_id, task_id):
    query = f'''
            SELECT a.id
                FROM tasks AS a
                         LEFT JOIN tasks_assigned AS b ON b.task_id = a.id
                WHERE a.id = {task_id}
                  AND (a.created_by = {user_id} OR b.assigned_to = {user_id})
    '''
    mycursor.execute(query)
    data = mycursor.fetchall()
    return len(data) > 0


# all routes are given below

@app.route('/signup', methods=['POST'])
def signup():
    post_data = json.loads(request.data)
    try:
        if 'username' in post_data and 'password' in post_data:
            result = user_sign_up(post_data['username'], post_data['password'])
            if not result:
                raise 'signup failed'
            return response(200, 'signup successful')
        else:
            raise 'Missing username or password'
    except Exception as e:
        return response(500, str(e))


@app.route('/login', methods=['POST'])
def login():
    post_data = json.loads(request.data)
    try:
        if 'username' in post_data and 'password' in post_data:
            result = user_login(post_data['username'], post_data['password'])
            if not result:
                return response(500, 'Incorrect username or password')
            return response(200, 'login successful', result)
        else:
            raise 'Missing username or password'
    except Exception as e:
        return response(500, str(e))


@app.route('/create-task', methods=['POST'])
def create_task():
    post_data = json.loads(request.data)
    try:
        if 'auth' not in post_data:
            raise Exception('Missing username or password')
        if 'title' not in post_data or 'desc' not in post_data or 'due_date' not in post_data:
            raise Exception('Missing title or desc or due_date')
        user_check = user_auth(post_data['auth'])
        query = "INSERT INTO tasks (title, description, due_date, created_by) VALUES (%s, %s, %s, %s)"
        mycursor.execute(query, (post_data['title'], post_data['desc'], post_data['due_date'], user_check))
        if mycursor.rowcount == 1:
            return response(200, 'Task created successfully')
        raise Exception('Task creation failed')
    except Exception as e:
        return response(500, str(e))


@app.route('/get-tasks', methods=['POST'])
def get_tasks():
    post_data = json.loads(request.data)
    try:
        if 'auth' not in post_data:
            raise Exception('Missing username or password')
        user_check = user_auth(post_data['auth'])
        where = [f"(a.created_by = {user_check} OR b.assigned_to = {user_check})"]
        if 'task_id' in post_data:
            where.append(f"a.id = {post_data['task_id']}")
        query = f'''SELECT a.*
                    FROM tasks AS a
                             LEFT JOIN tasks_assigned AS b ON b.task_id = a.id
                    WHERE  {" AND ".join(where)}'''
        mycursor.execute(query)
        data = mycursor.fetchall()

        if not data:
            raise Exception('Task not found')
        if 'task_id' in post_data:
            data = data[0]
        return response(200, 'Tasks retrieved successfully', data)
    except Exception as e:
        return response(500, str(e))


@app.route('/update-task', methods=['POST'])
def update_task():
    post_data = json.loads(request.data)
    try:
        if 'auth' not in post_data:
            raise Exception('Missing username or password')
        elif 'task_id' not in post_data:
            raise Exception('Task id missing')
        elif 'title' not in post_data and 'desc' not in post_data and 'due_date' not in post_data and 'status' not in post_data:
            raise Exception('You have to send something to update')
        elif 'status' in post_data:
            if post_data['status'] not in ['todo', 'inprogress', 'done']:
                raise Exception('Invalid Status')
        user_auth(post_data['auth'])
        updatable_fields = ['title', 'desc', 'due_date', 'status']
        updates = {}
        for key, value in post_data.items():
            if key in updatable_fields:
                updates[key] = value
        update_final = []
        for key, value in updates.items():
            key = key if key != 'desc' else 'description'
            update_final.append(f"{key} = '{value}'")
        if len(update_final) == 0:
            raise Exception('Error while updating')
        query = f"UPDATE tasks SET {", ".join(update_final)} WHERE id = {post_data['task_id']}"
        mycursor.execute(query)
        if mycursor.rowcount == 1:
            return response(200, 'Task updated successfully')
    except Exception as e:
        return response(500, str(e))


@app.route('/delete-task', methods=['POST'])
def delete_task():
    post_data = json.loads(request.data)
    try:
        if 'auth' not in post_data:
            raise Exception('Missing username or password')
        elif 'task_id' not in post_data:
            raise Exception('Task id missing')
        user_check = user_auth(post_data['auth'])
        if not check_task_access(user_check, post_data['task_id']):
            raise Exception('You can not delete this task')
        query = f"DELETE FROM tasks WHERE id = {post_data['task_id']}"
        mycursor.execute(query)
        if mycursor.rowcount == 1:
            return response(200, 'Task deleted successfully')
        raise Exception('Task was not found')
    except Exception as e:
        return response(500, str(e))


@app.route('/update-access-task', methods=['POST'])
def update_access_task():
    post_data = json.loads(request.data)
    try:
        if 'auth' not in post_data:
            raise Exception('Missing username or password')
        elif 'task_id' not in post_data or 'type' not in post_data or 'users' not in post_data:
            raise Exception('"Task id" or "type" or ""users" to assign or remove" is missing')
        elif post_data['type'] not in ['assign', 'remove']:
            raise Exception('Invalid Type')
        user_check = user_auth(post_data['auth'])
        if not check_task_access(user_check, post_data['task_id']):
            raise Exception('You can not add or remove users of this task')
        if post_data['type'] == 'assign':
            query = f'''
                INSERT INTO tasks_assigned(task_id, assigned_to, assigned_by)
                    SELECT a.id, b.id, {user_check}
                    FROM tasks AS a
                             LEFT JOIN users AS b ON b.id IN ({', '.join(str(i) for i in post_data['users'])})
                             LEFT JOIN tasks_assigned AS c ON c.task_id = a.id AND c.assigned_to = b.id
                    WHERE a.id = {post_data['task_id']}
                      AND a.created_by != b.id
                      AND c.id IS NULL;
            '''
            # in the above query i have used advance query of mysql in which
            # if the user is assigned already then the user will not get assigned again
            # and user who created the task always have access to the task until it is deleted
            # so the user itself is not assigned and is handled with in the query of mysql
        else:
            query = f'''
                    DELETE FROM tasks_assigned 
                        WHERE assigned_to IN ({', '.join(str(i) for i in post_data['users'])})
                            AND 
                        task_id = {post_data['task_id']}
            '''
        mycursor.execute(query)
        return response(200, 'Task access updated successfully')
    except Exception as e:
        return response(500, str(e))


@app.route('/task-access', methods=['POST'])
def task_access():
    post_data = json.loads(request.data)
    try:
        if 'auth' not in post_data:
            raise Exception('Missing username or password')
        user_auth(post_data['auth'])
        con1 = ''
        con2 = ''
        res = {}
        if 'task_id' in post_data:
            con1 = f"WHERE id = {post_data['task_id']}"
            con2 = f"WHERE task_id = {post_data['task_id']}"

        query = f'''
            SELECT id AS task_id, created_by AS assigned_to
                FROM tasks
            {con1}
                UNION
            SELECT task_id, assigned_to
                FROM tasks_assigned
            {con2}
        '''
        mycursor.execute(query)
        data = mycursor.fetchall()
        if len(data) == 0:
            raise Exception('Tasks not found')
        for i in data:
            if i['task_id'] not in res:
                res[i['task_id']] = {'task_id': i['task_id'], 'users_id': []}
            res[i['task_id']]['users_id'].append(i['assigned_to'])
        return response(200, 'Data fetched successful', list(res.values()))
    except Exception as e:
        return response(500, str(e))


if __name__ == '__main__':
    app.run(debug=True)


# Task Management API

This project is a simple task management system built with Flask and MySQL. It allows users to create, update, delete, and manage tasks, including assigning tasks to different users and checking access rights.

## Features

- **User Authentication:** Users must sign up and log in to obtain an auth token. This token is required for all subsequent API requests.
- **Task Management:** 
  - Create tasks with a title, description, and due date.
  - Update task details such as title, description, due date, or status.
  - Delete tasks that a user has access to.
- **Task Access Management:** Assign or remove access to tasks for other users. 
- **View Tasks:** Get all tasks or specific tasks that a user has access to.

## API Endpoints

### 1. User Authentication

- **Signup:** `/signup`  
  Request: 
  ```json
  {
    "username": "required",
    "password": "required"
  }
  ```

- **Login:** `/login`  
  Request: 
  ```json
  {
    "username": "required",
    "password": "required"
  }
  ```
  Response:
  ```json
  {
    "auth_token": "token_value"
  }
  ```

### 2. Task Operations

- **Create Task:** `/create_task`  
  Request:
  ```json
  {
    "auth": "required",
    "title": "optional",
    "desc": "optional",
    "due_date": "optional (YYYY-MM-DD)"
  }
  ```

- **Get Tasks:** `/get_tasks`  
  Request:
  ```json
  {
    "auth": "required",
    "task_id": "optional"
  }
  ```

- **Update Task:** `/update_task`  
  Request:
  ```json
  {
    "auth": "required",
    "task_id": "required",
    "title": "optional",
    "desc": "optional",
    "due_date": "optional (YYYY-MM-DD)",
    "status": "optional ('todo', 'inprogress', 'done')"
  }
  ```

- **Delete Task:** `/delete_task`  
  Request:
  ```json
  {
    "auth": "required",
    "task_id": "required"
  }
  ```

### 3. Task Access Management

- **Update Task Access:** `/update-access-task`  
  Request:
  ```json
  {
    "auth": "required",
    "task_id": "required",
    "type": "required ('assign', 'remove')",
    "users": "required array of user IDs"
  }
  ```

- **View Task Access:** `/task-access`  
  Request:
  ```json
  {
    "auth": "required",
    "task_id": "optional"
  }
  ```

## MySQL Setup

This project uses a MySQL database to store user and task information. The database connection is configured in the `mysql_con.py` file.

### Tables

You need to create the following tables in your MySQL database:

- **users**
- **tasks**
- **tasks_assigned**

## License

This project is licensed under the MIT License.

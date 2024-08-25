
# Task Management API - Endpoints and Parameters

This document details the API endpoints available in the Task Management API, including required parameters and descriptions.

## 1. `/signup` - User Signup
- **Method:** POST
- **Description:** Allows a new user to sign up and create an account.
- **Parameters:**
  - `username`: (required) The username of the new user.
  - `password`: (required) The password for the new account.

## 2. `/login` - User Login
- **Method:** POST
- **Description:** Authenticates the user and returns an authentication token.
- **Parameters:**
  - `username`: (required) The username of the user.
  - `password`: (required) The password of the user.

## 3. `/create_task` - Create a New Task
- **Method:** POST
- **Description:** Creates a new task.
- **Parameters:**
  - `auth`: (required) Authentication token.
  - `title`: (optional, but one of title, desc, or due_date is required) The title of the task.
  - `desc`: (optional, but one of title, desc, or due_date is required) The description of the task.
  - `due_date`: (optional, but one of title, desc, or due_date is required) The due date of the task in `YYYY-MM-DD` format.

## 4. `/get_tasks` - Get Tasks
- **Method:** POST
- **Description:** Retrieves tasks that the authenticated user has access to. Can retrieve a specific task by `task_id` or all tasks.
- **Parameters:**
  - `auth`: (required) Authentication token.
  - `task_id`: (optional) The ID of the task to retrieve. If not provided, all tasks the user has access to will be retrieved.

## 5. `/update_task` - Update a Task
- **Method:** POST
- **Description:** Updates a task's details. The user must have access to the task.
- **Parameters:**
  - `auth`: (required) Authentication token.
  - `task_id`: (required) The ID of the task to update.
  - `title`: (optional) The new title of the task.
  - `desc`: (optional) The new description of the task.
  - `due_date`: (optional) The new due date of the task in `YYYY-MM-DD` format.
  - `status`: (optional) The new status of the task. Must be one of 'todo', 'inprogress', or 'done'.

## 6. `/delete_task` - Delete a Task
- **Method:** POST
- **Description:** Deletes a task. The user must have access to the task.
- **Parameters:**
  - `auth`: (required) Authentication token.
  - `task_id`: (required) The ID of the task to delete.

## 7. `/update-access-task` - Update Task Access
- **Method:** POST
- **Description:** Allows a user to assign or remove other users' access to a task. The user must have access to the task.
- **Parameters:**
  - `auth`: (required) Authentication token.
  - `task_id`: (required) The ID of the task for which access is being updated.
  - `type`: (required) Must be either 'assign' or 'remove'.
  - `users`: (required) An array of user IDs to assign or remove access for.

## 8. `/task-access` - View Task Access
- **Method:** POST
- **Description:** Retrieves the list of users who have access to a specific task.
- **Parameters:**
  - `auth`: (required) Authentication token.
  - `task_id`: (optional) The ID of the task to view access for. If not provided, all tasks the user has access to will be displayed.

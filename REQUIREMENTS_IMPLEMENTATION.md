# Day 2 Requirements Added

This backend now satisfies the given requirements without removing the existing `/` and `/review` APIs.

## 1. Global Exception Handling

Added global exception handlers in `main.py`:

- `HTTPException` handler
- `RequestValidationError` handler
- Generic `Exception` handler

All errors now return clean JSON responses like:

```json
{
  "status": "error",
  "message": "Invalid request data",
  "path": "/api/register"
}
```

## 2. Logging Using Database and Logging Framework

Added Python logging framework setup in:

- `logging_config.py`
- `database.py`

The backend now logs request activity and errors into a SQLite database table called `api_logs`.

Database file auto-created when backend runs:

```text
backend/ai_code_reviewer.db
```

Do not manually create this file. It is generated automatically.

## 3. JSON API Endpoints

### Register

```http
POST /api/register
```

Request body:

```json
{
  "email": "student@example.com",
  "password": "pass1234",
  "profileImage": "optional-base64-image"
}
```

### Login

```http
POST /api/login
```

Request body:

```json
{
  "email": "student@example.com",
  "password": "pass1234"
}
```

### User

```http
GET /api/user/{user_id}
PATCH /api/user/{user_id}
GET /api/users
```

PATCH request body:

```json
{
  "profileImage": "updated-base64-image"
}
```

### Log

```http
POST /api/log
GET /api/logs
GET /api/log
```

POST request body:

```json
{
  "level": "INFO",
  "message": "Manual log message from frontend or Postman"
}
```

## Existing APIs Preserved

These existing endpoints still work:

```http
GET /
POST /review
```

Compatibility endpoints were also added for JSON-server style routes:

```http
GET /users
POST /users
PATCH /users/{user_id}
```

## How to Run Backend

From the `backend` folder:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

## What to Tell Sir

Implemented global exception handling, SQLite database-backed logging using Python logging framework, and JSON APIs for register, login, user profile, and logs. Existing `/review` API was preserved.

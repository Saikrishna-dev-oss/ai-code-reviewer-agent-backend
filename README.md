# AI Code Reviewer Agent Backend

A robust Python backend for AI-driven code review with authentication, logging, and comprehensive error handling.

## ✨ Features

### 1. **Global Exception Handling**
- Centralized exception handler for all unhandled exceptions
- Custom exception classes for specific error scenarios
- Detailed error responses with traceback in debug mode
- Automatic logging of all exceptions

### 2. **Database & Logging Framework**
- SQLAlchemy ORM for database operations
- Structured logging with both file and console output
- Database logging for audit trails and analytics
- Rotating file handlers to manage log files
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### 3. **API Endpoints**

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

#### Users
- `GET /api/users/me` - Get current user information
- `GET /api/users` - List all users (paginated)
- `GET /api/users/{user_id}` - Get user by ID

#### Logs
- `POST /api/logs` - Create a log entry
- `GET /api/logs` - Get logs with filtering
- `GET /api/logs/user/{user_id}` - Get logs for specific user

#### Code Review
- `POST /api/review` - Submit code for review

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/anjali03102005/ai-code-reviewer-agent-backend.git
   cd ai-code-reviewer-agent-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

---

## 📝 Configuration

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=sqlite:///./ai_code_reviewer.db

# JWT
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

---

## 🔒 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Getting a Token

1. Register a user:
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "email": "john@example.com",
       "password": "securepassword"
     }'
   ```

2. Login to get token:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "password": "securepassword"
     }'
   ```

3. Use the token in requests:
   ```bash
   curl -X GET http://localhost:8000/api/users/me \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

---

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 Project Structure

```
ai-code-reviewer-agent-backend/
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── database.py                # Database setup and session
├── models.py                  # SQLAlchemy models (User, Log)
├── schemas.py                 # Pydantic schemas for validation
├── crud.py                    # Database operations
├── auth.py                    # Authentication logic
├── utils.py                   # Utility functions (JWT, password hashing)
├── exceptions.py              # Custom exception classes
├── logger_setup.py            # Logging configuration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

---

## 🛡️ Exception Handling

The application includes:

- **Global Exception Handler**: Catches all unhandled exceptions
- **Custom Exceptions**:
  - `UserAlreadyExistsException` - User registration conflicts
  - `InvalidCredentialsException` - Authentication failures
  - `TokenExpiredException` - Expired JWT tokens
  - `InvalidTokenException` - Invalid or missing tokens
  - `UserNotFoundException` - User not found
  - `ValidationException` - Input validation errors

All exceptions are logged automatically with full context.

---

## 📋 Logging

Logs are written to:
1. **Console**: Real-time application output
2. **File** (`app.log`): Rotating logs (10MB, keeps 5 backups)
3. **Database**: Audit trail and analytics

Log levels:
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potential issues
- `ERROR` - Error messages for failures
- `CRITICAL` - Critical errors requiring immediate attention

---

## 🧪 Testing

Example curl commands:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' | jq -r '.access_token')

# Get current user
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"

# List users
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN"

# Get logs
curl -X GET http://localhost:8000/api/logs \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🔗 Related Projects

- [AI Code Reviewer Frontend](https://github.com/anjali03102005/ai-code-reviewer-agent-frontend)
- [Original Backend](https://github.com/Saikrishna-dev-oss/ai-code-reviewer-agent-backend)

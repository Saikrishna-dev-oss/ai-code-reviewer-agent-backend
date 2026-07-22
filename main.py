from __future__ import annotations
from fastapi.responses import StreamingResponse
import logging
from typing import List
from sqlite3 import IntegrityError
from time import perf_counter

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import APIRouter

from auth_utils import hash_password, verify_password
from database import (
    create_user,
    get_api_logs,
    get_user_by_email,
    get_user_by_id,
    init_db,
    list_users,
    public_user,
    update_user_profile_image,
)
from logging_config import configure_logging

from schemas import LoginRequest, LogCreateRequest, RegisterRequest, UserUpdateRequest, GitHubIngestRequest, CodebaseReviewRequest, FileReviewRequest
from connect import get_github_repo_tree, GITHUB_TOKEN

from agent import CodeReviewAgent

# ------------------- FastAPI Setup -------------------

# Create FastAPI app instance with a title
app = FastAPI(title="AI Code Reviewer API")

# Enable CORS so frontend (React/Vite on localhost:5173) can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables and configure logging system
init_db()
logger = configure_logging()


# ------------------- Middleware -------------------

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """
    Middleware that logs every API request.
    - Records duration in ms.
    - Logs success or failure into the logging framework.
    """
    start_time = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # Log unhandled exceptions
        logger.exception(
            "Unhandled request failure",
            extra={"method": request.method, "path": request.url.path, "status_code": 500},
        )
        raise

    # Log request completion with duration
    duration_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} completed in {duration_ms} ms",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    return response


# ------------------- Exception Handlers -------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for HTTP errors (e.g., 404, 401)."""
    logger.warning(
        f"HTTP error: {exc.detail}",
        extra={"method": request.method, "path": request.url.path, "status_code": exc.status_code},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail, "path": request.url.path},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles validation errors when request body doesn't match schema."""
    logger.warning(
        "Validation error",
        extra={"method": request.method, "path": request.url.path, "status_code": 422},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Invalid request data",
            "errors": exc.errors(),
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected server errors."""
    logger.exception(
        f"Unhandled server error: {exc}",
        extra={"method": request.method, "path": request.url.path, "status_code": 500},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Something went wrong on the server.", "path": request.url.path},
    )


# ------------------- Basic Endpoints -------------------

@app.get("/")
def read_root():
    """Simple root endpoint to confirm API is running."""
    return {"message": "Hello World. The AI Backend is running."}


# ------------------- AI Review Endpoint -------------------

@app.post("/api/review")
def generate_architecture_review(req: CodebaseReviewRequest):
    """Analyzes the repository architecture by routing it to the CodeReviewAgent."""
    logger.info(f"Starting AI review for {len(req.files)} files", extra={"method": "POST", "path": "/api/review", "status_code": 200})
    
    # 1. Format the data for the agent
    repo_structure = ""
    for f in req.files:
        repo_structure += f"- {f.fileName} ({f.category}, {f.loc} LOC)\n"

    # 2. Instantiate our new reusable agent class
    agent = CodeReviewAgent()

    # 3. Return the stream directly from the agent
    return StreamingResponse(
        agent.generate_review_stream(repo_structure, len(req.files)), 
        media_type="text/plain"
    )

# ------------------- Helper Functions -------------------

def validate_email(email: str) -> str:
    """Ensure email is valid format (basic check for '@' and '.')."""
    cleaned_email = email.strip().lower()
    if "@" not in cleaned_email or "." not in cleaned_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a valid email address.")
    return cleaned_email


def register_user_logic(payload: RegisterRequest) -> dict:
    """Business logic for registering a new user."""
    email = validate_email(payload.email)

    # Prevent duplicate registration
    if get_user_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists with this email.")

    try:
        user = create_user(
            email=email,
            password_hash=hash_password(payload.password),
            profile_image=payload.profileImage,
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists with this email.")

    logger.info(f"New user registered: {email}", extra={"method": "POST", "path": "/api/register", "status_code": 201})
    return {"status": "success", "message": "Registration successful", "user": user}


def login_user_logic(payload: LoginRequest) -> dict:
    """Business logic for user login with password verification."""
    email = validate_email(payload.email)
    user_row = get_user_by_email(email)

    if not user_row or not verify_password(payload.password, user_row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    logger.info(f"User logged in: {email}", extra={"method": "POST", "path": "/api/login", "status_code": 200})
    return {"status": "success", "message": "Login successful", "user": public_user(user_row)}


# ------------------- User Endpoints -------------------

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    """Register a new user using JSON request data."""
    return register_user_logic(payload)


@app.post("/api/login")
def login(payload: LoginRequest):
    """Login using JSON request data."""
    return login_user_logic(payload)


@app.get("/api/user/{user_id}")
def get_user(user_id: int):
    """Return one user as JSON without exposing password data."""
    row = get_user_by_id(user_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return {"status": "success", "user": public_user(row)}


@app.patch("/api/user/{user_id}")
def update_user(user_id: int, payload: UserUpdateRequest):
    """Update the user's profile image through JSON."""
    updated_user = update_user_profile_image(user_id, payload.profileImage)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    logger.info(f"User profile updated: {user_id}", extra={"method": "PATCH", "path": f"/api/user/{user_id}", "status_code": 200})
    return {"status": "success", "message": "User updated", "user": updated_user}


@app.get("/api/users")
def get_users():
    """Return all users as JSON. Useful for testing/admin demo."""
    return {"status": "success", "users": list_users()}


# ------------------- Logging Endpoints -------------------

@app.post("/api/log", status_code=status.HTTP_201_CREATED)
def create_log(payload: LogCreateRequest):
    """Create a manual application log using JSON request data."""
    numeric_level = getattr(logging, payload.level.upper(), logging.INFO)
    logger.log(numeric_level, payload.message, extra={"method": "POST", "path": "/api/log", "status_code": 201})
    return {"status": "success", "message": "Log saved", "latestLog": get_api_logs(limit=1)[0]}


@app.get("/api/logs")
def get_logs(limit: int = 50):
    """Return database logs as JSON."""
    return {"status": "success", "logs": get_api_logs(limit=limit)}


@app.get("/api/log")
def get_log_alias(limit: int = 50):
    """Alias endpoint because requirement mentions 'log' singular."""
    return get_logs(limit=limit)


@app.get("/api/health")
def health_check():
    """Simple endpoint to verify API + database logging setup."""
    return {"status": "success", "message": "API, exception handling, and DB logging are active."}

@app.post("/api/ingest/github")
def ingest_github(payload: GitHubIngestRequest):
    """Fetch a GitHub repository's file architecture."""
    logger.info(f"Starting GitHub ingestion for: {payload.repoUrl}", extra={"method": "POST", "path": "/api/ingest/github", "status_code": 200})
    
    try:
        # Call our PyGithub engine
        tree_data = get_github_repo_tree(payload.repoUrl, GITHUB_TOKEN)
        
        return {
            "status": "success",
            "message": "Repository successfully ingested.",
            "totalFiles": len(tree_data),
            "files": tree_data
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(re))
    
@app.post("/api/review/file")
async def review_single_file(request: FileReviewRequest):
    try:
        # 1. Extract the data sent by React
        file_name = request.fileName
        code_content = request.content
        history = request.chatHistory
        
        # 2. Check if the user typed a custom message or just requested a review
        if history and history[-1]["sender"] == "You":
            user_text = history[-1]["text"]
            mock_response = f"I see you said: '{user_text}'. I am currently a mock agent, but the real AI will process this request once the API keys are active!"
        else:
            mock_response = f"I have received `{file_name}`. It contains {len(code_content.splitlines())} lines of code. How can I help you improve it?"
        
        # 3. Send the response back to React
        return {"sender": "Agent", "text": mock_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------- Legacy Endpoints -------------------
# These mimic JSON-server style endpoints for compatibility with older frontend code.

@app.get("/users")
def legacy_get_users(email: str | None = None, password: str | None = None):
    """Legacy endpoint: fetch users or login if email+password provided."""
    if email and password:
        try:
            result = login_user_logic(LoginRequest(email=email, password=password))
            return [result["user"]]
        except HTTPException:
            return []
    return list_users()

@app.post("/users", status_code=status.HTTP_201_CREATED)
def legacy_create_user(payload: RegisterRequest):
    result = register_user_logic(payload)
    return result["user"]


@app.patch("/users/{user_id}")
def legacy_update_user(user_id: int, payload: UserUpdateRequest):
    result = update_user(user_id, payload)
    return result["user"]
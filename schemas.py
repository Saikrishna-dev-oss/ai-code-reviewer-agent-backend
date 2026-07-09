"""Pydantic models for JSON request and response bodies.

These models define the structure and validation rules for incoming API requests.
They ensure that data sent to the backend is properly typed and validated.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """
    Model for user registration requests.
    - email: must be between 3 and 120 characters.
    - password: must be between 4 and 100 characters.
    - profileImage: optional string (URL or path to profile image).
    """
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=4, max_length=100)
    profileImage: str | None = None


class LoginRequest(BaseModel):
    """
    Model for user login requests.
    - email: must be between 3 and 120 characters.
    - password: must be at least 1 character, max 100.
    """
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=1, max_length=100)


class UserUpdateRequest(BaseModel):
    """
    Model for updating user profile information.
    - profileImage: optional string (URL or path to new profile image).
    """
    profileImage: str | None = None


class LogCreateRequest(BaseModel):
    """
    Model for creating application logs.
    - level: logging level (INFO, WARNING, ERROR, etc.), default is INFO.
    - message: log message, must be between 1 and 500 characters.
    """
    level: str = Field(default="INFO", max_length=20)
    message: str = Field(..., min_length=1, max_length=500)

class GitHubIngestRequest(BaseModel):
    repoUrl: str = Field(..., min_length=5, max_length=200)
"""Pydantic models for JSON request and response bodies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=4, max_length=100)
    profileImage: str | None = None


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=1, max_length=100)


class UserUpdateRequest(BaseModel):
    profileImage: str | None = None


class LogCreateRequest(BaseModel):
    level: str = Field(default="INFO", max_length=20)
    message: str = Field(..., min_length=1, max_length=500)

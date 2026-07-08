# 🧠 AI-Code Reviewer Agent (Backend)

A production-grade Python backend built with **FastAPI** to power the AI-driven code review agent. 

This repository serves as the secure data layer and API gateway, handling user authentication, request validation, global error handling, and eventual AI model integration.

---

## 📑 Table of Contents
- [About](#about)
- [Core Features](#core-features)
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
- [Interactive API Docs](#interactive-api-docs)
- [Project Structure](#project-structure)

---

## 📖 About
Designed with a decoupled microservice architecture, this backend provides a robust RESTful API that communicates seamlessly with the React frontend. It utilizes an embedded SQLite database and enforces strict data validation to ensure a secure, zero-friction user experience.

---

## ✨ Core Features
- ⚡ **FastAPI Framework:** High-performance, asynchronous REST API.
- 🔐 **Secure Authentication:** Implements SHA-256 cryptographic salting and hashing for secure user credential storage.
- 🗄️ **Embedded SQLite Database:** Zero-config database handling user profiles and system state.
- 🛡️ **Pydantic Validation:** Strict request/response payload validation to prevent bad data from hitting the database.
- 📜 **Custom Logging Engine:** A custom SQLite log handler that intercepts global HTTP exceptions and records chronological system events.
- 🚦 **Global Exception Handlers:** Graceful error interception returning clean, formatted JSON (401, 404, 409, 422).

---

## 💻 Requirements
- Python **3.8+** (3.10+ recommended)
- `pip` (Python package manager)
- Embedded SQLite3 (Built into Python)

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Saikrishna-dev-oss/ai-code-reviewer-agent-backend.git
   cd ai-code-reviewer-agent-backend

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate  #windows
   ```

3. **Install the required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend**
   ```bash
   uvicorn main:app --reload

   The backend will be running at `http://localhost:8000`. You can send requests to this endpoint for code review.
   ```

### 📂 Project Structure

```
ai-code-reviewer-agent-backend/
│
├── main.py                # FastAPI app routing and global exception handlers
├── database.py            # SQLite connection, table creation, and queries
├── schemas.py             # Pydantic models for strict JSON validation
├── auth_utils.py          # Cryptographic hashing and verification logic
├── logging_config.py      # Custom SQLite logging handlers and formatting
├── requirements.txt       # Python dependency list
├── .gitignore             # Ignored files (including the .db file)
└── README.md              # Project documentation
```
---

## LICENSE
This Project is under the MIT License. See the [LICENSE](LICENSE) file for details.

### In development:
- [Configuration](#configuration)
- [Contributing](#contributing)

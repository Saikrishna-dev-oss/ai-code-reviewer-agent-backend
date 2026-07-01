from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="AI Code Reviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World. The AI Backend is running."}

@app.post("/review")
def mock_review():
    
    return {
        "status": "success",
        "review": "This is a mock AI code review. The files look structurally sound."
        "Good job! However, please ensure to follow best practices and coding standards for your specific programming language."
    }
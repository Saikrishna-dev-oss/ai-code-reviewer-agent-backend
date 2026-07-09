"""
GitHub Repository Ingestion Engine
----------------------------------
This script connects to the GitHub API to recursively read and extract the file
structure and contents of a target repository. It uses a Personal Access Token (PAT)
to bypass the standard 60-request/hour rate limit, upgrading it to 5,000/hour,
allowing it to read massive codebases without crashing.
"""

import os
import argparse
from github import Github
from github import Auth
from dotenv import load_dotenv

# ---------------------------------------------------------
# Configuration & Secrets Management
# ---------------------------------------------------------
# We use python-dotenv to securely load the GitHub token from a local .env file.
# This prevents the token from being accidentally committed to version control.
load_dotenv()

# The `or ""` fallback satisfies strict type checkers (like Pylance).
# It guarantees GITHUB_TOKEN is always a string, even if the .env file is missing.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or ""


def get_github_repo_tree(repo_name: str, token: str) -> list[dict]:
    """
    Connects to GitHub, traverses the repository, and returns a structured JSON tree.
    """
    if not token:
        raise ValueError("GITHUB_TOKEN is missing from the environment.")

    auth = Auth.Token(token)
    g = Github(auth=auth)
    file_tree = []

    try:
        # Clean the input just in case the frontend sends a full URL instead of "user/repo"
        clean_repo_name = repo_name.replace("https://github.com/", "").strip("/")
        repo = g.get_repo(clean_repo_name)

        def traverse_directory(path: str = ""):
            contents = repo.get_contents(path)
            
            if not isinstance(contents, list):
                contents = [contents]
            
            for item in contents:
                if item.type == "dir":
                    traverse_directory(item.path)
                else:
                    # Instead of printing, we build a dictionary for the frontend
                    file_tree.append({
                        "path": item.path,
                        "size": item.size,
                        "url": item.html_url
                    })

        traverse_directory()
        return file_tree

    except Exception as e:
        raise RuntimeError(f"Failed to fetch repository: {str(e)}")
    finally:
        g.close()

# ---------------------------------------------------------
# Command Line Interface (CLI) Setup
# ---------------------------------------------------------
if __name__ == "__main__":
    # argparse allows developers to pass the repository name directly in the terminal
    # Example: python connect.py Saikrishna-dev-oss/ai-code-reviewer-agent-backend
    parser = argparse.ArgumentParser(description="Fetch files from a GitHub repository.")
    
    parser.add_argument(
        "repo", 
        type=str, 
        help="The target repository in format 'username/repo-name'"
    )
    
    # Extract the arguments typed in the terminal
    args = parser.parse_args()
    
    # Final validation check before execution
    if not GITHUB_TOKEN:
        print("❌ Error: Missing GITHUB_TOKEN. Please add it to your .env file.")
    else:
        # Execute the main engine
        get_github_repo_tree(args.repo, GITHUB_TOKEN)
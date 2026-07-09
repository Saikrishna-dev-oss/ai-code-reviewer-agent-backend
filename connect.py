import os
import requests  # 🚀 Standard library for downloading the raw file text
from github import Github
from github import Auth
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or ""

def get_github_repo_tree(repo_name: str, token: str) -> list[dict]:
    """
    Connects to GitHub, traverses the repository, and downloads the raw code securely.
    """
    if not token:
        raise ValueError("GITHUB_TOKEN is missing from the environment.")

    auth = Auth.Token(token)
    g = Github(auth=auth)
    file_tree = []

    try:
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
                    file_content = ""
                    try:
                        # Protect backend memory: Only read files under 100KB
                        if item.size < 100000:
                            # 🚀 THE FIX: Physically download the raw text from GitHub
                            if item.download_url:
                                headers = {"Authorization": f"token {token}"}
                                response = requests.get(item.download_url, headers=headers, timeout=10)
                                
                                if response.status_code == 200:
                                    file_content = response.text
                                    # Add this line to print the first 50 characters to your terminal!
                                    print(f"✅ Read {len(file_content)} characters from {item.path}")
                                else:
                                    file_content = f"// HTTP {response.status_code}: Failed to download."
                            else:
                                file_content = "// No download URL provided by GitHub."
                        else:
                            file_content = "// File skipped: Exceeds 100KB size limit."
                    except Exception as e:
                        file_content = f"// Error reading file: {str(e)}"

                    # Add the real content to the JSON payload
                    file_tree.append({
                        "path": item.path,
                        "size": item.size,
                        "url": item.html_url,
                        "content": file_content
                    })

        traverse_directory()
        return file_tree

    except Exception as e:
        raise RuntimeError(f"Failed to fetch repository: {str(e)}")
    finally:
        g.close()
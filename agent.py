# agent.py
import os
import time
import logging
from typing import Any, cast
from openai import OpenAI

logger = logging.getLogger(__name__)

class CodeReviewAgent:
    """
    A standalone, reusable AI Agent class for codebase architectural reviews.
    This class handles all LLM routing and streaming logic independent of the web framework.
    """
    
    def __init__(self):
        # The coordinator's proxy configuration
        self.endpoint = os.getenv("AGENT_ENDPOINT", "http://localhost:8000") + "/api/v1/"
        self.access_key = os.getenv("AGENT_ACCESS_KEY", "dummy_key_waiting_for_coordinator")
        
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.access_key,
        )

    def generate_review_stream(self, repo_structure: str, total_files: int):
        """
        Calls the AI model and yields the response chunk-by-chunk.
        If API keys are missing/invalid, safely yields a mock typewriter stream.
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert AI Software Architect. Review the provided repository structure and analyze its design, scalability, and potential security flaws."
            },
            {
                "role": "user",
                "content": f"Please review this codebase architecture:\n\n{repo_structure}\n\nProvide a high-level summary, identify any missing standard files (like .gitignore or README), and suggest architectural improvements."
            }
        ]

        try:
            # 🚀 Attempt the Real AI Call
            response = self.client.chat.completions.create(
                model="n/a",
                messages=cast(Any, messages),
                extra_body={"include_retrieval_info": True},
                stream=True 
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.warning(f"AI Stream Failed (Expected without keys): {str(e)}. Falling back to Mock Stream.")
            
            # The Safe Fallback Stream (if API KEY is not there)
            mock_review = f"**[MOCK REVIEW]**\n\nI received your repository containing **{total_files} files**.\n\n### Architectural Summary\n* **Structure:** The codebase looks well-categorized based on the provided file tree.\n* **Next Steps:** Once the real API keys are injected, I will stream a deep-dive analysis of the system design right here.\n\n*Connection successfully closed.*"
            
            # typewriter effect 
            for char in mock_review:
                yield char
                time.sleep(0.01)
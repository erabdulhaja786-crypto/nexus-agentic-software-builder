import os

from dotenv import load_dotenv
from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MODEL
)

client = Groq(
    api_key=GROQ_API_KEY
)


def planner_agent(state):
    requirement = state["user_requirement"].strip()

    plan = f"""
SOFTWARE DEVELOPMENT PLAN

User Requirement:
{requirement}

Steps:
1. Identify the required application features.
2. Design the user interface and user interactions.
3. Select suitable technologies.
4. Implement the requested features.
5. Create automated tests.
6. Run tests and fix failures.
7. Build the production application.

Requirements:
- Preserve the user's requested functionality.
- Avoid unrelated features.
- Ensure the application is responsive.
- Ensure the project can be tested and built.
"""

    print("Local Planner: Plan generated.")

    return {"plan": plan}


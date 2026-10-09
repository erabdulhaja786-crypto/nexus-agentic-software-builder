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


def architect_agent(state):
    requirement = state["user_requirement"].strip()

    architecture = f"""
APPLICATION ARCHITECTURE

USER REQUIREMENT:
{requirement}

Choose the simplest suitable technology for the actual request.

SUPPORTED PROJECT TYPES:

1. React + Vite
   Use for interactive web applications, dashboards, portfolios,
   and frontend projects that benefit from React.

2. Python + Streamlit
   Use for data dashboards, data analysis tools, ML demos,
   and Python-based interactive applications.

3. Python + FastAPI
   Use for REST APIs and backend services.

4. Python CLI
   Use for command-line utilities and automation scripts.

TECHNOLOGY SELECTION RULES:

* Match the user's requirement, not a fixed template.
* If the user explicitly requests a technology, prefer it.
* Do not use React for a Python-only CLI or API request.
* Do not use Streamlit when a REST API is explicitly requested.
* Keep the implementation focused on the requested features.
* If the requirement is ambiguous, choose a sensible default
  and state the choice in the generated project README.
* Do not claim external services work without configuring them.
* Do not invent API keys, credentials, or external data.
* Use environment variables for secrets.
* Include a README with installation and run instructions.
* Include meaningful tests where practical.
* Do not create unnecessary files.

OUTPUT EXPECTATIONS:

The Coder Agent must generate a complete runnable project.
Every local import must resolve.
Include dependency manifests and actual source files.
Use relative paths in FILE markers.
Do not return directory-only FILE markers.
Avoid placeholders, TODO sections, and incomplete code.

The project must be validated using commands appropriate
for its selected technology.
"""

    print("Architect: Requirement-based architecture generated.")

    return {"architecture": architecture}


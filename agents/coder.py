
import os

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL

load_dotenv()

client = Groq(api_key=GROQ_API_KEY)

SUPPORTED_STACKS = """
Choose the most suitable stack:
- React + Vite for interactive web frontends.
- Python + Streamlit for interactive Python apps.
- Python + FastAPI for REST APIs.
- Python CLI for command-line tools.
Respect explicit technology choices in the requirement.
"""

def coder_agent(state):
    requirement = state.get("user_requirement", "").strip()
    plan = state.get("plan", "")
    architecture = state.get("architecture", "")
    retry_count = state.get("retry_count", 0)

    if not requirement:
        return {
            "generated_code": "",
            "status": "FAILED",
            "error": "Missing user requirement."
        }

    is_repair = retry_count > 0
    error = str(state.get("error", ""))
    error_analysis = str(state.get("error_analysis", ""))

    if is_repair:
        prompt = f"""
You are a debugging software engineer.

USER REQUIREMENT:
{requirement}

EXISTING ARCHITECTURE:
{architecture[:1500]}

VALIDATION ERRORS:
{error[:3000]}

ERROR ANALYSIS:
{error_analysis[:1000]}

TASK:
Return the complete corrected project. Preserve the original
technology stack and all required functionality.

Include every required source file, local import, dependency
manifest, README, and practical tests.

Do not include explanations outside the file sections.
Do not use placeholders or incomplete code.

SUPPORTED STACKS:
{SUPPORTED_STACKS}

OUTPUT FORMAT:
**FILE: relative/path**
**LANGUAGE: language**

```language
complete file contents
```

Return only FILE sections.
"""
    else:
        prompt = f"""
You are the Coder Agent in a software-building system.

USER REQUIREMENT:
{requirement}

PLAN:
{plan[:1800]}

ARCHITECTURE:
{architecture[:2200]}

TASK:

Generate only essential application files, required dependencies,
README, and practical tests.

Do not generate GitHub workflows, issue templates, deployment
pipelines, editor settings, pre-commit files, or duplicate files
unless explicitly requested.

Do not create .env files containing secrets or credentials.
Preserve the existing project structure and working functionality.
Generate a complete, runnable project that satisfies the
user requirement.

Include all required source files, local imports, dependencies,
a README with setup instructions, and tests where practical.

Use environment variables for secrets. Do not invent credentials.
Do not include unrelated features, placeholders, or explanations
outside the file sections.

For Streamlit, document: streamlit run app.py
For FastAPI, document the correct API startup command.
For React + Vite, include package.json and working build scripts.

SUPPORTED STACKS:
{SUPPORTED_STACKS}

OUTPUT FORMAT:
**FILE: relative/path**
**LANGUAGE: language**

```language
complete file contents
```

Return only FILE sections.
"""

    from tools.file_manager import parse_generated_code

    max_attempts = 3
    configured_tokens = int(os.getenv("CODER_MAX_TOKENS", "8192"))
    last_error = "No usable response received"

    for attempt in range(1, max_attempts + 1):
        # On retries, use a smaller response budget to avoid
        # repeatedly making an oversized generation request.
        if attempt == 1:
            token_budget = configured_tokens
        else:
            token_budget = min(configured_tokens, 4096)

        print(f"\nCoder LLM attempt {attempt}/{max_attempts}")
        print(f"Model: {GROQ_MODEL}")
        print(f"Token budget: {token_budget}")
        print(f"Mode: {'REPAIR' if is_repair else 'NEW PROJECT'}")

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert software engineer. "
                            "Return complete project files in the "
                            "requested FILE format."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
                max_completion_tokens=token_budget,
            )

            if not response.choices:
                last_error = "Groq returned no response choices."
                print(last_error)
                continue

            choice = response.choices[0]
            message = choice.message
            generated_code = (message.content or "").strip()

            print(f"Finish reason: {choice.finish_reason}")
            print(f"Response characters: {len(generated_code)}")

            if not generated_code:
                last_error = (
                    "Groq returned empty content. "
                    f"finish_reason={choice.finish_reason}. "
                    "Check the model, token budget, and API response."
                )
                print(last_error)

                if is_repair:
                    return {
                        "generated_code": "",
                        "status": "FAILED",
                        "error": last_error,
                     }

                # Shorten the next request if the model returned
                # no usable text.
                prompt = (
                    "Generate a complete runnable project for this "
                    "requirement. Return only complete FILE sections.\n\n"
                    f"REQUIREMENT:\n{requirement}\n\n"
                    f"ARCHITECTURE:\n{architecture[:1000]}\n\n"
                    f"VALIDATION ERRORS:\n{error[:1500]}\n\n"
                    "Format:\n"
                    "**FILE: relative/path**\n"
                    "**LANGUAGE: language**\n"
                    "```language\ncomplete file contents\n```\n"
                )
                continue

            parsed_files = parse_generated_code(generated_code)

            if not parsed_files:
                last_error = (
                    "The model returned text, but no valid FILE "
                    "sections were found."
                )
                print(last_error)

                prompt += (
                    "\nIMPORTANT: Your previous output was not parsed "
                    "into files. Return strictly formatted FILE sections "
                    "with complete file contents."
                )
                continue

            usable_files = {
                name: data
                for name, data in parsed_files.items()
                if isinstance(data, dict)
                and data.get("code", "").strip()
            }

            if not usable_files:
                last_error = "FILE sections contained no usable code."
                print(last_error)
                continue

            print(
                f"Coder response: PASS "
                f"({len(usable_files)} usable files)"
            )

            return {
                "generated_code": generated_code,
                "status": "SUCCESS",
                "error": "",
            }

        
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(f"Coder attempt failed: {last_error}")

            if type(exc).__name__ == "RateLimitError":
                clean_error = (
                    "Groq rate limit reached. "
                    "Wait for quota reset or use another model "
                    "with available quota. "
                    f"Details: {exc}"
                )
                print(clean_error)

                return {
                    "generated_code": "",
                    "status": "FAILED",
                    "error": clean_error,
                }

    clean_error = (
        f"Coder Agent failed after {max_attempts} attempts. "
        f"Last error: {last_error}"
    )

    print(clean_error)

    return {
        "generated_code": "",
        "status": "FAILED",
        "error": clean_error,
    }
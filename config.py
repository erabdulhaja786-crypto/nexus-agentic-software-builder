import os

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GROQ API KEY
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env"
    )


# ============================================================
# GROQ MODEL
# ============================================================

GROQ_MODEL = "openai/gpt-oss-20b"
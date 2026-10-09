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

# ============================================================
# ERROR ANALYZER AGENT
# ============================================================

def error_analyzer_agent(state):
    """
    Analyze the Observer error and produce
    a concise correction plan.

    Important:
    We intentionally do NOT send the complete
    generated source code to Groq.

    This keeps the request below the Groq
    8,000 TPM limit.
    """

    requirement = state[
        "user_requirement"
    ]

    architecture = state[
        "architecture"
    ]

    error = state.get(
        "error",
        ""
    )


    # ========================================================
    # LIMIT ARCHITECTURE SIZE
    # ========================================================

    architecture_for_analysis = architecture[
        :5000
    ]


    # ========================================================
    # ERROR ANALYSIS PROMPT
    # ========================================================

    prompt = f"""
You are an expert software debugging agent.

The Observer/Tester found a problem in a
generated software project.

USER REQUIREMENT:
{requirement}

ARCHITECTURE:
{architecture_for_analysis}

OBSERVER ERROR:
{error}

Analyze ONLY the reported Observer error.

Return:

1. ERROR
2. ROOT CAUSE
3. REQUIRED FIX
4. FILES THAT NEED TO BE CHANGED
5. DETAILED FIX INSTRUCTIONS

Rules:

- Focus only on the reported error.
- Do not invent unrelated problems.
- Identify the most likely root cause.
- Give practical correction instructions.
- Keep the solution consistent with the architecture.
- Do not generate complete source code.
- Keep the response concise.

Return only the debugging analysis.
"""


    # ========================================================
    # CALL GROQ
    # ========================================================

    response = client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )


    # ========================================================
    # GET ANALYSIS
    # ========================================================

    analysis = (
        response
        .choices[0]
        .message
        .content
    )


    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================

    return {

        "error": error,

        "test_result": "FAIL",

        "status": "ERROR_ANALYZED",

        "error_analysis": analysis
    }
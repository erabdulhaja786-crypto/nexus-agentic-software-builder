from agents.error_analyzer import (
    error_analyzer_agent
)


state = {

    "user_requirement":
        "Build a simple calculator web application",

    "plan":
        """
        Create a calculator web application
        with HTML, CSS and JavaScript.
        """,

    "architecture":
        """
        The application contains:
        index.html
        calculator.js
        ui.js
        styles.css
        """,

    "generated_code":
        """
        index.html references index.js.

        The generated project actually contains:
        calculator.js
        ui.js
        """,

    "project_path":
        r"C:\AI PROJECTS\Agentic Software Builder"
        r"\generated_projects\calculator_app",

    "test_result":
        "FAIL",

    "error":
        "Referenced JavaScript file not found: index.js",

    "error_analysis":
        "",

    "retry_count":
        0,

    "status":
        "FAILED"
}


result = error_analyzer_agent(
    state
)


print()
print("==========================================")
print(" ERROR ANALYZER TEST")
print("==========================================")

print()

print(
    "Status:",
    result["status"]
)

print()

print(
    "Observer Error:"
)

print(
    result["error"]
)

print()

print(
    "=========================================="
)

print(
    " ERROR ANALYSIS"
)

print(
    "=========================================="
)

print()

print(
    result["error_analysis"]
)
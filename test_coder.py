from agents.coder import coder_agent


state = {
    "user_requirement": "Build a simple calculator web application",

    "plan": """
1. Create calculator user interface.
2. Add number and operator buttons.
3. Implement addition, subtraction,
   multiplication, and division.
4. Add decimal support.
5. Add keyboard support.
6. Add clear functionality.
7. Handle division by zero.
""",

    "architecture": """
Project:

calc-lite/

Files:

index.html
style.css
script.js

index.html:
Contains the calculator interface and buttons.

style.css:
Contains responsive calculator styling.

script.js:
Contains calculator logic, button handling,
keyboard handling, and error handling.

The application should be dependency-free
and runnable directly in a browser.
""",

    "generated_code": "",
    "project_path": "",
    "test_result": "",
    "error": "",
    "retry_count": 0,
    "status": ""
}


result = coder_agent(state)


print("\n========== CODER OUTPUT ==========\n")

print(result["generated_code"])
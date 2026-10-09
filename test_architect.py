from agents.architect import architect_agent


state = {
    "user_requirement": "Build a simple calculator web application",

    "plan": """
1. Create calculator user interface.
2. Add number and operator buttons.
3. Implement arithmetic operations.
4. Add decimal support.
5. Add keyboard support.
6. Add error handling.
7. Test the calculator.
""",

    "architecture": "",
    "generated_code": "",
    "project_path": "",
    "test_result": "",
    "error": "",
    "retry_count": 0,
    "status": ""
}


result = architect_agent(state)


print("\n========== ARCHITECT OUTPUT ==========\n")

print(result["architecture"])
from agents.observer import observer_agent


state = {
    "user_requirement": "Build a simple calculator web application",

    "plan": "",

    "architecture": "",

    "generated_code": "",

    "project_path": (
        r"C:\AI PROJECTS\Agentic Software Builder"
        r"\generated_projects\calculator_app"
    ),

    "test_result": "",

    "error": "",

    "retry_count": 0,

    "status": ""
}


result = observer_agent(state)


print("\n==========================================")
print(" TEST RESULT")
print("==========================================")

print("\nStatus:")
print(result["status"])

print("\nTest Result:")
print(result["test_result"])

print("\nError:")

if result["error"]:
    print(result["error"])
else:
    print("No errors found.")
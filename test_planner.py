from agents.planner import planner_agent


state = {
    "user_requirement": "Build a simple calculator web application",
    "plan": "",
    "architecture": "",
    "generated_code": "",
    "project_path": "",
    "test_result": "",
    "error": "",
    "retry_count": 0,
    "status": ""
}


result = planner_agent(state)


print("\n========== PLANNER OUTPUT ==========\n")

print(result["plan"])
from graph.builder_graph import app


# ============================================================
# INITIAL STATE
# ============================================================

initial_state = {
    "user_requirement": (
        "Build a Todo application where users can add tasks, "
        "mark tasks as completed, delete tasks, and see "
        "completed and pending task counts."
        ),

    "plan":
        "",

    "architecture":
        "",

    "generated_code":
        "",

    "project_path":
        "",

    "test_result":
        "",

    "error":
        "",

    "error_analysis":
        "",

    "retry_count":
        0,

    "status":
        ""
}


# ============================================================
# START
# ============================================================

print()

print("=" * 50)

print(
    " LANGGRAPH AGENTIC WORKFLOW"
)

print("=" * 50)

print()

print(
    "Starting workflow..."
)

print()


# ============================================================
# RUN GRAPH
# ============================================================

result = app.invoke(
    initial_state
)


# ============================================================
# RESULT
# ============================================================

print()

print("=" * 50)

print(
    " WORKFLOW COMPLETE"
)

print("=" * 50)

print()

print(
    "Project Path:"
)

print(
    result["project_path"]
)

print()

print(
    "Test Result:"
)

print(
    result["test_result"]
)

print()

print(
    "Retry Count:"
)

print(
    result["retry_count"]
)

print()

print(
    "Status:"
)

print(
    result["status"]
)

print()

# ============================================================
# ERROR
# ============================================================

if result["error"]:

    print(
        "Last Error:"
    )

    print(
        result["error"]
    )

    print()


# ============================================================
# FINAL STATUS
# ============================================================

print("=" * 50)

if result["test_result"] == "PASS":

    print(
        " APPLICATION PASSED"
    )

else:

    print(
        " APPLICATION FAILED"
    )

print("=" * 50)
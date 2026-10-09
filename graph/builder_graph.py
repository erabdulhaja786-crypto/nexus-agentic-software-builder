from langgraph.graph import StateGraph, END

from graph.state import AgentState

from agents.planner import planner_agent
from agents.architect import architect_agent
from agents.coder import coder_agent
from agents.observer import observer_agent
from agents.error_analyzer import error_analyzer_agent

from tools.file_manager import create_project_files
import re

# ============================================================
# FILE MANAGER NODE
# ============================================================

def file_manager_node(state):
    requirement = state["user_requirement"]

    project_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        requirement.lower()
    ).strip("_")[:40]

    if not project_name:
        project_name = "generated_app"

    result = create_project_files(
        state["generated_code"],
        project_name=project_name,
        clean_existing=(
            state.get("retry_count", 0) == 0
        )
    )

    return {
        "project_path": result["project_path"],
        "status": "FILES_CREATED"
    }


# ============================================================
# PREPARE RETRY
# ============================================================

def prepare_retry_node(state):

    retry_count = state.get(
        "retry_count",
        0
    )

    return {
        "retry_count": retry_count + 1,
        "status": "RETRYING"
    }


# ============================================================
# OBSERVER ROUTER
# ============================================================

def observer_router(state):

    test_result = state.get(
        "test_result",
        ""
    )

    retry_count = state.get(
        "retry_count",
        0
    )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if test_result == "PASS":

        return "end"

    # --------------------------------------------------------
    # MAX RETRIES
    # --------------------------------------------------------

    if retry_count >= 3:

        return "end"

    # --------------------------------------------------------
    # ERROR ANALYSIS
    # --------------------------------------------------------

    return "error_analyzer"


# ============================================================
# ERROR ANALYZER ROUTER
# ============================================================

def error_analyzer_router(state):

    return "prepare_retry"



# ============================================================
# SAFE CODER NODE
# ============================================================

def safe_coder_node(state):
    try:
        result = coder_agent(state)
        generated_code = result.get("generated_code", "").strip()

        if not generated_code or "FILE:" not in generated_code.upper():
            return {
                "generated_code": "",
                "error": "Coder returned empty or invalid code.",
                "error_analysis": "",
                "coder_failed": True,
                "status": "CODER_FAILED"
            }

        return {
            **result,
            "coder_failed": False,
            "error": "",
            "status": "CODE_GENERATED"
        }

    except Exception as exc:
        message = f"Coder error: {type(exc).__name__}: {exc}"
        print(message)

        return {
            "generated_code": "",
            "error": message,
            "error_analysis": "",
            "coder_failed": True,
            "status": "CODER_FAILED"
        }


# ============================================================
# CODER ROUTER
# ============================================================

def coder_router(state):
    if not state.get("coder_failed", False):
        return "file_manager"

    if state.get("retry_count", 0) >= 3:
        return "end"

    return "error_analyzer"


# ============================================================
# BUILD LANGGRAPH
# ============================================================

workflow = StateGraph(
    AgentState
)


# ============================================================
# ADD NODES
# ============================================================

workflow.add_node(
    "planner",
    planner_agent
)

workflow.add_node(
    "architect",
    architect_agent
)

workflow.add_node(
    "coder",
    safe_coder_node
)

workflow.add_conditional_edges(
    "coder",
    coder_router,
    {
        "file_manager": "file_manager",
        "error_analyzer": "error_analyzer",
        "end": END
    }
)

workflow.add_node(
    "observer",
    observer_agent
)

workflow.add_node(
    "error_analyzer",
    error_analyzer_agent
)

workflow.add_node(
    "prepare_retry",
    prepare_retry_node
)


# ============================================================
# ENTRY
# ============================================================

workflow.set_entry_point(
    "planner"
)


# ============================================================
# NORMAL FLOW
# ============================================================

workflow.add_edge(
    "planner",
    "architect"
)

workflow.add_edge(
    "architect",
    "coder"
)

workflow.add_edge(
    "coder",
    "file_manager"
)

workflow.add_edge(
    "file_manager",
    "observer"
)


# ============================================================
# OBSERVER CONDITIONAL FLOW
# ============================================================

workflow.add_conditional_edges(
    "observer",
    observer_router,
    {
        "end": END,
        "error_analyzer": "error_analyzer"
    }
)


# ============================================================
# ERROR → RETRY
# ============================================================

workflow.add_edge(
    "error_analyzer",
    "prepare_retry"
)

workflow.add_edge(
    "prepare_retry",
    "coder"
)


# ============================================================
# COMPILE
# ============================================================

app = workflow.compile()
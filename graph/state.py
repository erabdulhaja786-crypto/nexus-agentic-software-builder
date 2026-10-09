from typing import TypedDict


class AgentState(TypedDict, total=False):
    user_requirement: str
    plan: str
    architecture: str
    generated_code: str
    project_path: str

    retry_count: int
    test_result: str
    error: str
    error_analysis: str
    coder_failed: bool
    status: str
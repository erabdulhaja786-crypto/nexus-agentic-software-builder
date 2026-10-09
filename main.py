import json
import os
import re
import subprocess
import sys
from pathlib import Path

from agents.planner import planner_agent
from agents.architect import architect_agent
from agents.coder import coder_agent
from tools.file_manager import create_project_files, parse_generated_code


MAX_REPAIR_ROUNDS = 3
COMMAND_TIMEOUT = 300


def run_command(command, project_path, label):
    print(f"\n{'=' * 50}\n RUNNING: {label}\n{'=' * 50}")

    try:
        result = subprocess.run(
            command,
            cwd=project_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=COMMAND_TIMEOUT,
            shell=False,
        )

        output = (
            (result.stdout or "") + "\n" + (result.stderr or "")
        ).strip()

        print(output[-6000:] if output else "No command output.")
        print(f"\nExit code: {result.returncode}")

        return {
            "success": result.returncode == 0,
            "output": output,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        message = f"{label} timed out after {COMMAND_TIMEOUT} seconds."
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"

    print(message)
    return {"success": False, "output": message, "returncode": -1}


def project_slug(requirement):
    """Create a safe, readable folder name from the user's requirement."""

    words = re.findall(r"[a-zA-Z0-9]+", requirement.lower())
    slug = "_".join(words[:7]).strip("_")
    return (slug or "generated_app")[:70]


def validate_node_project(project_path):
    package_file = Path(project_path) / "package.json"

    if not package_file.is_file():
        return {
            "success": False,
            "test_result": "FAILED",
            "error": "Node project is missing package.json.",
        }

    try:
        package_data = json.loads(package_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "success": False,
            "test_result": "FAILED",
            "error": f"Invalid package.json: {exc}",
        }

    scripts = package_data.get("scripts", {})

    missing = [
        name for name in ("test", "build")
        if not scripts.get(name)
    ]

    if missing:
        return {
            "success": False,
            "test_result": "FAILED",
            "error": "Missing package.json scripts: " + ", ".join(missing),
        }

    install = run_command(
        ["npm", "install", "--no-audit", "--no-fund"],
        project_path,
        "INSTALL NODE DEPENDENCIES",
    )

    if not install["success"]:
        return {
            "success": False,
            "test_result": "FAILED",
            "error": "npm install failed:\n" + install["output"][-8000:],
        }

    tests = run_command(
        ["npm", "test"],
        project_path,
        "AUTOMATED TESTS",
    )

    build = run_command(
        ["npm", "run", "build"],
        project_path,
        "PRODUCTION BUILD",
    )

    errors = []

    if not tests["success"]:
        errors.append("TESTS FAILED:\n" + tests["output"][-6000:])

    if not build["success"]:
        errors.append("BUILD FAILED:\n" + build["output"][-6000:])

    success = tests["success"] and build["success"]

    return {
        "success": success,
        "test_result": "PASS" if success else "FAILED",
        "error": "\n\n".join(errors),
    }


def validate_python_project(project_path):
    root = Path(project_path)
    requirements = root / "requirements.txt"

    if requirements.is_file():
        install = run_command(
            [
                sys.executable, "-m", "pip", "install",
                "-r", str(requirements),
            ],
            project_path,
            "INSTALL PYTHON DEPENDENCIES",
        )

        if not install["success"]:
            return {
                "success": False,
                "test_result": "FAILED",
                "error": "Dependency installation failed:\n"
                         + install["output"][-8000:],
            }

    source_files = [
        path for path in root.rglob("*.py")
        if ".venv" not in path.parts
        and "venv" not in path.parts
        and "__pycache__" not in path.parts
    ]

    if not source_files:
        return {
            "success": False,
            "test_result": "FAILED",
            "error": "No Python source files were generated.",
        }

    compile_result = run_command(
        [sys.executable, "-m", "compileall", "-q", "."],
        project_path,
        "PYTHON SYNTAX CHECK",
    )

    if not compile_result["success"]:
        return {
            "success": False,
            "test_result": "FAILED",
            "error": "Python syntax check failed:\n"
                     + compile_result["output"][-8000:],
        }

    test_files = [
        path for path in source_files
        if path.name.startswith("test_") or path.name.endswith("_test.py")
    ]

    if test_files:
        tests = run_command(
            [sys.executable, "-m", "pytest", "-q"],
            project_path,
            "PYTHON TESTS",
        )

        if not tests["success"]:
            return {
                "success": False,
                "test_result": "FAILED",
                "error": "Python tests failed:\n"
                         + tests["output"][-8000:],
            }

        test_message = "Python syntax check and tests passed."
    else:
        test_message = (
            "Python syntax check passed. No automated test files "
            "were found, so functional behavior is not fully verified."
        )

    return {
        "success": True,
        "test_result": "PASS" if test_files else "SYNTAX PASS",
        "error": test_message,
    }


def validate_project(project_path):
    root = Path(project_path)

    if (root / "package.json").is_file():
        return validate_node_project(project_path)

    python_manifests = (
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
    )

    if (
        any((root / name).is_file() for name in python_manifests)
        or (root / "app.py").is_file()
        or (root / "main.py").is_file()
    ):
        return validate_python_project(project_path)

    if (root / "index.html").is_file():
        return {
            "success": True,
            "test_result": "BASIC CHECK",
            "error": (
                "Static HTML project detected. Files were generated, "
                "but no browser-based functional test was run."
            ),
        }

    return {
        "success": False,
        "test_result": "FAILED",
        "error": (
            "Could not identify a supported project type. "
            "Expected package.json, a Python project entry point, "
            "or index.html."
        ),
    }


def run_builder(user_requirement):
    state = {
        "user_requirement": user_requirement,
        "plan": "",
        "architecture": "",
        "generated_code": "",
        "project_path": "",
        "test_result": "",
        "error": "",
        "error_analysis": "",
        "retry_count": 0,
        "status": "",
    }

    print("\n========== PLANNER AGENT ==========")
    state.update(planner_agent(state))

    print("\n========== ARCHITECT AGENT ==========")
    state.update(architect_agent(state))

    print("\n========== CODER AGENT ==========")
    generation = coder_agent(state)
    state.update(generation)

    if not state.get("generated_code", "").strip():
        state["status"] = "FAILED"
        state["error"] = state.get("error") or "Coder returned no code."

        existing_project = (
            Path(__file__).resolve().parent
            / "generated_projects"
            / project_slug(user_requirement)
        )

        if existing_project.is_dir():
            state["project_path"] = str(existing_project)

        print(state["error"])

        if state["project_path"]:
            print(
                "An existing project folder was found:",
                state["project_path"],
            )

        return state

    project_name = project_slug(user_requirement)

    for repair_round in range(MAX_REPAIR_ROUNDS + 1):
        print(f"\n{'=' * 50}")
        print(f" VALIDATION ROUND: {repair_round + 1}")
        print("=" * 50)

        try:
            project_result = create_project_files(
                state["generated_code"],
                project_name=project_name,
                clean_existing=True,
            )
        except Exception as exc:
            state["status"] = "FAILED"
            state["error"] = (
                f"Project file creation failed: {type(exc).__name__}: {exc}"
            )
            print(state["error"])
            break

        state["project_path"] = project_result["project_path"]

        print("\nProject path:", state["project_path"])
        print("\nFiles created:")
        for file_path in project_result["files"]:
            print("  [OK]", file_path)

        validation = validate_project(state["project_path"])
        state["test_result"] = validation["test_result"]
        state["error"] = validation.get("error", "")

        if validation["success"]:
            state["status"] = "PASS"
            print("\nALL AVAILABLE VALIDATIONS PASSED")
            break

        if repair_round == MAX_REPAIR_ROUNDS:
            state["status"] = "FAILED"
            print("\nNo repair attempts remaining.")
            break

        state["retry_count"] = repair_round + 1
        state["error_analysis"] = (
            "Fix the actual validation errors. Preserve the original "
            "user requirement and selected technology.\n\n"
            + state["error"]
        )

        print(
            f"\nRepair attempt {state['retry_count']} "
            f"of {MAX_REPAIR_ROUNDS}"
        )

        try:
            repair_result = coder_agent(state)
            candidate_code = repair_result.get("generated_code", "")

            if not candidate_code.strip():
                raise ValueError("Coder returned an empty response.")

            if not parse_generated_code(candidate_code):
                raise ValueError(
                    "Coder response contains no valid FILE sections."
                )

            state.update(repair_result)
            state["generated_code"] = candidate_code
            state["status"] = "REPAIRING"

        except Exception as exc:
            state["status"] = "FAILED"
            state["error"] = (
                f"Repair generation failed: {type(exc).__name__}: {exc}"
            )
            print(state["error"])
            break

    print("\n" + "=" * 50)
    print(" BUILDER COMPLETE")
    print("=" * 50)
    print("Status:", state["status"])
    print("Validation:", state["test_result"])
    print("Repair rounds used:", state["retry_count"])
    print("Project:", state["project_path"])

    if state["error"]:
        print("\nDetails:")
        print(state["error"])

    return state


if __name__ == "__main__":
    requirement = input(
        "\nEnter your software requirement:\n> "
    ).strip()

    if not requirement:
        print("Requirement cannot be empty.")
        raise SystemExit(1)

    try:
        final_state = run_builder(requirement)

        if final_state["status"] != "PASS":
            raise SystemExit(1)

    except KeyboardInterrupt:
        print("\nBuilder interrupted by user.")
        raise SystemExit(130)
    except Exception as exc:
        print(
            f"\nBuilder encountered an error: "
            f"{type(exc).__name__}: {exc}"
        )
        raise SystemExit(1)
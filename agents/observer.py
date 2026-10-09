import os
import re
import json
import subprocess


def run_command(command, project_path, timeout=120):
    try:
        result = subprocess.run(
            command,
            cwd=project_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=True
        )

        output = ""

        if result.stdout:
            output += result.stdout

        if result.stderr:
            output += "\n" + result.stderr

        return (
            result.returncode == 0,
            output.strip()
        )

    except subprocess.TimeoutExpired:
        return (
            False,
            f"Command timed out after {timeout} seconds."
        )

    except Exception as error:
        return False, str(error)


def repair_vite_dependencies(project_path):
    package_path = os.path.join(
        project_path,
        "package.json"
    )

    config_path = os.path.join(
        project_path,
        "vite.config.js"
    )

    if not os.path.isfile(package_path):
        return False, "package.json not found."

    with open(
        package_path,
        "r",
        encoding="utf-8"
    ) as file:
        package = json.load(file)

    dependencies = package.setdefault(
        "dependencies",
        {}
    )

    dev_dependencies = package.setdefault(
        "devDependencies",
        {}
    )

    if os.path.isfile(config_path):
        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:
            vite_config = file.read()

        if "@vitejs/plugin-react" in vite_config:
            dev_dependencies.setdefault(
                "@vitejs/plugin-react",
                "^4.7.0"
            )

    with open(
        package_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            package,
            file,
            indent=2
        )

    return True, "Vite dependencies checked."

# ============================================================
# OBSERVER AGENT
# ============================================================


def observer_agent(state):
    project_path = state.get("project_path", "")

    print()
    print("=" * 50)
    print(" OBSERVER / TESTER AGENT")
    print("=" * 50)

    # Validate the project folder before accessing its files.
    if not project_path or not os.path.isdir(project_path):
        print("Project folder: FAIL")
        return {
            "test_result": "FAIL",
            "error": (
                f"Generated project folder does not exist: "
                f"{project_path!r}"
            ),
            "status": "FAILED"
        }

    print("Project folder: PASS")

    # Check and repair package dependencies.
    try:
        repair_success, repair_message = (
            repair_vite_dependencies(project_path)
        )
    except Exception as exc:
        repair_success = False
        repair_message = (
            f"Dependency configuration error: "
            f"{type(exc).__name__}: {exc}"
        )

    print()
    print("Dependency repair:", repair_message)

    if not repair_success:
        return {
            "test_result": "FAIL",
            "error": repair_message,
            "status": "FAILED"
        }

    # ========================================================
    # PROJECT FOLDER
    # ========================================================

    if not os.path.exists(project_path):

        print()
        print("Project folder: FAIL")

        return {
            "test_result": "FAIL",
            "error": (
                "Generated project folder "
                "does not exist."
            ),
            "status": "FAILED"
        }

    print()
    print("Project folder: PASS")

    # ========================================================
    # FIND FILES
    # ========================================================

    files = []

    for root, directories, filenames in os.walk(
        project_path
    ):

        for filename in filenames:

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                project_path
            )

            files.append(
                relative_path
            )

    print()
    print("Files found:")

    for filename in files:

        print(
            f"  [OK] {filename}"
        )

    # ========================================================
    # HTML VALIDATION
    # ========================================================

    html_files = [
        file
        for file in files
        if file.lower().endswith(".html")
    ]

    if not html_files:

        return {
            "test_result": "FAIL",
            "error": "No HTML file found.",
            "status": "FAILED"
        }

    for html_file in html_files:

        html_path = os.path.join(
            project_path,
            html_file
        )

        with open(
            html_path,
            "r",
            encoding="utf-8"
        ) as file:

            html_code = file.read()

        html_lower = html_code.lower()

        required_html = [
            "<html",
            "<head",
            "<body",
            "</html>"
        ]

        for tag in required_html:

            if tag not in html_lower:

                return {
                    "test_result": "FAIL",
                    "error": (
                        f"HTML validation failed "
                        f"in {html_file}: "
                        f"{tag} not found."
                    ),
                    "status": "FAILED"
                }

    print()
    print("HTML structure: PASS")

    # ========================================================
    # CSS VALIDATION
    # ========================================================

    css_files = [
        file
        for file in files
        if file.lower().endswith(".css")
    ]

    for css_file in css_files:

        css_path = os.path.join(
            project_path,
            css_file
        )

        with open(
            css_path,
            "r",
            encoding="utf-8"
        ) as file:

            css_code = file.read()

        if not css_code.strip():

            return {
                "test_result": "FAIL",
                "error": (
                    f"CSS file is empty: "
                    f"{css_file}"
                ),
                "status": "FAILED"
            }

    print()
    print("CSS validation: PASS")

    # ========================================================
    # JAVASCRIPT / JSX VALIDATION
    # ========================================================

    js_files = [
        file
        for file in files
        if file.lower().endswith(
            (
                ".js",
                ".jsx"
            )
        )
    ]

    for js_file in js_files:

        js_path = os.path.join(
            project_path,
            js_file
        )

        with open(
            js_path,
            "r",
            encoding="utf-8"
        ) as file:

            js_code = file.read()

        if not js_code.strip():

            return {
                "test_result": "FAIL",
                "error": (
                    f"JavaScript file is empty: "
                    f"{js_file}"
                ),
                "status": "FAILED"
            }

    print()
    print("JavaScript validation: PASS")

    # ========================================================
    # RESOURCE REFERENCES
    # ========================================================

    for html_file in html_files:

        html_path = os.path.join(
            project_path,
            html_file
        )

        with open(
            html_path,
            "r",
            encoding="utf-8"
        ) as file:

            html_code = file.read()

        # ----------------------------------------------------
        # CSS REFERENCES
        # ----------------------------------------------------

        css_references = re.findall(
            r'href=["\']([^"\']+\.css)["\']',
            html_code,
            re.IGNORECASE
        )

        for reference in css_references:

            reference = reference.split("?")[0]
            reference = reference.split("#")[0]

            if reference.startswith("/"):

                reference = reference[1:]

                reference_path = os.path.join(
                    project_path,
                    reference
                )

            else:

                html_directory = os.path.dirname(
                    html_path
                )

                reference_path = os.path.normpath(
                    os.path.join(
                        html_directory,
                        reference
                    )
                )

            if not os.path.exists(
                reference_path
            ):

                return {
                    "test_result": "FAIL",
                    "error": (
                        "Referenced CSS file "
                        f"not found: {reference}"
                    ),
                    "status": "FAILED"
                }

        # ----------------------------------------------------
        # JAVASCRIPT REFERENCES
        # ----------------------------------------------------

        js_references = re.findall(
            r'<script[^>]+src=["\']([^"\']+\.js)["\']',
            html_code,
            re.IGNORECASE
        )

        for reference in js_references:

            reference = reference.split("?")[0]
            reference = reference.split("#")[0]

            if reference.startswith("/"):

                filesystem_reference = (
                    reference.lstrip("/")
                )

                reference_path = os.path.join(
                    project_path,
                    filesystem_reference
                )

            else:

                html_directory = os.path.dirname(
                    html_path
                )

                reference_path = os.path.normpath(
                    os.path.join(
                        html_directory,
                        reference
                    )
                )

            if not os.path.exists(
                reference_path
            ):

                return {
                    "test_result": "FAIL",
                    "error": (
                        "Referenced JavaScript "
                        f"file not found: {reference}"
                    ),
                    "status": "FAILED"
                }

    print()
    print("Resource references: PASS")

    # ========================================================
    # PACKAGE.JSON
    # ========================================================

    package_json = os.path.join(
        project_path,
        "package.json"
    )

    if not os.path.exists(
        package_json
    ):

        return {
            "test_result": "FAIL",
            "error": (
                "package.json not found. "
                "Cannot execute the generated "
                "JavaScript application."
            ),
            "status": "FAILED"
        }

    print()
    print("package.json: PASS")

    # ========================================================
    # NPM CHECK
    # ========================================================

    print()
    print("Checking npm...")

    npm_success, npm_output = run_command(
        "npm --version",
        project_path,
        timeout=30
    )

    if not npm_success:

        return {
            "test_result": "FAIL",
            "error": (
                "npm is not available.\n"
                + npm_output
            ),
            "status": "FAILED"
        }

    print()
    print("npm: PASS")

    print()
    print("npm version:")
    print(npm_output)

    # ========================================================
    # NPM INSTALL
    # ========================================================

    print()
    print("=" * 50)
    print(" INSTALLING DEPENDENCIES")
    print("=" * 50)

    install_success, install_output = run_command(
        "npm install",
        project_path,
        timeout=180
    )

    if not install_success:

        print()
        print("npm install: FAIL")

        print(
            install_output
        )

        return {
            "test_result": "FAIL",
            "error": (
                "npm install failed.\n\n"
                + install_output[-5000:]
            ),
            "status": "FAILED"
        }

    print()
    print("npm install: PASS")

    # ========================================================
    # NPM BUILD
    # ========================================================

    print()
    print("=" * 50)
    print(" RUNNING APPLICATION BUILD")
    print("=" * 50)

    build_success, build_output = run_command(
        "npm run build",
        project_path,
        timeout=180
    )

    if not build_success:

        print()
        print("Application build: FAIL")

        print(
            build_output
        )

        return {
            "test_result": "FAIL",
            "error": (
                "Application build failed.\n\n"
                + build_output[-5000:]
            ),
            "status": "FAILED"
        }

    print()
    print("Application build: PASS")

    print()
    print("Build output:")
    print(
        build_output[-3000:]
    )

    # ========================================================
    # AUTOMATED TESTS
    # ========================================================

    print()
    print("=" * 50)
    print(" RUNNING AUTOMATED TESTS")
    print("=" * 50)

    test_success, test_output = run_command(
        "npm test -- --runInBand",
        project_path,
        timeout=180
    )

    if not test_success:

        print()
        print("Automated tests: FAIL")

        print(
            test_output
        )

        return {
            "test_result": "FAIL",
            "error": (
                "Automated tests failed.\n\n"
                + test_output[-5000:]
            ),
            "status": "FAILED"
        }

    print()
    print("Automated tests: PASS")

    print()
    print("Test output:")
    print(
        test_output[-3000:]
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 50)
    print(" OBSERVER RESULT: PASS")
    print("=" * 50)

    return {
        "test_result": "PASS",
        "error": "",
        "status": "PASSED"
    }
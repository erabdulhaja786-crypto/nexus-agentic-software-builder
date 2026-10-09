from agents.coder import coder_agent


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
        FILE: index.html

        LANGUAGE: HTML

        <script src="index.js"></script>

        FILE: calculator.js

        LANGUAGE: JavaScript

        function add(a, b) {
            return a + b;
        }

        FILE: ui.js

        LANGUAGE: JavaScript

        console.log("UI");

        FILE: styles.css

        LANGUAGE: CSS

        body {
            font-family: Arial;
        }
        """,

    "project_path":
        r"C:\AI PROJECTS\Agentic Software Builder"
        r"\generated_projects\calculator_app",

    "test_result":
        "FAIL",

    "error":
        "Referenced JavaScript file not found: index.js",

    "error_analysis":
        """
        ERROR:
        index.html references index.js.

        ROOT CAUSE:
        index.js does not exist.

        REQUIRED FIX:
        Update index.html so that it references
        the actual JavaScript files.
        """,

    "retry_count":
        1,

    "status":
        "FAILED"
}


print()
print("==========================================")
print(" CODER RETRY TEST")
print("==========================================")
print()


result = coder_agent(state)


print("Corrected code generated successfully.")
print()


print("==========================================")
print(" CORRECTED PROJECT")
print("==========================================")
print()


print(result["generated_code"])
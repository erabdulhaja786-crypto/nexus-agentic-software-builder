import contextlib
import io
import os
import subprocess
import sys
from pathlib import Path

import streamlit as st

from main import run_builder, project_slug


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="NEXUS | AI Software Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
GENERATED_DIR = ROOT / "generated_projects"


# --------------------------------------------------
# DARK THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --bg: #080d18;
        --panel: #101827;
        --panel2: #141f30;
        --border: #263449;
        --text: #f1f5f9;
        --muted: #91a2b8;
        --green: #34d399;
        --blue: #60a5fa;
    }

    .stApp {
        background:
            radial-gradient(
                ellipse at 10% 0%,
                rgba(16, 185, 129, 0.10),
                transparent 35%
            ),
            radial-gradient(
                ellipse at 90% 10%,
                rgba(59, 130, 246, 0.08),
                transparent 30%
            ),
            var(--bg);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #0b1220;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: -0.7px;
    }

    p, label, .stMarkdown {
        color: #c4d0df;
    }

    .hero {
        padding: 30px;
        background: linear-gradient(
            135deg,
            rgba(16, 185, 129, 0.12),
            rgba(20, 31, 48, 0.94) 50%,
            rgba(59, 130, 246, 0.10)
        );
        border: 1px solid #2a3b50;
        border-radius: 22px;
        margin-bottom: 25px;
    }

    .eyebrow {
        color: var(--green);
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: clamp(30px, 4vw, 48px);
        font-weight: 800;
        line-height: 1.15;
        color: #f8fafc;
        margin-top: 12px;
    }

    .hero-desc {
        color: #a9b9cc;
        font-size: 15px;
        line-height: 1.8;
        max-width: 760px;
        margin-top: 12px;
    }

    .panel {
        background: linear-gradient(
            145deg,
            #121d2d,
            #0e1725
        );
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 23px;
        margin-bottom: 18px;
    }

    .feature-card {
        background: #111c2b;
        border: 1px solid #26364b;
        border-radius: 15px;
        padding: 18px;
        min-height: 125px;
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }

    .feature-title {
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 6px;
    }

    .feature-desc {
        color: #91a2b8;
        font-size: 12px;
        line-height: 1.7;
    }

    .stTextArea textarea,
    .stTextInput input {
        background: #0b1321 !important;
        color: #f1f5f9 !important;
        border: 1px solid #34445b !important;
        border-radius: 12px !important;
    }

    [data-baseweb="select"] > div {
        background: #0b1321;
        border-color: #34445b;
        border-radius: 10px;
        color: #f1f5f9;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(
            100deg,
            #059669,
            #10b981
        );
        color: white !important;
        border: 1px solid #34d399;
        border-radius: 11px;
        font-weight: 700;
        min-height: 44px;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(
            100deg,
            #047857,
            #059669
        );
        border-color: #6ee7b7;
        transform: translateY(-1px);
    }

    [data-testid="stMetric"] {
        background: #111c2b;
        border: 1px solid #29394f;
        border-radius: 15px;
        padding: 19px;
    }

    [data-testid="stMetricLabel"] {
        color: #91a2b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #34d399 !important;
        font-weight: 800;
    }

    [data-testid="stExpander"] {
        background: #101a29;
        border: 1px solid #29394f;
        border-radius: 12px;
    }

    hr {
        border-color: #263449;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .footer {
        text-align: center;
        color: #62738a;
        font-size: 12px;
        padding: 25px 0 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Build Application"

if "requirement" not in st.session_state:
    st.session_state.requirement = ""

if "build_result" not in st.session_state:
    st.session_state.build_result = None

if "build_log" not in st.session_state:
    st.session_state.build_log = ""

if "building" not in st.session_state:
    st.session_state.building = False


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def show_header():
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">⚡ Autonomous Development Platform</div>
            <div class="hero-title">
                Turn your ideas into<br>
                <span style="color:#34d399">working software.</span>
            </div>
            <div class="hero-desc">
                Describe your application in plain English.
                Let AI agents plan the solution, design its architecture,
                generate source files, validate the code, and attempt
                automatic repairs.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_project_files(project_path):
    root = Path(project_path)

    if not root.is_dir():
        return []

    excluded = {
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".git",
        ".pytest_cache",
    }

    files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in excluded for part in path.parts):
            continue

        if path.suffix in {".pyc", ".pyo"}:
            continue

        files.append(path.relative_to(root).as_posix())

        if len(files) >= 250:
            break

    return sorted(files)


def start_build(requirement):
    st.session_state.requirement = requirement
    st.session_state.build_result = None
    st.session_state.build_log = ""
    st.session_state.page = "Build Results"
    st.session_state.building = True


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="padding:8px 0 25px">
            <div style="font-size:30px;font-weight:800;color:#34d399">
                ⚡ NEXUS
            </div>
            <div style="font-size:11px;letter-spacing:2px;color:#91a2b8">
                AI SOFTWARE BUILDER
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### WORKSPACE")

    selected_page = st.radio(
        "Navigation",
        ["Build Application", "Build Results"],
        index=(
            0 if st.session_state.page == "Build Application"
            else 1
        ),
        label_visibility="collapsed",
    )

    st.session_state.page = selected_page

    st.divider()

    st.markdown("### AGENT PIPELINE")

    for icon, name, description in [
        ("🧠", "Planner", "Requirement analysis"),
        ("🏗️", "Architect", "System design"),
        ("💻", "Coder", "Source generation"),
        ("🧪", "Validator", "Tests and repair"),
    ]:
        st.markdown(
            f"""
            <div style="
                display:flex;
                gap:10px;
                align-items:center;
                padding:10px 0;
                border-bottom:1px solid #1d2a3d;
            ">
                <div style="font-size:22px">{icon}</div>
                <div>
                    <div style="font-weight:600;color:#e2e8f0">
                        {name}
                    </div>
                    <div style="font-size:11px;color:#91a2b8">
                        {description}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.caption("POWERED BY YOUR EXISTING AGENTS")
    st.caption("Python · Groq · Streamlit")


# --------------------------------------------------
# PAGE 1: BUILD APPLICATION
# --------------------------------------------------

if st.session_state.page == "Build Application":
    show_header()

    st.markdown("## Create a new application")
    st.markdown(
        "Tell the builder what you want to create. "
        "Be as specific as possible."
    )

    with st.form("application_builder_form"):
        st.markdown("#### 01 / Describe your idea")

        requirement = st.text_area(
            "Software requirements",
            value=st.session_state.requirement,
            placeholder=(
                "Example: Build a student management system with "
                "student registration, attendance tracking, marks, "
                "search, reports, and a database..."
            ),
            height=190,
            help=(
                "Describe the functionality, users, data storage, "
                "screens, and any special requirements."
            ),
        )

        st.markdown("#### 02 / Choose a technology preference")

        stack = st.selectbox(
            "Preferred technology stack",
            [
                "Auto-detect from requirements",
                "Python + Streamlit",
                "Python + FastAPI",
                "React + Vite",
                "Python CLI",
            ],
        )

        st.markdown("#### 03 / Build your application")

        submitted = st.form_submit_button(
            "⚡  BUILD APPLICATION",
            use_container_width=True,
        )

    if submitted:
        if not requirement.strip():
            st.error("Please enter your software requirements first.")
        else:
            final_requirement = requirement.strip()

            stack_prompts = {
                "Python + Streamlit":
                    "Preferred technology stack: Python with Streamlit.",
                "Python + FastAPI":
                    "Preferred technology stack: Python with FastAPI.",
                "React + Vite":
                    "Preferred technology stack: React with Vite.",
                "Python CLI":
                    "Preferred technology stack: Python command-line application.",
            }

            if stack in stack_prompts:
                final_requirement += (
                    "\n\n" + stack_prompts[stack]
                )

            start_build(final_requirement)
            st.rerun()

    st.markdown("---")
    st.markdown("### Need inspiration?")

    examples = [
        (
            "📊 Expense Tracker",
            "Build a Python Streamlit expense tracker with income "
            "and expenses, category filters, monthly summaries, "
            "charts, and CSV export.",
        ),
        (
            "🎓 Student Management",
            "Build a student management application with student "
            "registration, attendance, marks, search, and reports.",
        ),
        (
            "🤖 AI Chatbot",
            "Build an AI chatbot with conversation history, "
            "a clean chat interface, and configurable LLM integration.",
        ),
    ]

    cols = st.columns(3)

    for col, (title, example) in zip(cols, examples):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">
                        Click the button below to use this example.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Use example",
                key=f"example_{title}",
                use_container_width=True,
            ):
                st.session_state.requirement = example
                st.rerun()


# --------------------------------------------------
# PAGE 2: BUILD RESULTS
# --------------------------------------------------

elif st.session_state.page == "Build Results":
    show_header()

    st.markdown("## Application build results")

    # Run the builder only after a build request.
    if st.session_state.building:
        requirement = st.session_state.requirement

        st.markdown(
            """
            <div class="panel">
                <div style="color:#34d399;font-weight:700">
                    BUILD IN PROGRESS
                </div>
                <div style="color:#c4d0df;margin-top:8px">
                    Your AI agents are generating and validating
                    the application. Please wait for the process
                    to finish.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        log_buffer = io.StringIO()
        result = None
        build_exception = None

        with st.status(
            "Running the AI software development pipeline...",
            expanded=True,
        ) as status:
            try:
                with contextlib.redirect_stdout(log_buffer):
                    result = run_builder(requirement)

                if result.get("status") == "PASS":
                    status.update(
                        label="Build completed successfully",
                        state="complete",
                        expanded=False,
                    )
                else:
                    status.update(
                        label="Build finished with errors",
                        state="error",
                        expanded=True,
                    )

            except Exception as exc:
                build_exception = (
                    f"{type(exc).__name__}: {exc}"
                )
                status.update(
                    label="Builder encountered an error",
                    state="error",
                    expanded=True,
                )

        st.session_state.build_result = result
        st.session_state.build_log = log_buffer.getvalue()

        if build_exception:
            st.session_state.build_log += (
                "\n\nBUILDER EXCEPTION:\n" + build_exception
            )

        st.session_state.building = False
        st.rerun()

    result = st.session_state.build_result

    if result is None:
        st.info(
            "No build results yet. Open **Build Application**, "
            "enter your requirements, and start a build."
        )

        if st.button("← Back to Build Application"):
            st.session_state.page = "Build Application"
            st.rerun()

    else:
        success = result.get("status") == "PASS"
        project_path = result.get("project_path", "")
        files = get_project_files(project_path) if project_path else []

        if success:
            st.success("Application generated and validation passed.")
        else:
            st.error(
                "The build did not pass all available validations. "
                "Review the error details and build log."
            )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Build Status",
                "SUCCESS" if success else "FAILED",
            )

        with c2:
            st.metric(
                "Validation",
                result.get("test_result", "Not available"),
            )

        with c3:
            st.metric(
                "Repair Attempts",
                result.get("retry_count", 0),
            )

        st.markdown("### Your requirements")

        st.markdown(
            f"""
            <div class="panel">
                {st.session_state.requirement}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Generated project")

        st.code(project_path or "No project path available")

        if project_path and Path(project_path).is_dir():
            st.markdown(f"**Files generated:** {len(files)}")

            with st.expander("📁 Explore generated files", expanded=True):
                for file in files:
                    st.markdown(f"- `{file}`")

            st.markdown("### Run your application")

            st.markdown(
                "Use the command appropriate for your generated project."
            )

            st.code(
                f'cd "{project_path}"',
                language="powershell",
            )

            root = Path(project_path)

            if (root / "app.py").is_file():
                st.code(
                    "python -m streamlit run app.py",
                    language="powershell",
                )
            elif (root / "package.json").is_file():
                st.code(
                    "npm install\nnpm run dev",
                    language="powershell",
                )
            elif (root / "main.py").is_file():
                st.code(
                    "python main.py",
                    language="powershell",
                )
            elif (root / "index.html").is_file():
                st.info(
                    "This project contains HTML. Open index.html "
                    "in a browser or use a local development server."
                )

            st.markdown("### Validation details")

            st.write(result.get("error") or "No validation errors reported.")

        else:
            st.warning("The generated project directory was not found.")

        with st.expander("🧾 View agent execution log"):
            st.text(
                st.session_state.build_log
                or "No execution log was captured."
            )

        left, right = st.columns(2)

        with left:
            if st.button(
                "＋ Build another application",
                use_container_width=True,
            ):
                st.session_state.page = "Build Application"
                st.session_state.requirement = ""
                st.session_state.build_result = None
                st.session_state.build_log = ""
                st.rerun()

        with right:
            if st.button(
                "↻ Rebuild this application",
                use_container_width=True,
            ):
                start_build(st.session_state.requirement)
                st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        NEXUS AI SOFTWARE BUILDER · BUILT WITH PYTHON & STREAMLIT
    </div>
    """,
    unsafe_allow_html=True,
)
import os
import re
import shutil
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def parse_generated_code(generated_code):
    """Extract real files from the Coder Agent's FILE sections."""
    files = {}

    if not isinstance(generated_code, str) or not generated_code.strip():
        return files

    lines = generated_code.splitlines()
    markers = []

    for index, line in enumerate(lines):
        cleaned = line.strip().strip("*").strip()

        if cleaned.upper().startswith("FILE:"):
            filename = cleaned.split(":", 1)[1].strip()
            if filename:
                markers.append((index, filename))

    for marker_index, (line_index, filename) in enumerate(markers):
        end_index = (
            markers[marker_index + 1][0]
            if marker_index + 1 < len(markers)
            else len(lines)
        )

        section = "\n".join(lines[line_index + 1:end_index])
        language = ""
        section_lines = section.splitlines()

        for i, line in enumerate(section_lines):
            cleaned = line.strip().strip("*").strip()
            if cleaned.upper().startswith("LANGUAGE:"):
                language = cleaned.split(":", 1)[1].strip()
                section_lines.pop(i)
                break

        code = "\n".join(section_lines).strip()
        code = re.sub(r"\A\s*```[^\n]*\n", "", code, count=1)
        code = re.sub(r"\n?```\s*\Z", "", code, count=1).strip()

        files[filename] = {
            "language": language,
            "code": code,
        }

    return files


def _safe_relative_path(filename):
    """Reject absolute paths, parent traversal, and Windows drive paths."""
    if not filename or "\x00" in filename:
        raise ValueError("Empty or invalid filename.")

    normalized = filename.replace("\\", "/").strip()
    posix_path = PurePosixPath(normalized)
    windows_path = PureWindowsPath(filename)

    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or any(part == ".." for part in posix_path.parts)
    ):
        raise ValueError(f"Unsafe file path: {filename}")

    clean_path = Path(*posix_path.parts)

    if not clean_path.parts or str(clean_path) in ("", "."):
        raise ValueError(f"Invalid file path: {filename}")

    return clean_path


def looks_like_file(filename, code):
    """Reject directory-only markers and empty file entries."""
    basename = Path(filename).name

    if not basename or basename in (".", ".."):
        return False

    if not code.strip():
        return False

    return True


def create_project_files(
    generated_code,
    project_name="generated_app",
    clean_existing=True,
):
    """Safely create a project from generated FILE sections."""
    if (
        not project_name
        or project_name in (".", "..")
        or "/" in project_name
        or "\\" in project_name
        or "\x00" in project_name
    ):
        raise ValueError("project_name must be a simple directory name.")

    base_dir = Path(__file__).resolve().parent.parent / "generated_projects"
    base_dir.mkdir(parents=True, exist_ok=True)

    project_path = base_dir / project_name
    files = parse_generated_code(generated_code)

    if not files:
        raise ValueError("No files could be extracted from Coder Agent output.")

    validated_files = {}

    for filename, file_data in files.items():
        try:
            relative_path = _safe_relative_path(filename)
        except ValueError:
            print(f"Skipping unsafe path: {filename}")
            continue

        code = file_data.get("code", "")

        if not looks_like_file(str(relative_path), code):
            print(f"Skipping empty or directory-only entry: {filename}")
            continue

        validated_files[relative_path] = code

    if not validated_files:
        raise ValueError("No usable source files were generated.")

    recognized_files = {
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "main.py",
        "app.py",
        "index.html",
        "pom.xml",
        "go.mod",
        "cargo.toml",
    }

    has_project_file = any(
        Path(str(path)).name.lower() in recognized_files
        for path in validated_files
    )

    if not has_project_file:
        raise ValueError(
            "Generated files do not contain a recognizable project entry or "
            "manifest (for example package.json, app.py, main.py, or index.html)."
        )

    staging_path = Path(
        tempfile.mkdtemp(prefix=f".{project_name}_staging_", dir=str(base_dir))
    )

    try:
        for relative_path, code in validated_files.items():
            destination = staging_path / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(code, encoding="utf-8")

        if project_path.exists() and not clean_existing:
            raise FileExistsError(f"Project already exists: {project_path}")

        if project_path.exists() and clean_existing:
            shutil.rmtree(project_path)

        try:
            staging_path.rename(project_path)
        except OSError:
            if project_path.exists():
                shutil.rmtree(project_path)
            staging_path.rename(project_path)

        created_files = [
            str(project_path / relative_path)
            for relative_path in validated_files
        ]

        print(f"\nProject created safely: {project_path}")
        print(f"Files created: {len(created_files)}")

        return {
            "project_path": str(project_path),
            "files": created_files,
        }

    finally:
        if staging_path.exists():
            shutil.rmtree(staging_path, ignore_errors=True)


from tools.file_manager import (
    parse_generated_code,
    create_project_files,
)


generated_code = """**FILE: index.html**
**LANGUAGE: HTML**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Calculator</title>
</head>
<body>
    <h1>Calculator</h1>
</body>
</html>

**FILE: style.css**
**LANGUAGE: CSS**

body {
    font-family: Arial, sans-serif;
}

button {
    padding: 10px;
}

**FILE: script.js**
**LANGUAGE: JavaScript**

console.log("Calculator started");
"""

print()
print("==========================================")
print(" FILE PARSER TEST")
print("==========================================")
print()

files = parse_generated_code(generated_code)

print("Files detected:")
for filename in files:
    print(f" ✓ {filename}")

print()

if len(files) != 3:
    print("==========================================")
    print("              TEST FAILED")
    print("==========================================")
    print()
    print("Expected: 3 files")
    print("Detected:", len(files))
    raise SystemExit(1)

result = create_project_files(
    generated_code,
    project_name="calculator_test",
)

print("==========================================")
print(" PROJECT CREATED")
print("==========================================")
print()

print("Project Path:")
print(result["project_path"])
print()

print("Created Files:")
for file_path in result["files"]:
    print(f" ✓ {file_path}")

print()
print("==========================================")
print(" TEST PASSED")
print("==========================================")
print()

print("Total files created:", len(result["files"]))

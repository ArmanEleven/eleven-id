from pathlib import Path
import ast
import sys

ROOT = Path(__file__).parent

REQUIRED_FILES = [
    "main.py",
    "checker.py",
    "generator.py",
    "api_setup.py",
    "README.md",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "LICENSE",
    "install.bat",
    "install.ps1",
    "run.bat",
]

FORBIDDEN_FILES = [
    ".env",
]

FORBIDDEN_DIRS = [
    ".venv",
    "sessions",
    "results",
    "__pycache__",
    ".git",
]

PYTHON_FILES = [
    "main.py",
    "checker.py",
    "generator.py",
    "api_setup.py",
]


def ok(msg):
    print(f"[OK]   {msg}")


def warn(msg):
    print(f"[WARN] {msg}")


def fail(msg):
    print(f"[FAIL] {msg}")


print("=" * 60)
print(" Eleven ID - Project Health Check")
print("=" * 60)
print()

errors = 0
warnings = 0

# Required files
print("Checking required files...")

for filename in REQUIRED_FILES:
    path = ROOT / filename

    if path.is_file():
        ok(filename)
    else:
        fail(f"Missing: {filename}")
        errors += 1

print()

# Forbidden files
print("Checking sensitive files...")

for filename in FORBIDDEN_FILES:
    path = ROOT / filename

    if path.exists():
        fail(f"Sensitive file exists: {filename}")
        errors += 1
    else:
        ok(f"{filename} is not present")

print()

# Forbidden directories
print("Checking generated/private folders...")

for dirname in FORBIDDEN_DIRS:
    path = ROOT / dirname

    if path.exists():
        if dirname == ".git":
            warn(f"{dirname} exists - Git repository detected")
            warnings += 1
        else:
            warn(f"{dirname} exists")
            warnings += 1
    else:
        ok(f"{dirname} is clean")

print()

# Python syntax
print("Checking Python syntax...")

for filename in PYTHON_FILES:
    path = ROOT / filename

    if not path.exists():
        continue

    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=filename)
        ok(f"{filename} syntax is valid")
    except SyntaxError as e:
        fail(f"{filename}: line {e.lineno} - {e.msg}")
        errors += 1
    except Exception as e:
        fail(f"{filename}: {e}")
        errors += 1

print()

# .env.example
print("Checking .env.example...")

env_example = ROOT / ".env.example"

if env_example.exists():
    content = env_example.read_text(encoding="utf-8", errors="ignore")

    if "API_ID" in content:
        ok("API_ID exists")
    else:
        warn("API_ID not found in .env.example")
        warnings += 1

    if "API_HASH" in content:
        ok("API_HASH exists")
    else:
        warn("API_HASH not found in .env.example")
        warnings += 1

    if "PHONE" in content:
        ok("PHONE exists")
    else:
        warn("PHONE not found in .env.example")
        warnings += 1

print()

# requirements
print("Checking requirements.txt...")

requirements = ROOT / "requirements.txt"

if requirements.exists():
    content = requirements.read_text(encoding="utf-8", errors="ignore").lower()

    if "telethon" in content:
        ok("Telethon dependency found")
    else:
        warn("Telethon not found in requirements.txt")
        warnings += 1

print()

# .gitignore
print("Checking .gitignore...")

gitignore = ROOT / ".gitignore"

if gitignore.exists():
    content = gitignore.read_text(encoding="utf-8", errors="ignore")

    important_entries = [
        ".env",
        ".venv",
        "sessions",
        "results",
        "__pycache__",
    ]

    for entry in important_entries:
        if entry in content:
            ok(f".gitignore contains: {entry}")
        else:
            warn(f".gitignore may be missing: {entry}")
            warnings += 1

print()

# Final result
print("=" * 60)

if errors == 0 and warnings == 0:
    print("HEALTH CHECK PASSED")
    print("Project looks ready for GitHub.")
    sys.exit(0)

if errors == 0:
    print("HEALTH CHECK PASSED WITH WARNINGS")
    print(f"Warnings: {warnings}")
    print("Review the warnings before publishing.")
    sys.exit(0)

print("HEALTH CHECK FAILED")
print(f"Errors: {errors}")
print(f"Warnings: {warnings}")
print("Fix the errors before publishing.")
sys.exit(1)
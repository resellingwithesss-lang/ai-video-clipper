import os
import subprocess
import difflib
import time
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROTECTED_FILES = ["login", "auth", "security"]
MAX_CHANGE_PERCENT = 1.2


def clean_code_output(text):
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)

    return text


def get_repo_files():
    files = subprocess.check_output(
        "git ls-files", shell=True
    ).decode().splitlines()

    return [
        f for f in files
        if f.startswith("backend/") and f.endswith(".py")
        and not any(p in f.lower() for p in PROTECTED_FILES)
    ]


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def is_safe_change(original, modified):
    diff = list(difflib.unified_diff(
        original.splitlines(),
        modified.splitlines()
    ))

    change_ratio = len(diff) / max(len(original.splitlines()), 1)
    print(f"Change ratio: {change_ratio:.2f}")

    return change_ratio <= MAX_CHANGE_PERCENT


def improve_code(code):
    prompt = f"""
You are a senior FastAPI backend engineer improving a SaaS backend.

Rules:
- Do NOT delete endpoints.
- Do NOT modify authentication.
- Do NOT change deployment logic.
- Improve structure, validation, logging, safety.
- Keep changes incremental.
- Return full updated file.
- Return code only. No markdown.

CODE:
{code}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return clean_code_output(response.output_text)


def main():
    files = get_repo_files()

    if not files:
        print("No backend files found.")
        return

    branch_name = f"ai-improvement-{int(time.time())}"
    subprocess.run(["git", "checkout", "-b", branch_name])

    changes_made = False

    for file in files:
        original_code = read_file(file)
        improved_code = improve_code(original_code)

        if not improved_code or improved_code == original_code:
            continue

        if not is_safe_change(original_code, improved_code):
            continue

        write_file(file, improved_code)
        subprocess.run(["git", "add", file])
        changes_made = True

    if changes_made:
        subprocess.run(["git", "commit", "-m", "🤖 AI backend improvements"])
        subprocess.run(["git", "push", "origin", branch_name])
    else:
        print("No safe changes detected.")


if __name__ == "__main__":
    main()

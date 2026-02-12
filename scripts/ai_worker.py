import os
import subprocess
import difflib
import time
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROTECTED_FILES = ["login", "auth", "security"]
MAX_CHANGE_PERCENT = 1.5  # Allows structural improvements safely


# ---------------- FILE DISCOVERY ----------------
def get_repo_files():
    files = subprocess.check_output(
        "git ls-files", shell=True
    ).decode().splitlines()

    valid_files = []

    for f in files:
        if f.startswith("backend/") and f.endswith(".py"):
            if not any(p in f.lower() for p in PROTECTED_FILES):
                valid_files.append(f)

    return valid_files


# ---------------- FILE IO ----------------
def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------- SAFETY CHECK ----------------
def is_safe_change(original, modified):
    diff = list(difflib.unified_diff(
        original.splitlines(),
        modified.splitlines()
    ))

    change_ratio = len(diff) / max(len(original.splitlines()), 1)

    print(f"Change ratio: {change_ratio:.2f}")

    if change_ratio > MAX_CHANGE_PERCENT:
        print("❌ Change too large. Skipping file.")
        return False

    return True


# ---------------- AI EDIT ----------------
def improve_code(code):
    prompt = f"""
You are a senior FastAPI backend engineer improving a SaaS backend.

STRICT RULES:
- Do NOT delete endpoints.
- Do NOT remove routes.
- Do NOT modify authentication.
- Do NOT rewrite entire architecture.
- Improve structure, validation, logging, safety, and performance.
- Keep changes incremental.
- Return FULL updated file.
- Return code only. No explanations.

CODE:
{code}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text.strip()


# ---------------- MAIN ----------------
def main():
    files = get_repo_files()

    if not files:
        print("No backend files found.")
        return

    # Create unique branch per run
    branch_name = f"ai-improvement-{int(time.time())}"
    subprocess.run(["git", "checkout", "-b", branch_name])

    for file in files:
        print(f"\n🔧 Improving {file}")

        original_code = read_file(file)
        improved_code = improve_code(original_code)

        if not improved_code:
            print("No changes returned.")
            continue

        if improved_code == original_code:
            print("No improvement detected.")
            continue

        if not is_safe_change(original_code, improved_code):
            continue

        write_file(file, improved_code)
        subprocess.run(["git", "add", file])

    # Commit if changes exist
    subprocess.run(["git", "commit", "-m", "🤖 AI backend improvements"], check=False)

    # Push new branch
    subprocess.run(["git", "push", "origin", branch_name])


if __name__ == "__main__":
    main()

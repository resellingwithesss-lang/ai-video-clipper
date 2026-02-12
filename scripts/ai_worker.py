import os
import subprocess
import difflib
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROTECTED_FILES = ["login", "auth", "security"]
MAX_CHANGE_PERCENT = 0.35  # prevents large rewrites


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
You are a senior FastAPI backend engineer improving a SaaS project.

STRICT RULES:
- Do NOT delete endpoints.
- Do NOT remove routes.
- Do NOT change authentication logic.
- Do NOT modify deployment config.
- Improve performance, safety, and structure only.
- Keep edits minimal.
- Return FULL updated file content.
- Do NOT include explanations.
- Return code only.

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

    subprocess.run(["git", "checkout", "-B", "ai-improvements"])

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

    subprocess.run(["git", "commit", "-m", "🤖 AI backend improvements"], check=False)
    subprocess.run(["git", "push", "--force", "origin", "ai-improvements"])


if __name__ == "__main__":
    main()

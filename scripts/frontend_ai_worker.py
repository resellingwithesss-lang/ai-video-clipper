import os
import subprocess
import difflib
import time
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

MAX_CHANGE_PERCENT = 1.2
FRONTEND_PATH = "app/src"


def clean_code_output(text):
    if text.startswith("```"):
        text = text.strip()
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)
    return text


def get_frontend_files():
    files = subprocess.check_output(
        "git ls-files", shell=True
    ).decode().splitlines()

    return [
        f for f in files
        if f.startswith(FRONTEND_PATH)
        and (f.endswith(".jsx") or f.endswith(".js") or f.endswith(".tsx"))
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

    if change_ratio > MAX_CHANGE_PERCENT:
        print("❌ Change too large. Skipping file.")
        return False

    return True


def improve_frontend(code):
    prompt = f"""
You are a senior React + UX engineer improving a SaaS frontend.

STRICT RULES:
- Do NOT break functionality.
- Do NOT remove API calls.
- Improve UI clarity.
- Improve loading states.
- Improve spacing and structure.
- Add better UX patterns.
- Keep changes incremental.
- Return FULL updated file.
- Return code only. No markdown.

CODE:
{code}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return clean_code_output(response.output_text.strip())


def main():
    files = get_frontend_files()

    if not files:
        print("No frontend files found.")
        return

    branch_name = f"ai-frontend-improvement-{int(time.time())}"
    subprocess.run(["git", "checkout", "-b", branch_name])

    for file in files:
        print(f"\n🎨 Improving {file}")

        original_code = read_file(file)
        improved_code = improve_frontend(original_code)

        if not improved_code:
            continue

        if improved_code == original_code:
            continue

        if not is_safe_change(original_code, improved_code):
            continue

        write_file(file, improved_code)
        subprocess.run(["git", "add", file])

    subprocess.run(["git", "commit", "-m", "🎨 AI frontend UX improvements"], check=False)
    subprocess.run(["git", "push", "origin", branch_name])


if __name__ == "__main__":
    main()

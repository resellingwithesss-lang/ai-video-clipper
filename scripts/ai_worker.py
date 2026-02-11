import os
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 🔒 Only allow backend Python files (protect workflow + scripts)
def get_repo_files():
    files = subprocess.check_output(
        "git ls-files", shell=True
    ).decode().splitlines()

    return [
        f for f in files
        if f.startswith("backend/") and f.endswith(".py")
    ]

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def improve_code(code):
    prompt = f"""
You are a senior backend engineer improving a production SaaS API.

Rules:
- Fix bugs
- Improve structure
- Improve performance
- Add small improvements
- DO NOT remove working endpoints
- DO NOT modify authentication logic
- DO NOT modify deployment configuration
- Return ONLY valid Python code

CODE:
{code}
"""

    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


files = get_repo_files()

changes_made = False

for file in files:
    original_code = read_file(file)
    improved_code = improve_code(original_code)

    if improved_code.strip() != original_code.strip():
        write_file(file, improved_code)
        changes_made = True

if changes_made:
    subprocess.run("git config user.name 'AI Dev'", shell=True)
    subprocess.run("git config user.email 'ai@repo.com'", shell=True)
    subprocess.run("git checkout -b ai-improvements || true", shell=True)
    subprocess.run("git add backend/", shell=True)
    subprocess.run("git commit -m 'AI backend improvements'", shell=True)
    subprocess.run("git push origin ai-improvements", shell=True)

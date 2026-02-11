import os
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_repo_files():
    files = subprocess.check_output(
        "git ls-files", shell=True
    ).decode().splitlines()
    return [f for f in files if f.endswith((".py",".js",".jsx",".ts",".tsx",".json",".css"))]

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def improve_code(code):
    prompt = f"""
You are a senior software engineer improving a SaaS product.

Improve this code:
- Fix bugs
- Improve UX
- Improve performance
- Add small useful features
- Do NOT break existing functionality
- Return ONLY the new code

CODE:
{code}
"""
  res = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role":"user","content":prompt}]
)


    return res.choices[0].message.content

files = get_repo_files()

for file in files:
    code = read_file(file)
    improved = improve_code(code)
    write_file(file, improved)

subprocess.run("git config user.name 'AI Dev'", shell=True)
subprocess.run("git config user.email 'ai@repo.com'", shell=True)
subprocess.run("git checkout -b ai-improvements || true", shell=True)
subprocess.run("git add .", shell=True)
subprocess.run("git commit -m 'AI automatic improvements'", shell=True)
subprocess.run("git push origin ai-improvements", shell=True)

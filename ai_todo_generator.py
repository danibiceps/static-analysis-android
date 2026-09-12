import os
import glob
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_apk_artifacts():
    manifest_path = "decompiled_apk/resources/AndroidManifest.xml"
    manifest_content = ""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", errors="ignore") as f:
            manifest_content = f.read()

    sources = glob.glob("decompiled_apk/sources/**/*.java", recursive=True)[:10]
    source_code = ""
    for file in sources:
        with open(file, "r", errors="ignore") as f:
            source_code += f"\n--- File: {file} ---\n" + f.read()[:2500]

    return manifest_content, source_code

def generate_todo():
    manifest, sources = get_apk_artifacts()

    prompt = f"""
    You are an expert Mobile Application Security Engineer conducting a Static Analysis (SAST) review.
    Analyze the provided AndroidManifest.xml and source code snippets.

    Convert all identified security issues, hardcoded secrets, misconfigurations, and OWASP Mobile risks into an actionable developer TO-DO checklist.

    Output Format Requirements:
    1. Organize items by Severity: [CRITICAL], [HIGH], [MEDIUM], [LOW].
    2. Format each item as a Markdown checkbox: `- [ ] [SEVERITY] Task Title`
    3. Include the exact File Path / Location for each task.
    4. Provide a 1-2 sentence developer instruction on how to fix it.
    5. Include a brief code snippet fix where applicable.

    [AndroidManifest.xml]
    {manifest}

    [Source Snippets]
    {sources}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    todo_output = response.text

    with open("SECURITY_TODO.md", "w") as f:
        f.write("# APK Security Remediation To-Do List\n\n")
        f.write(todo_output)

    print("=== SECURITY TO-DO LIST GENERATED ===")
    print(todo_output)

if __name__ == "__main__":
    generate_todo()

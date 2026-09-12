import os
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)

    # Read AndroidManifest.xml if available for security context
    manifest_path = "decompiled_apk/AndroidManifest.xml"
    manifest_content = ""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
            manifest_content = f.read()[:10000] # Limit size

    prompt = f"""
    You are an expert Android Application Security Analyst and Mobile Pentester.
    Analyze the following AndroidManifest.xml snippet and provide a clear, prioritized SECURITY_TODO.md file 
    outlining security vulnerabilities, misconfigurations, or best practices that need remediation.

    AndroidManifest.xml:
    ```xml
    {manifest_content}
    ```

    Format the output strictly as a Markdown checklist (`- [ ]`) grouped by severity (High, Medium, Low).
    """

    print("Sending decompiled metadata to Gemini for security analysis...")
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )

    # Write output to SECURITY_TODO.md
    with open("SECURITY_TODO.md", "w", encoding="utf-8") as f:
        f.write("# Security Remediation To-Do List\n\n")
        f.write(response.text)

    print("SECURITY_TODO.md successfully generated.")

if __name__ == "__main__":
    main()
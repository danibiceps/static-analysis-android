import os
from google import genai

def gather_apk_context():
    """Gathers critical configuration and file structure from the decompiled APK."""
    context = []
    
    # 1. Read AndroidManifest.xml
    manifest_path = "decompiled_apk/AndroidManifest.xml"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
            context.append("=== ANDROID MANIFEST ===\n" + f.read()[:15000])

    # 2. Check Network Security Config if present
    net_config = "decompiled_apk/res/xml/network_security_config.xml"
    if os.path.exists(net_config):
        with open(net_config, "r", encoding="utf-8", errors="ignore") as f:
            context.append("\n=== NETWORK SECURITY CONFIG ===\n" + f.read()[:5000])

    # 3. List source directory structure to identify packages/classes
    sources_dir = "decompiled_apk/sources"
    if os.path.exists(sources_dir):
        file_list = []
        for root, dirs, files in os.walk(sources_dir):
            for file in files:
                if file.endswith(".java") or file.endswith(".smali"):
                    file_list.append(os.path.relpath(os.path.join(root, file), sources_dir))
            if len(file_list) > 200: # Cap list size
                break
        context.append("\n=== KEY SOURCE FILES STRUCTURE ===\n" + "\n".join(file_list[:150]))

    return "\n".join(context)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)

    print("Collecting decompiled app structure and configurations...")
    app_data = gather_apk_context()

    prompt = f"""
    You are an elite Lead Android Security Architect and Offensive Mobile Pentester.
    Perform an exhaustive A-Z static security analysis of the provided Android application context below.

    App Context:
    ```text
    {app_data}
    ```

    Please generate a comprehensive `SECURITY_TODO.md` file structured into two major sections:

    ### Section 1: Comprehensive A-Z Static Analysis & CVSS 3.1 Report
    - Identify potential architectural flaws, insecure permissions, insecure data storage, weak cryptography, or misconfigurations.
    - For each vulnerability found, provide:
      - **Vulnerability Name**
      - **Severity & CVSS 3.1 Score** (e.g., Critical / 9.8 or High / 8.1)
      - **Affected Component/File**
      - **Remediation guidance**

    ### Section 2: Dynamic Analysis To-Do Checklist for Pentesters
    - Provide a concrete, step-by-step checklist for a human pentester to perform manual dynamic analysis (e.g., traffic interception via Burp Suite, root/emulator detection bypass, hooking with Frida/Xposed, intent fuzzing, local database inspection, and authentication state manipulation).
    - Format these as actionable Markdown checklists (`- [ ]`).
    """

    print("Sending context to Gemini for advanced security analysis...")
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )

    # Write output to SECURITY_TODO.md
    with open("SECURITY_TODO.md", "w", encoding="utf-8") as f:
        f.write("# Comprehensive Android Security Assessment & Pentesting Report\n\n")
        f.write(response.text)

    print("SECURITY_TODO.md successfully generated with CVSS and Dynamic Testing Checklist.")

if __name__ == "__main__":
    main()
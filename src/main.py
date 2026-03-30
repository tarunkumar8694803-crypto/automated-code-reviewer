import sys
import os

# 1. Force the 'src' directory into the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Hard-check if the file actually exists where we think it is
scanner_path = os.path.join(current_dir, "utils", "file_scanner.py")
if not os.path.exists(scanner_path):
    print(f"🚨 CRITICAL ERROR: I looked for the scanner at {scanner_path} but it's not there!")
    print("Please check your folder structure in VS Code.")
    sys.exit(1)

# 3. Standard Imports
try:
    from engines.ai_reviewer import AIReviewer
    from engines.static_analyzer import StaticAnalyzer
    from utils.file_scanner import get_all_python_files
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def main():
    print("🛡️  PRO AUTOMATED CODE REVIEW SYSTEM 🛡️")
    ai_reviewer = AIReviewer()
    security_scanner = StaticAnalyzer()

    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    files_to_review = get_all_python_files(project_root)
    
    # --- Added Stats Tracking ---
    stats = {"total": 0, "clean": 0, "issues": 0}
    issue_files = []

    print(f"🔎 Found {len(files_to_review)} files. Starting analysis...\n")

    for file_path in files_to_review:
        clean_path = os.path.normpath(file_path)
        if any(x in clean_path for x in ["venv", ".git", "__pycache__"]):
            continue
            
        stats["total"] += 1
        print(f"🔄 Processing: {clean_path}")

        sec_report = security_scanner.run_security_scan(clean_path)
        
        # Track if issues were found
        if "Security Issues Found" in sec_report:
            stats["issues"] += 1
            issue_files.append(clean_path)
        else:
            stats["clean"] += 1

        try:
            with open(clean_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            ai_report = ai_reviewer.review_code(code_content)
            
            print("\n" + "="*50)
            print(f"📢 REPORT FOR: {clean_path}")
            print(f"🛡️  SECURITY:\n{sec_report}")
            print(f"🤖 AI INSIGHTS:\n{ai_report}")
            print("="*50 + "\n")
        except Exception as e:
            print(f"❌ Error reading {clean_path}: {e}")

    # --- Final Summary Table ---
    print("\n" + "📊 SCAN SUMMARY")
    print("="*30)
    print(f"✅ Total Files Scanned: {stats['total']}")
    print(f"🟢 Clean Files:        {stats['clean']}")
    print(f"🔴 Files with Issues:  {stats['issues']}")
    print("="*30)
    
    if issue_files:
        print("\n⚠️  FILES REQUIRING ATTENTION:")
        for f in issue_files:
            print(f" - {f}")
    
    print("\n✅ All files have been reviewed.")
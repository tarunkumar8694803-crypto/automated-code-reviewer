import subprocess
import json

class StaticAnalyzer:
    def __init__(self):
        pass

    def run_security_scan(self, file_path):
        """Runs Bandit security scan on a specific file."""
        print(f"🔍 Running Security Scan on {file_path}...")
        
        # We run bandit via the command line and get results in JSON format
        result = subprocess.run(
            ["bandit", "-f", "json", file_path],
            capture_output=True,
            text=True
        )
        
        # Bandit returns exit code 1 if it finds issues, which is fine
        try:
            data = json.loads(result.stdout)
            issues = data.get("results", [])
            
            if not issues:
                return "✅ No security vulnerabilities found by Static Analysis."
            
            report = "⚠️ Security Issues Found:\n"
            for issue in issues:
                report += f"- [{issue['issue_severity']}] {issue['issue_text']} (Line {issue['line_number']})\n"
            return report
        except Exception as e:
            return f"❌ Error running static analysis: {e}"
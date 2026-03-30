import streamlit as st
import os
import sys
import ast  # Built-in library to check Python syntax

# Ensure Python can find our engines
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from engines.ai_reviewer import AIReviewer
from engines.static_analyzer import StaticAnalyzer

# --- Page Configuration ---
st.set_page_config(page_title="AI Code Reviewer", page_icon="🛡️", layout="wide")

st.title("🛡️ AI Automated Code Reviewer")
st.markdown("Paste your Python code below for a **Syntax, Security, and Logic** analysis.")

# --- Sidebar ---
st.sidebar.header("Settings")
model_choice = st.sidebar.selectbox("AI Model", ["qwen2.5-coder:1.5b"])

# --- Syntax Checker Function ---
def check_syntax(code):
    try:
        ast.parse(code)
        return True, "✅ Syntax is valid."
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e.msg} (Line {e.lineno})"

# --- UI Layout ---
code_input = st.text_area("✍️ Paste your Python code here:", height=250, placeholder="print('Hello World')")

if st.button("🚀 Run Deep Review"):
    if code_input.strip():
        # 1. Check Syntax First
        is_valid, syntax_msg = check_syntax(code_input)
        
        if not is_valid:
            st.error(syntax_msg)
            st.info("💡 Please fix the syntax error above before running the security and AI review.")
        else:
            st.success(syntax_msg)
            
            ai_reviewer = AIReviewer()
            security_scanner = StaticAnalyzer()

            with st.spinner("🕵️‍♂️ Analyzing security and logic..."):
                # 2. Run Security Scan
                temp_file = os.path.join(BASE_DIR, "snippet_to_review.py")
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(code_input)

                sec_report = security_scanner.run_security_scan(temp_file)
                
                # 3. Run AI Review
                ai_report = ai_reviewer.review_code(code_input)
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # --- Display Results ---
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🛡️ Security Scan (Bandit)")
                if "✅ No security" in sec_report:
                    st.success("No vulnerabilities detected.")
                else:
                    st.warning(sec_report)

            with col2:
                st.subheader("🤖 AI Insights (Ollama)")
                st.markdown(ai_report)
    else:
        st.error("Please paste some code first!")
        
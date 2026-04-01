import streamlit as st
import os
import sys
import ast
import io
from fpdf import FPDF
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter

# Ensure Python can find our engines (AI and Static Analyzer)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from engines.ai_reviewer import AIReviewer
from engines.static_analyzer import StaticAnalyzer

# --- PDF Generation Function ---
def generate_pdf(security_text, ai_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt="AI Code Review Report", ln=True, align='C')
    pdf.ln(10)
    
    # Security Section
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="🛡️ Security Scan Results:", ln=True)
    pdf.set_font("Helvetica", size=10)
    # multi_cell handles long text wrapping
    pdf.multi_cell(0, 7, txt=security_text)
    pdf.ln(5)
    
    # AI Section
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, txt="🤖 AI Insights:", ln=True)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 7, txt=ai_text)
    
    # Return as bytes for Streamlit download button
    return pdf.output()

# --- Advanced Syntax & Logic Checker ---
def check_code_quality(code):
    # 1. Basic Syntax Check
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e.msg} (Line {e.lineno})"

    # 2. Logic Check (Undefined variables/names)
    stdout = io.StringIO()
    stderr = io.StringIO()
    reporter = Reporter(stdout, stderr)
    pyflakes_check(code, "snippet.py", reporter)
    
    errors = stdout.getvalue()
    if errors:
        clean_errors = errors.replace("snippet.py:", "Line ")
        return False, f"❌ Logic Error:\n{clean_errors}"

    return True, "✅ Code structure is valid."

# --- Streamlit UI Configuration ---
st.set_page_config(page_title="AI Code Reviewer", page_icon="🛡️", layout="wide")

st.title("🛡️ AI Automated Code Reviewer")
st.markdown("Paste your Python code below for a **Syntax, Security, and AI Logic** analysis.")

# Sidebar Settings
st.sidebar.header("Settings")
model_choice = st.sidebar.selectbox("AI Model", ["qwen2.5-coder:1.5b"])

# Main Input
code_input = st.text_area("✍️ Paste your Python code here:", height=250, placeholder="import os\n...")

if st.button("🚀 Run Deep Review"):
    if code_input.strip():
        # Step 1: Validate Code Quality
        is_valid, validation_msg = check_code_quality(code_input)
        
        if not is_valid:
            st.error(validation_msg)
            st.warning("Please fix the errors above before running the full analysis.")
        else:
            st.success(validation_msg)
            
            ai_reviewer = AIReviewer()
            security_scanner = StaticAnalyzer()

            with st.spinner("🕵️‍♂️ Analyzing security and generating AI insights..."):
                # Step 2: Run Security Scan (requires a temp file)
                temp_file = os.path.join(BASE_DIR, "snippet_to_review.py")
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(code_input)

                sec_report = security_scanner.run_security_scan(temp_file)
                
                # Step 3: Run AI Review
                ai_report = ai_reviewer.review_code(code_input)
                
                # Cleanup temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # --- Display Results ---
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🛡️ Security Scan (Bandit)")
                if "✅ No security" in sec_report:
                    st.success(sec_report)
                else:
                    st.warning(sec_report)

            with col2:
                st.subheader("🤖 AI Insights (Ollama)")
                st.markdown(ai_report)

            # --- Step 4: Generate and Show Download Button ---
            st.divider()
            st.subheader("📥 Export Results")
            try:
                pdf_data = generate_pdf(sec_report, ai_report)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name="code_review_report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Could not generate PDF: {e}")
    else:
        st.error("Please paste some code first!")

st.divider()
st.caption("Developed with Streamlit, Bandit, Pyflakes, and Ollama.")
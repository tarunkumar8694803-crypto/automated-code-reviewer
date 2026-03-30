import ollama

class AIReviewer:
    def __init__(self, model="qwen2.5-coder:1.5b"):
        self.model = model

    def review_code(self, code_content):
        """
        Sends code to Ollama and returns a formatted review.
        """
        prompt = f"""
        You are a Senior Software Engineer. Review the following code for:
        1. Potential bugs or logical errors.
        2. Security vulnerabilities.
        3. Readability and best practices.
        
        Provide your feedback in a concise bullet-point list.
        If the code is perfect, just say "LGTM" (Looks Good To Me).

        CODE TO REVIEW:
        ```python
        {code_content}
        ```
        """
        
        try:
            print(f"🤖 AI Reviewer is thinking (using {self.model})...")
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            return f"❌ Error connecting to Ollama: {str(e)}"

# Quick test if run directly
if __name__ == "__main__":
    reviewer = AIReviewer()
    sample_code = "def add(a, b): return a + b"
    print(reviewer.review_code(sample_code))
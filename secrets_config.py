import streamlit as st

def create_secrets_page():
    st.title("HuggingFace Spaces Secrets Configuration")
    
    st.markdown("""
    ## Required Secrets for Multi-AI App
    
    To properly configure this application in HuggingFace Spaces, you need to add the following secrets in your Space's settings:
    
    1. Go to your Space settings
    2. Navigate to the "Secrets" section
    3. Add each of the following secrets:
    """)
    
    secrets_list = [
        ("OPENAI_API_KEY", "Your OpenAI API key"),
        ("CLAUDE_API_KEY", "Your Anthropic Claude API key"),
        ("GEMINI_API_KEY", "Your Google Gemini API key"),
        ("LLAMA_API_KEY", "Your Llama API key"),
        ("HUGGINGFACE_API_KEY", "Your HuggingFace API key"),
        ("OPENROUTER_API_KEY", "Your OpenRouter API key"),
        ("DEEPSEEK_API_KEY", "Your DeepSeek API key")
    ]
    
    for key, description in secrets_list:
        st.code(f"{key}: {description}")
    
    st.markdown("""
    ## Important Notes
    
    - Keep your API keys secure and never share them publicly
    - The application will automatically load these secrets when deployed
    - You can update these secrets at any time in your Space settings
    """)

if __name__ == "__main__":
    create_secrets_page()

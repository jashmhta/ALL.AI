import os
import streamlit as st

# Set page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="Multi-AI Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import uuid
import time
import asyncio
from datetime import datetime

# Import UI components
from ui_components import (
    load_css, inject_javascript, create_model_selection, 
    create_chat_message, create_thinking_indicator, 
    create_credit_display, create_expandable_section,
    create_code_block, create_file_upload_area
)

# Import backend components
from backend.features.secret_manager import SecretManager
from backend.features.conversation_memory import ConversationMemory
from backend.features.file_processor import FileProcessor
from backend.features.model_optimizer import ModelOptimizer
from backend.features.feedback_manager import FeedbackManager

# Import AI clients
from backend.clients.openai_client import OpenAIClient
from backend.clients.claude_client import ClaudeClient
from backend.clients.gemini_client import GeminiClient
from backend.clients.llama_client import LlamaClient
from backend.clients.huggingface_client import HuggingFaceClient
from backend.clients.openrouter_client import OpenRouterClient
from backend.clients.deepseek_client import DeepSeekClient
from backend.clients.synthesis_client import SynthesisClient
from backend.clients.github_models_client import GitHubModelsClient
from backend.clients.puter_client import PuterClient

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.current_model = "gpt-4"
    st.session_state.current_provider = "openai"
    st.session_state.temperature = 0.7
    st.session_state.max_tokens = 1000
    st.session_state.show_settings = False
    st.session_state.show_api_keys = False
    st.session_state.show_advanced = False
    st.session_state.show_feedback = False
    st.session_state.show_file_upload = False
    st.session_state.uploaded_files = []
    st.session_state.synthesis_mode = False
    st.session_state.synthesis_models = []
    st.session_state.dark_mode = True
    st.session_state.credits = {
        "openai": "$10.00",
        "claude": "$15.00",
        "gemini": "$20.00",
        "llama": "Unlimited",
        "huggingface": "$5.00",
        "openrouter": "$8.00",
        "deepseek": "$12.00",
        "github_gpt4_mini": "$25.00",
        "github_deepseek": "$18.00",
        "github_llama": "$22.00",
        "puter": "Free"
    }
    st.session_state.initialized = True

# Initialize backend components
@st.cache_resource
def initialize_backend():
    secret_manager = SecretManager()
    conversation_memory = ConversationMemory()
    file_processor = FileProcessor()
    model_optimizer = ModelOptimizer()
    feedback_manager = FeedbackManager()
    
    # Initialize AI clients
    openai_client = OpenAIClient(secret_manager.get_secret("OPENAI_API_KEY"))
    claude_client = ClaudeClient(secret_manager.get_secret("CLAUDE_API_KEY"))
    gemini_client = GeminiClient(secret_manager.get_secret("GEMINI_API_KEY"))
    llama_client = LlamaClient(secret_manager.get_secret("LLAMA_API_KEY"))
    huggingface_client = HuggingFaceClient(secret_manager.get_secret("HUGGINGFACE_API_KEY"))
    openrouter_client = OpenRouterClient(
        secret_manager.get_secret("OPENROUTER_API_KEY")
    )
    deepseek_client = DeepSeekClient(secret_manager.get_secret("DEEPSEEK_API_KEY"))
    synthesis_client = SynthesisClient()
    github_gpt4_mini_client = GitHubModelsClient(secret_manager.get_secret("GITHUB_PAT_TOKEN"), model="gpt-4.1-mini")
    github_deepseek_client = GitHubModelsClient(secret_manager.get_secret("GITHUB_PAT_TOKEN"), model="deepseek-v3")
    github_llama_client = GitHubModelsClient(secret_manager.get_secret("GITHUB_PAT_TOKEN"), model="llama-4-scout")
    puter_client = PuterClient()
    
    return {
        "secret_manager": secret_manager,
        "conversation_memory": conversation_memory,
        "file_processor": file_processor,
        "model_optimizer": model_optimizer,
        "feedback_manager": feedback_manager,
        "clients": {
            "openai": openai_client,
            "claude": claude_client,
            "gemini": gemini_client,
            "llama": llama_client,
            "huggingface": huggingface_client,
            "openrouter": openrouter_client,
            "deepseek": deepseek_client,
            "synthesis": synthesis_client,
            "github_gpt4_mini": github_gpt4_mini_client,
            "github_deepseek": github_deepseek_client,
            "github_llama": github_llama_client,
            "puter": puter_client
        }
    }

# Initialize backend
backend = initialize_backend()

# Apply custom CSS and JavaScript
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)
st.markdown(inject_javascript(), unsafe_allow_html=True)

# Main layout
main_container = st.container()
with main_container:
    # Create two columns for the main layout
    col1, col2 = st.columns([1, 3])
    
    # Sidebar (left column)
    with col1:
        st.markdown("<h2 class='app-title'>Multi-AI Interface</h2>", unsafe_allow_html=True)
        st.markdown("<hr/>", unsafe_allow_html=True)
        
        # Model selection
        st.markdown("<h3 class='section-header'>Model Selection</h3>", unsafe_allow_html=True)
        
        # Get available models based on API keys
        available_models = backend["secret_manager"].get_available_models()
        
        # Provider selection
        provider_options = []
        if available_models["openai"]:
            provider_options.append("OpenAI")
        if available_models["claude"]:
            provider_options.append("Claude")
        if available_models["gemini"]:
            provider_options.append("Gemini")
        if available_models["llama"]:
            provider_options.append("Llama")
        if available_models["huggingface"]:
            provider_options.append("HuggingFace")
        if available_models["openrouter"]:
            provider_options.append("OpenRouter")
        if available_models["deepseek"]:
            provider_options.append("DeepSeek")
        if available_models.get("github_pat_token"):
            provider_options.append("GitHub-GPT4-Mini")
            provider_options.append("GitHub-DeepSeek")
            provider_options.append("GitHub-Llama")
        if available_models.get("puter"):
            provider_options.append("Puter")
        
        # Add synthesis option if at least two providers are available
        if len(provider_options) >= 2:
            provider_options.append("Mixture-of-Agents")
        
        # If no providers are available, show placeholder options
        if not provider_options:
            provider_options = ["OpenAI", "Claude", "Gemini", "Llama", "HuggingFace", "OpenRouter", "DeepSeek", 
                               "GitHub-GPT4-Mini", "GitHub-DeepSeek", "GitHub-Llama", "Puter", "Mixture-of-Agents"]
        
        # Create model selection UI
        all_models = ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek", 
                     "github_gpt4_mini", "github_deepseek", "github_llama", "puter"]
        
        if st.session_state.synthesis_mode:
            selected_models = st.session_state.synthesis_models
            st.markdown(create_model_selection(all_models, selected_models), unsafe_allow_html=True)
            
            # Synthesis method
            st.markdown("<h4 class='subsection-header'>Synthesis Method</h4>", unsafe_allow_html=True)
            synthesis_method = st.radio(
                "Synthesis Method",
                ["Parallel", "Sequential", "Debate"],
                index=0,
                label_visibility="collapsed"
            )
            
            st.session_state.synthesis_method = synthesis_method.lower()
        else:
            selected_provider = st.selectbox(
                "AI Provider",
                provider_options,
                index=provider_options.index("OpenAI") if "OpenAI" in provider_options else 0,
                label_visibility="collapsed"
            )
            
            # Convert provider name to backend client key
            provider_key_map = {
                "OpenAI": "openai",
                "Claude": "claude",
                "Gemini": "gemini",
                "Llama": "llama",
                "HuggingFace": "huggingface",
                "OpenRouter": "openrouter",
                "DeepSeek": "deepseek",
                "GitHub-GPT4-Mini": "github_gpt4_mini",
                "GitHub-DeepSeek": "github_deepseek",
                "GitHub-Llama": "github_llama",
                "Puter": "puter",
                "Mixture-of-Agents": "mixture-of-agents"
            }
            
            selected_provider_key = provider_key_map.get(selected_provider, selected_provider.lower().replace("-", "_"))
            
            if selected_provider_key == "mixture-of-agents":
                st.session_state.synthesis_mode = True
                st.session_state.synthesis_models = ["openai", "claude"]
                st.rerun()
            
            st.session_state.current_provider = selected_provider_key
            
            # Model options based on provider
            model_options = []
            
            if selected_provider_key == "openai":
                model_options = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
            elif selected_provider_key == "claude":
                model_options = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            elif selected_provider_key == "gemini":
                model_options = ["gemini-pro", "gemini-2.0-flash", "gemini-pro-vision"]
            elif selected_provider_key == "llama":
                model_options = ["llama-3-70b", "llama-3-8b"]
            elif selected_provider_key == "huggingface":
                model_options = ["mistral-7b", "falcon-40b", "llama-2-13b"]
            elif selected_provider_key == "openrouter":
                model_options = ["openai/gpt-4", "anthropic/claude-3-opus", "google/gemini-pro", "meta-llama/llama-3-70b"]
            elif selected_provider_key == "deepseek":
                model_options = ["deepseek-chat", "deepseek-coder", "deepseek-llm-67b"]
            elif selected_provider_key == "github_gpt4_mini":
                model_options = ["gpt-4.1-mini"]
            elif selected_provider_key == "github_deepseek":
                model_options = ["deepseek-v3-0324"]
            elif selected_provider_key == "github_llama":
                model_options = ["llama-4-scout-17b-16e"]
            elif selected_provider_key == "puter":
                model_options = ["gpt-3.5-turbo", "gpt-4"]
            
            selected_model = st.selectbox("Model", model_options, label_visibility="collapsed")
            st.session_state.current_model = selected_model
        
        st.markdown("<hr/>", unsafe_allow_html=True)
        
        # Settings
        st.markdown("<h3 class='section-header'>Settings</h3>", unsafe_allow_html=True)
        
        # Temperature
        temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.1)
        st.session_state.temperature = temperature
        
        # Max tokens
        max_tokens = st.slider("Max Tokens", 100, 4000, st.session_state.max_tokens, 100)
        st.session_state.max_tokens = max_tokens
        
        # File upload toggle
        if st.button("Toggle File Upload", use_container_width=True, type="primary"):
            st.session_state.show_file_upload = not st.session_state.show_file_upload
        
        # Credit display
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-header'>API Credits</h3>", unsafe_allow_html=True)
        st.markdown(create_credit_display(st.session_state.credits), unsafe_allow_html=True)
        
        # Advanced options
        st.markdown("<hr/>", unsafe_allow_html=True)
        if st.button("Advanced Options", use_container_width=True, type="secondary"):
            st.session_state.show_advanced = not st.session_state.show_advanced
        
        if st.session_state.show_advanced:
            st.markdown("<h3 class='section-header'>Advanced Options</h3>", unsafe_allow_html=True)
            
            # API Keys
            if st.button("API Keys", use_container_width=True, type="secondary"):
                st.session_state.show_api_keys = not st.session_state.show_api_keys
            
            if st.session_state.show_api_keys:
                st.markdown("<h4 class='subsection-header'>API Keys</h4>", unsafe_allow_html=True)
                
                # Only show API key inputs in local mode, not on HuggingFace Spaces
                if not backend["secret_manager"].is_huggingface_space:
                    openai_key = st.text_input("OpenAI API Key", 
                                              value=backend["secret_manager"].get_secret("OPENAI_API_KEY"),
                                              type="password")
                    
                    claude_key = st.text_input("Claude API Key", 
                                              value=backend["secret_manager"].get_secret("CLAUDE_API_KEY"),
                                              type="password")
                    
                    gemini_key = st.text_input("Gemini API Key", 
                                              value=backend["secret_manager"].get_secret("GEMINI_API_KEY"),
                                              type="password")
                    
                    llama_key = st.text_input("Llama API Key", 
                                             value=backend["secret_manager"].get_secret("LLAMA_API_KEY"),
                                             type="password")
                    
                    huggingface_key = st.text_input("HuggingFace API Key", 
                                                   value=backend["secret_manager"].get_secret("HUGGINGFACE_API_KEY"),
                                                   type="password")
                    
                    openrouter_key = st.text_input("OpenRouter API Key", 
                                                  value=backend["secret_manager"].get_secret("OPENROUTER_API_KEY"),
                                                  type="password")
                    
                    deepseek_key = st.text_input("DeepSeek API Key", 
                                                value=backend["secret_manager"].get_secret("DEEPSEEK_API_KEY"),
                                                type="password")
                    
                    github_pat_key = st.text_input("GitHub PAT Token", 
                                                 value=backend["secret_manager"].get_secret("GITHUB_PAT_TOKEN"),
                                                 type="password")
                    
                    # Update API keys if changed
                    if openai_key != backend["secret_manager"].get_secret("OPENAI_API_KEY"):
                        backend["secret_manager"].set_secret("OPENAI_API_KEY", openai_key)
                        backend["clients"]["openai"].api_key = openai_key
                    
                    if claude_key != backend["secret_manager"].get_secret("CLAUDE_API_KEY"):
                        backend["secret_manager"].set_secret("CLAUDE_API_KEY", claude_key)
                        backend["clients"]["claude"].api_key = claude_key
                    
                    if gemini_key != backend["secret_manager"].get_secret("GEMINI_API_KEY"):
                        backend["secret_manager"].set_secret("GEMINI_API_KEY", gemini_key)
                        backend["clients"]["gemini"].api_key = gemini_key
                    
                    if llama_key != backend["secret_manager"].get_secret("LLAMA_API_KEY"):
                        backend["secret_manager"].set_secret("LLAMA_API_KEY", llama_key)
                        backend["clients"]["llama"].api_key = llama_key
                    
                    if huggingface_key != backend["secret_manager"].get_secret("HUGGINGFACE_API_KEY"):
                        backend["secret_manager"].set_secret("HUGGINGFACE_API_KEY", huggingface_key)
                        backend["clients"]["huggingface"].api_key = huggingface_key
                    
                    if openrouter_key != backend["secret_manager"].get_secret("OPENROUTER_API_KEY"):
                        backend["secret_manager"].set_secret("OPENROUTER_API_KEY", openrouter_key)
                        backend["clients"]["openrouter"].api_key = openrouter_key
                    
                    if deepseek_key != backend["secret_manager"].get_secret("DEEPSEEK_API_KEY"):
                        backend["secret_manager"].set_secret("DEEPSEEK_API_KEY", deepseek_key)
                        backend["clients"]["deepseek"].api_key = deepseek_key
                    
                    if github_pat_key != backend["secret_manager"].get_secret("GITHUB_PAT_TOKEN"):
                        backend["secret_manager"].set_secret("GITHUB_PAT_TOKEN", github_pat_key)
                        backend["clients"]["github_gpt4_mini"].api_key = github_pat_key
                        backend["clients"]["github_deepseek"].api_key = github_pat_key
                        backend["clients"]["github_llama"].api_key = github_pat_key
                    
                    # Save API keys to secrets.toml
                    if st.button("Save API Keys", type="primary"):
                        if backend["secret_manager"].create_secrets_toml(os.path.dirname(os.path.dirname(__file__))):
                            st.success("API keys saved successfully!")
                        else:
                            st.error("Failed to save API keys.")
                else:
                    st.info("API keys are managed through HuggingFace Spaces secrets. Please configure them in the Space settings.")
            
            # Model Optimization
            if st.button("Model Optimization", use_container_width=True, type="secondary"):
                st.session_state.show_optimization = not st.session_state.show_optimization
            
            if st.session_state.show_advanced and st.session_state.get("show_optimization", False):
                st.markdown("<h4 class='subsection-header'>Model Optimization</h4>", unsafe_allow_html=True)
                
                optimization_priority = st.radio(
                    "Optimization Priority",
                    ["Balanced", "Speed", "Quality", "Cost"],
                    index=0
                )
                
                st.session_state.optimization_priority = optimization_priority.lower()
                
                if st.button("Recommend Model", type="primary"):
                    # Get the last user message if available
                    last_user_message = ""
                    for msg in reversed(st.session_state.messages):
                        if msg["role"] == "user":
                            last_user_message = msg["content"]
                            break
                    
                    if last_user_message:
                        recommendation = backend["model_optimizer"].recommend_model(
                            last_user_message, 
                            priority=st.session_state.optimization_priority
                        )
                        
                        st.success(f"Recommended model: {recommendation['provider']}/{recommendation['model']}")
                    else:
                        st.warning("Please send a message first to get a recommendation.")
    
    # Main chat area (right column)
    with col2:
        # File upload area
        if st.session_state.show_file_upload:
            st.markdown("<h3 class='section-header'>File Upload</h3>", unsafe_allow_html=True)
            uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True, label_visibility="collapsed")
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    # Save the file
                    file_path = os.path.join("uploads", uploaded_file.name)
                    os.makedirs("uploads", exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Add to session state if not already there
                    if file_path not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(file_path)
            
            # Display uploaded files
            if st.session_state.uploaded_files:
                st.markdown("<h4 class='subsection-header'>Uploaded Files</h4>", unsafe_allow_html=True)
                for file_path in st.session_state.uploaded_files:
                    file_name = os.path.basename(file_path)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{file_name}**")
                    with col2:
                        if st.button(f"Remove {file_name}", key=f"remove_{file_name}", type="secondary"):
                            st.session_state.uploaded_files.remove(file_path)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            st.rerun()
        
        # Chat messages
        st.markdown("<h3 class='section-header'>Chat</h3>", unsafe_allow_html=True)
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(create_chat_message(message["content"], role="user", expandable=False), unsafe_allow_html=True)
                else:
                    model = message.get("model", st.session_state.current_model)
                    st.markdown(create_chat_message(message["content"], role="assistant", model=model), unsafe_allow_html=True)
        
        # Input area
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        user_input = st.text_area("Message", height=100, placeholder="Type your message here...", label_visibility="collapsed")
        col1, col2 = st.columns([4, 1])
        
        with col2:
            if st.button("Send", use_container_width=True, type="primary"):
                if user_input:
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    
                    # Display thinking indicator
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown(create_thinking_indicator(), unsafe_allow_html=True)
                    
                    # Process with selected model or synthesis
                    if st.session_state.synthesis_mode:
                        # Placeholder for synthesis response
                        response_text = f"This is a synthesized response from multiple models using the {st.session_state.synthesis_method} method."
                        
                        # Add individual model responses for demonstration
                        individual_responses = []
                        for model in st.session_state.synthesis_models:
                            individual_responses.append({
                                "model": model,
                                "content": f"Response from {model} model: This is a sample response to demonstrate the UI."
                            })
                        
                        # Add synthesized response to chat
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text,
                            "model": "Mixture-of-Agents",
                            "individual_responses": individual_responses
                        })
                    else:
                        # Placeholder for single model response
                        response_text = f"Response from {st.session_state.current_model}: This is a sample response to demonstrate the UI."
                        
                        # Add response to chat
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text,
                            "model": st.session_state.current_provider
                        })
                    
                    # Clear thinking indicator and rerun to update UI
                    thinking_placeholder.empty()
                    st.rerun()

# Add custom CSS for improved aesthetics
st.markdown("""
<style>
.app-title {
    color: #4CAF50;
    font-size: 2.2em;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
}

.section-header {
    color: #2196F3;
    font-size: 1.5em;
    font-weight: bold;
    margin-top: 15px;
    margin-bottom: 10px;
    border-bottom: 2px solid #2196F3;
    padding-bottom: 5px;
}

.subsection-header {
    color: #9C27B0;
    font-size: 1.2em;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* Improve button styling */
.stButton > button {
    border-radius: 8px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Improve chat message styling */
.chat-message {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.user-message {
    background-color: #E3F2FD;
    border-left: 5px solid #2196F3;
}

.assistant-message {
    background-color: #F1F8E9;
    border-left: 5px solid #4CAF50;
}

/* Improve dropdown styling */
.stSelectbox > div > div {
    border-radius: 8px;
}

/* Improve slider styling */
.stSlider > div > div > div {
    height: 6px;
}

.stSlider > div > div > div > div {
    height: 20px;
    width: 20px;
}
</style>
""", unsafe_allow_html=True)

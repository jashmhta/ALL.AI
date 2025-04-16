import os
import streamlit as st
import uuid
import time
import asyncio
from datetime import datetime

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
        secret_manager.get_secret("OPENROUTER_API_KEY"),
        secret_manager.get_secret("OPENROUTER_API_KEY_2")
    )
    deepseek_client = DeepSeekClient(secret_manager.get_secret("DEEPSEEK_API_KEY"))
    synthesis_client = SynthesisClient()
    
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
            "synthesis": synthesis_client
        }
    }

# Initialize backend
backend = initialize_backend()

# Set page config
st.set_page_config(
    page_title="Multi-AI Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for dark mode
def apply_custom_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    .stTextInput, .stTextArea, .stSelectbox {
        background-color: #2D2D2D;
        color: #E0E0E0;
        border-color: #444444;
    }
    .stButton>button {
        background-color: #444444;
        color: #E0E0E0;
    }
    .stSidebar {
        background-color: #252526;
    }
    .css-1d391kg, .css-12oz5g7 {
        background-color: #2D2D2D;
        border-color: #444444;
    }
    .stMarkdown {
        color: #E0E0E0;
    }
    header {
        background-color: #252526 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS if dark mode is enabled
if st.session_state.dark_mode:
    apply_custom_css()

# Sidebar
with st.sidebar:
    st.title("Multi-AI Interface")
    st.markdown("---")
    
    # Model selection
    st.subheader("Model Selection")
    
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
    
    # Add synthesis option if at least two providers are available
    if len(provider_options) >= 2:
        provider_options.append("Synthesis (Multi-model)")
    
    # If no providers are available, show placeholder options
    if not provider_options:
        provider_options = ["OpenAI", "Claude", "Gemini", "Llama", "HuggingFace", "OpenRouter", "DeepSeek", "Synthesis (Multi-model)"]
    
    selected_provider = st.selectbox(
        "AI Provider",
        provider_options,
        index=provider_options.index("OpenAI") if "OpenAI" in provider_options else 0
    ).lower().split()[0]  # Extract first word and convert to lowercase
    
    st.session_state.current_provider = selected_provider
    
    # Model options based on provider
    model_options = []
    
    if selected_provider == "openai":
        model_options = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    elif selected_provider == "claude":
        model_options = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    elif selected_provider == "gemini":
        model_options = ["gemini-pro", "gemini-pro-vision"]
    elif selected_provider == "llama":
        model_options = ["llama-3-70b", "llama-3-8b"]
    elif selected_provider == "huggingface":
        model_options = ["mistral-7b", "falcon-40b", "llama-2-13b"]
    elif selected_provider == "openrouter":
        model_options = ["openai/gpt-4", "anthropic/claude-3-opus", "google/gemini-pro", "meta-llama/llama-3-70b"]
    elif selected_provider == "deepseek":
        model_options = ["deepseek-chat", "deepseek-coder", "deepseek-llm-67b"]
    elif selected_provider == "synthesis":
        st.session_state.synthesis_mode = True
        
        # Select models for synthesis
        st.write("Select models for synthesis:")
        
        synthesis_models = []
        
        if available_models["openai"]:
            if st.checkbox("GPT-4", value=True):
                synthesis_models.append("openai/gpt-4")
        
        if available_models["claude"]:
            if st.checkbox("Claude-3-Opus", value=True):
                synthesis_models.append("anthropic/claude-3-opus")
        
        if available_models["gemini"]:
            if st.checkbox("Gemini Pro", value=False):
                synthesis_models.append("google/gemini-pro")
        
        if available_models["llama"]:
            if st.checkbox("Llama-3-70B", value=False):
                synthesis_models.append("meta/llama-3-70b")
        
        st.session_state.synthesis_models = synthesis_models
        
        # Synthesis method
        synthesis_method = st.radio(
            "Synthesis Method",
            ["Parallel", "Sequential", "Debate"],
            index=0
        )
        
        st.session_state.synthesis_method = synthesis_method.lower()
    else:
        st.session_state.synthesis_mode = False
    
    # Model selection if not in synthesis mode
    if not st.session_state.synthesis_mode:
        selected_model = st.selectbox("Model", model_options)
        st.session_state.current_model = selected_model
    
    st.markdown("---")
    
    # Settings
    st.subheader("Settings")
    
    # Temperature
    temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.1)
    st.session_state.temperature = temperature
    
    # Max tokens
    max_tokens = st.slider("Max Tokens", 100, 4000, st.session_state.max_tokens, 100)
    st.session_state.max_tokens = max_tokens
    
    # Dark mode toggle
    dark_mode = st.checkbox("Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.experimental_rerun()
    
    st.markdown("---")
    
    # Advanced options
    if st.button("Advanced Options"):
        st.session_state.show_advanced = not st.session_state.show_advanced
    
    if st.session_state.show_advanced:
        st.subheader("Advanced Options")
        
        # API Keys
        if st.button("API Keys"):
            st.session_state.show_api_keys = not st.session_state.show_api_keys
        
        if st.session_state.show_api_keys:
            st.write("API Keys")
            
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
                
                # Save API keys to secrets.toml
                if st.button("Save API Keys"):
                    if backend["secret_manager"].create_secrets_toml(os.path.dirname(os.path.dirname(__file__))):
                        st.success("API keys saved successfully!")
                    else:
                        st.error("Failed to save API keys.")
            else:
                st.info("API keys are managed through HuggingFace Spaces secrets. Please configure them in the Space settings.")
        
        # Model Optimization
        if st.button("Model Optimization"):
            st.session_state.show_optimization = not st.session_state.show_optimization
        
        if st.session_state.show_advanced and st.session_state.get("show_optimization", False):
            st.write("Model Optimization")
            
            optimization_priority = st.radio(
                "Optimization Priority",
                ["Balanced", "Speed", "Quality", "Cost"],
                index=0
            )
            
            st.session_state.optimization_priority = optimization_priority.lower()
            
            if st.button("Recommend Model"):
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
                    
                    if recommendation["model"]:
                        st.success(f"Recommended model: {recommendation['model']}")
                        st.json(recommendation)
                    else:
                        st.warning(f"No recommendation available: {recommendation['reason']}")
                else:
                    st.warning("No user messages available for recommendation.")
            
            # Performance chart
            if st.button("Show Performance Chart"):
                chart_data = backend["model_optimizer"].generate_performance_chart()
                
                if chart_data:
                    st.image(f"data:image/png;base64,{chart_data}")
                else:
                    st.warning("No performance data available for chart.")
        
        # Feedback
        if st.button("Feedback"):
            st.session_state.show_feedback = not st.session_state.show_feedback
        
        if st.session_state.show_advanced and st.session_state.show_feedback:
            st.write("Feedback")
            
            # Get the last assistant message if available
            last_assistant_message = ""
            last_user_message = ""
            last_model = ""
            
            for i in range(len(st.session_state.messages) - 1, -1, -1):
                msg = st.session_state.messages[i]
                if msg["role"] == "assistant" and not last_assistant_message:
                    last_assistant_message = msg["content"]
                    last_model = msg.get("model", st.session_state.current_model)
                elif msg["role"] == "user" and not last_user_message:
                    last_user_message = msg["content"]
                
                if last_assistant_message and last_user_message:
                    break
            
            if last_assistant_message and last_user_message:
                st.write("Rate the last response:")
                
                rating = st.slider("Rating", 1, 5, 3, 1)
                
                comment = st.text_area("Comment (optional)")
                
                if st.button("Submit Feedback"):
                    success = backend["feedback_manager"].add_rating(
                        model=last_model,
                        rating=rating,
                        prompt=last_user_message,
                        response=last_assistant_message,
                        conversation_id=st.session_state.conversation_id,
                        comment=comment if comment else None
                    )
                    
                    if success:
                        st.success("Feedback submitted successfully!")
                    else:
                        st.error("Failed to submit feedback.")
            else:
                st.warning("No conversation available for feedback.")
            
            # Rating chart
            if st.button("Show Rating Chart"):
                chart_data = backend["feedback_manager"].generate_rating_chart()
                
                if chart_data:
                    st.image(f"data:image/png;base64,{chart_data}")
                else:
                    st.warning("No rating data available for chart.")
        
        # Conversation Management
        if st.button("Conversation Management"):
            st.session_state.show_conversation = not st.session_state.show_conversation
        
        if st.session_state.show_advanced and st.session_state.get("show_conversation", False):
            st.write("Conversation Management")
            
            if st.button("New Conversation"):
                st.session_state.conversation_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.experimental_rerun()
            
            if st.button("Save Conversation"):
                filepath = backend["conversation_memory"].save_conversation(st.session_state.conversation_id)
                
                if filepath:
                    st.success(f"Conversation saved successfully!")
                else:
                    st.error("Failed to save conversation.")
            
            # List saved conversations
            saved_conversations = backend["conversation_memory"].get_all_conversations()
            
            if saved_conversations:
                st.write("Saved Conversations:")
                
                for conv in saved_conversations[:5]:  # Show only the 5 most recent
                    conv_id = conv["conversation_id"]
                    timestamp = datetime.fromtimestamp(conv["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    message_count = conv["message_count"]
                    
                    st.write(f"{timestamp} ({message_count} messages)")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"Load", key=f"load_{conv_id}"):
                            if backend["conversation_memory"].load_conversation(conv_id):
                                st.session_state.conversation_id = conv_id
                                st.session_state.messages = backend["conversation_memory"].get_conversation_history(conv_id)
                                st.experimental_rerun()
                            else:
                                st.error("Failed to load conversation.")
                    
                    with col2:
                        if st.button(f"Delete", key=f"delete_{conv_id}"):
                            if backend["conversation_memory"].delete_conversation(conv_id):
                                st.success("Conversation deleted successfully!")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to delete conversation.")
            else:
                st.info("No saved conversations available.")

# Main chat interface
st.title("Multi-AI Chat Interface")

# File upload
if st.button("File Upload"):
    st.session_state.show_file_upload = not st.session_state.show_file_upload

if st.session_state.show_file_upload:
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "md", "py", "js", "html", "css", "json", "xml"])
    
    if uploaded_file:
        # Process the file
        file_content = uploaded_file.read()
        filename = uploaded_file.name
        
        # Process the file asynchronously
        result = asyncio.run(backend["file_processor"].process_file(file_content, filename))
        
        if result["success"]:
            file_info = result["file_info"]
            
            # Add to uploaded files list
            st.session_state.uploaded_files.append(file_info)
            
            st.success(f"File uploaded successfully: {filename} ({file_info['size_human']})")
            
            # Show file preview if text was extracted
            if file_info.get("has_text", False):
                with st.expander(f"Preview: {filename}"):
                    st.write(file_info["text_preview"])
        else:
            st.error(f"Error uploading file: {result['error']}")

# Display uploaded files
if st.session_state.uploaded_files:
    st.write("Uploaded Files:")
    
    for file_info in st.session_state.uploaded_files:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"{file_info['filename']} ({file_info['size_human']})")
        
        with col2:
            if st.button("Use in Prompt", key=f"use_{file_info['filename']}"):
                # Extract text from the file
                success, text_content, error = asyncio.run(
                    backend["file_processor"].extract_text_from_file(file_info['path'])
                )
                
                if success:
                    # Create a system message with the file content
                    file_message = {
                        "role": "system",
                        "content": f"The user has uploaded a file: {file_info['filename']} ({file_info['size_human']})\n\nFile content:\n\n{text_content}"
                    }
                    
                    # Add to messages
                    st.session_state.messages.append(file_message)
                    
                    # Add to conversation memory
                    backend["conversation_memory"].add_message(
                        st.session_state.conversation_id,
                        "system",
                        file_message["content"]
                    )
                    
                    st.success(f"File content added to the conversation.")
                else:
                    st.error(f"Error extracting text from file: {error}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Add to conversation memory
    backend["conversation_memory"].add_message(
        st.session_state.conversation_id,
        "user",
        prompt
    )
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response based on selected provider
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Show thinking indicator
        message_placeholder.markdown("Thinking...")
        
        try:
            # Get conversation history for context
            conversation_context = backend["conversation_memory"].get_context_for_prompt(
                st.session_state.conversation_id
            )
            
            # Prepare parameters
            params = {
                "temperature": st.session_state.temperature,
                "max_tokens": st.session_state.max_tokens
            }
            
            start_time = time.time()
            
            # Get response based on provider
            if st.session_state.synthesis_mode:
                # Use synthesis client with multiple models
                if not st.session_state.synthesis_models:
                    # Default to GPT-4 and Claude if no models selected
                    synthesis_models = ["openai/gpt-4", "anthropic/claude-3-opus"]
                else:
                    synthesis_models = st.session_state.synthesis_models
                
                # Create a coroutine and run it with asyncio.run
                async def get_synthesis_response():
                    return await backend["clients"]["synthesis"].generate_response(
                        prompt=prompt,
                        context=conversation_context,
                        models=synthesis_models,
                        method=st.session_state.get("synthesis_method", "parallel"),
                        params=params
                    )
                
                response = asyncio.run(get_synthesis_response())
            else:
                # Use single model
                provider = st.session_state.current_provider
                model = st.session_state.current_model
                
                # Create a coroutine and run it with asyncio.run based on provider
                async def get_provider_response():
                    if provider == "openai":
                        return await backend["clients"]["openai"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                    elif provider == "claude":
                        return await backend["clients"]["claude"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                    elif provider == "gemini":
                        return await backend["clients"]["gemini"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                    elif provider == "llama":
                        return await backend["clients"]["llama"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                    elif provider == "huggingface":
                        return await backend["clients"]["huggingface"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                    elif provider == "openrouter":
                        return await backend["clients"]["openrouter"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                    elif provider == "deepseek":
                        return await backend["clients"]["deepseek"].generate_response(
                            prompt=prompt,
                            context=conversation_context,
                            model=model,
                            params=params
                        )
                
                # Run the async function
                response = asyncio.run(get_provider_response())
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Check if response was successful
            if response["success"]:
                full_response = response["content"]
                model_used = response.get("model", st.session_state.current_model)
                tokens = response.get("tokens", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
                
                # Record request for optimization
                backend["model_optimizer"].record_request(
                    model=model_used,
                    prompt=prompt,
                    response=response,
                    latency=latency,
                    tokens=tokens,
                    conversation_id=st.session_state.conversation_id
                )
                
                # Update message placeholder with full response
                message_placeholder.markdown(full_response)
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "model": model_used
                })
                
                # Add to conversation memory
                backend["conversation_memory"].add_message(
                    st.session_state.conversation_id,
                    "assistant",
                    full_response,
                    model_used
                )
            else:
                error_message = response.get("error", "Unknown error occurred")
                message_placeholder.markdown(f"Error: {error_message}")
                
                # Add error message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Error: {error_message}",
                    "model": "error"
                })
                
                # Add to conversation memory
                backend["conversation_memory"].add_message(
                    st.session_state.conversation_id,
                    "assistant",
                    f"Error: {error_message}",
                    "error"
                )
        except Exception as e:
            message_placeholder.markdown(f"Error: {str(e)}")
            
            # Add error message to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Error: {str(e)}",
                "model": "error"
            })
            
            # Add to conversation memory
            backend["conversation_memory"].add_message(
                st.session_state.conversation_id,
                "assistant",
                f"Error: {str(e)}",
                "error"
            )

# Footer
st.markdown("---")
st.markdown("Multi-AI Interface | Powered by Streamlit")

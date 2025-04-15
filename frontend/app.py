import streamlit as st
import asyncio
import uuid
import json
import os
import base64
from datetime import datetime
import sys

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MultiAIApp class
from backend.main import MultiAIApp

# Set page configuration
st.set_page_config(
    page_title="ALL.AI - Multi-AI Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for strictly black and grey theme
st.markdown("""
<style>
    /* Main theme colors and styling */
    :root {
        --primary-color: #333333;
        --secondary-color: #555555;
        --background-color: #121212;
        --surface-color: #1E1E1E;
        --on-surface-color: #E0E0E0;
        --error-color: #CF6679;
        --success-color: #66BB6A;
        --border-radius: 4px;
        --card-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* General styling */
    .stApp {
        background-color: var(--background-color);
        color: var(--on-surface-color);
    }
    
    /* Streamlit component overrides */
    .stTextInput > div > div > input {
        background-color: var(--surface-color);
        color: var(--on-surface-color);
        border-radius: var(--border-radius);
        border: 1px solid var(--secondary-color);
    }
    
    .stTextArea > div > div > textarea {
        background-color: var(--surface-color);
        color: var(--on-surface-color);
        border-radius: var(--border-radius);
        border: 1px solid var(--secondary-color);
    }
    
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: var(--border-radius);
        border: none;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
    }
    
    .stCheckbox > div > label {
        color: var(--on-surface-color);
    }
    
    .stExpander > div > div > div > div > div > p {
        color: var(--on-surface-color);
    }
    
    /* Header styling */
    .main-header {
        background-color: var(--primary-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .main-header h1 {
        margin: 0;
        color: white;
        font-size: 1.8rem;
    }
    
    /* Chat container styling */
    .chat-container {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Message styling */
    .message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: var(--border-radius);
        position: relative;
    }
    
    .user-message {
        background-color: #2A2A2A;
        border-left: 2px solid var(--primary-color);
        margin-left: 1rem;
    }
    
    .assistant-message {
        background-color: #262626;
        border-left: 2px solid var(--secondary-color);
        margin-right: 1rem;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: #AAAAAA;
    }
    
    .message-content {
        white-space: pre-wrap;
    }
    
    /* Input area styling */
    .input-area {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        box-shadow: var(--card-shadow);
    }
    
    /* Sidebar styling */
    .sidebar .stButton button {
        width: 100%;
        border-radius: var(--border-radius);
        margin-bottom: 0.5rem;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading-indicator {
        display: flex;
        align-items: center;
        margin: 1rem 0;
    }
    
    .loading-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--primary-color);
        margin: 0 4px;
        animation: pulse 1.5s infinite;
    }
    
    .loading-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .loading-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Feedback buttons */
    .feedback-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .feedback-button {
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        border-radius: var(--border-radius);
    }
    
    .feedback-button:hover {
        background-color: rgba(224, 224, 224, 0.1);
    }
    
    .feedback-button.positive {
        color: var(--success-color);
    }
    
    .feedback-button.negative {
        color: var(--error-color);
    }
    
    /* File upload area */
    .file-upload-area {
        border: 1px dashed var(--secondary-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* File preview */
    .file-preview {
        background-color: #262626;
        border-radius: var(--border-radius);
        padding: 0.75rem;
        margin-bottom: 1rem;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #AAAAAA;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'app' not in st.session_state:
    st.session_state.app = MultiAIApp()

if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None

if 'uploaded_file_info' not in st.session_state:
    st.session_state.uploaded_file_info = None

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
    
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Function to add a message to the chat
def add_message(role, content, model=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "model": model,
        "id": str(uuid.uuid4())
    })

# Function to process user input
def process_user_input(user_input):
    if not user_input.strip():
        return
    
    # Add user message to chat
    add_message("user", user_input)
    
    # Set processing flag
    st.session_state.processing = True
    
    try:
        # Get selected model from sidebar
        model = st.session_state.get('selected_model', None)
        
        # Check if we should get responses from all models
        use_multiple = st.session_state.get('use_multiple', False)
        
        # Check if we should synthesize responses
        synthesize = st.session_state.get('synthesize', False)
        
        # Process the prompt
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(st.session_state.app.process_prompt(
            prompt=user_input,
            model=model,
            use_multiple=use_multiple,
            synthesize=synthesize,
            conversation_id=st.session_state.conversation_id,
            user_id=st.session_state.user_id,
            file_path=st.session_state.uploaded_file_path,
            temperature=st.session_state.get('temperature', 0.7),
            max_tokens=st.session_state.get('max_tokens', 1000)
        ))
        loop.close()
        
        # Clear uploaded file after use
        st.session_state.uploaded_file_path = None
        st.session_state.uploaded_file_info = None
        
        # Handle multiple responses
        if use_multiple:
            if synthesize and "synthesis" in response and response["synthesis"]["success"]:
                # Add synthesized response
                add_message(
                    "assistant", 
                    response["synthesis"]["text"], 
                    f"Synthesis (via {response['synthesis']['model']})"
                )
            
            # Add individual responses
            for resp in response.get("responses", []):
                if resp.get("success", False):
                    add_message("assistant", resp["text"], resp["model"])
        else:
            # Add single response
            if response.get("success", False):
                add_message("assistant", response["text"], response["model"])
            else:
                add_message("assistant", f"Error: {response.get('text', 'Unknown error')}", "system")
    except Exception as e:
        # Add error message
        add_message("assistant", f"Error: {str(e)}", "system")
    finally:
        # Clear processing flag
        st.session_state.processing = False

# Function to handle file upload
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            # Read file content
            file_content = uploaded_file.getvalue()
            
            # Process the file
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(st.session_state.app.process_file(file_content, uploaded_file.name))
            loop.close()
            
            if result["success"]:
                st.session_state.uploaded_file_info = result["file_info"]
                st.session_state.uploaded_file_path = result["file_info"]["path"]
                return True, f"File uploaded: {uploaded_file.name}"
            else:
                return False, f"Error uploading file: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return False, f"Error processing file: {str(e)}"
    
    return False, "No file selected"

# Function to handle feedback
def handle_feedback(message_id, model, is_positive):
    try:
        rating = 5 if is_positive else 1
        st.session_state.app.add_feedback(message_id, model, rating, user_id=st.session_state.user_id)
        
        # Show feedback confirmation
        st.toast(f"{'Positive' if is_positive else 'Negative'} feedback recorded. Thank you!", icon="✅")
    except Exception as e:
        st.toast(f"Error recording feedback: {str(e)}", icon="❌")

# Function to save conversation
def save_conversation():
    try:
        filepath = st.session_state.app.save_conversation(st.session_state.conversation_id)
        if filepath:
            st.toast("Conversation saved successfully!", icon="✅")
        else:
            st.toast("Failed to save conversation", icon="❌")
    except Exception as e:
        st.toast(f"Error saving conversation: {str(e)}", icon="❌")

# Function to clear conversation
def clear_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.toast("Conversation cleared", icon="🗑️")

# Function to get model recommendations
def get_model_recommendations():
    try:
        if 'app' in st.session_state and hasattr(st.session_state.app, 'get_model_recommendations'):
            return st.session_state.app.get_model_recommendations()
        else:
            return {"overall_best": [], "creative": [], "factual": [], "technical": [], 
                   "mathematical": [], "analytical": [], "instructional": []}
    except Exception as e:
        st.error(f"Error getting model recommendations: {str(e)}")
        return {"overall_best": [], "creative": [], "factual": [], "technical": [], 
               "mathematical": [], "analytical": [], "instructional": []}

# Main layout
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 ALL.AI - Multi-AI Chat Interface</h1>
        <div>
            <span style="color: white; opacity: 0.8;">Powered by multiple AI models</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### AI Settings")
        
        # Model selection
        available_models = []
        try:
            if 'app' in st.session_state and hasattr(st.session_state.app, 'get_available_models'):
                available_models = st.session_state.app.get_available_models()
        except Exception as e:
            st.error(f"Error getting available models: {str(e)}")
        
        if available_models:
            st.session_state.selected_model = st.selectbox(
                "Select AI Model", 
                ["Auto"] + available_models,
                index=0
            )
            if st.session_state.selected_model == "Auto":
                st.session_state.selected_model = None
        else:
            st.error("No AI models available. Please check your API keys.")
        
        # Multiple models option
        st.session_state.use_multiple = st.checkbox("Get responses from all available models", value=False)
        
        # Synthesis option
        synthesis_available = False
        try:
            if 'app' in st.session_state and hasattr(st.session_state.app, 'is_synthesis_available'):
                synthesis_available = st.session_state.app.is_synthesis_available()
        except Exception as e:
            st.error(f"Error checking synthesis availability: {str(e)}")
            
        if synthesis_available:
            st.session_state.synthesize = st.checkbox("Synthesize responses using Llama", value=False, disabled=not st.session_state.use_multiple)
        else:
            st.info("Synthesis requires Llama API key")
            st.session_state.synthesize = False
        
        # Advanced options
        with st.expander("Advanced Options"):
            st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
            st.session_state.max_tokens = st.slider("Max Tokens", 100, 2000, 1000, 100)
        
        # History management
        st.markdown("### Conversation")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", use_container_width=True):
                save_conversation()
        with col2:
            if st.button("Clear", use_container_width=True):
                clear_conversation()
        
        # Model recommendations
        st.markdown("### Model Insights")
        recommendations = get_model_recommendations()
        if recommendations and "overall_best" in recommendations and recommendations["overall_best"]:
            best_model = recommendations["overall_best"][0]["model"]
            st.info(f"Best overall model: {best_model}")
        
        # Categories with recommendations
        for category, models in recommendations.items():
            if category != "overall_best" and models:
                with st.expander(f"{category.capitalize()} queries"):
                    for model_data in models:
                        st.write(f"- {model_data['model']}")
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                <h3>👋 Welcome to ALL.AI</h3>
                <p>Start a conversation with multiple AI models or upload a file for analysis.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display messages
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp", "")
            model = message.get("model", "")
            message_id = message.get("id", "")
            
            if role == "user":
                st.markdown(f"""
                <div class="message user-message">
                    <div class="message-header">
                        <span>You</span>
                        <span>{timestamp}</span>
                    </div>
                    <div class="message-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                model_display = f" ({model})" if model else ""
                
                st.markdown(f"""
                <div class="message assistant-message">
                    <div class="message-header">
                        <span>Assistant{model_display}</span>
                        <span>{timestamp}</span>
                    </div>
                    <div class="message-content">{content}</div>
                    <div class="feedback-buttons">
                        <button class="feedback-button positive" onclick="handleFeedback('{message_id}', '{model}', true)">👍</button>
                        <button class="feedback-button negative" onclick="handleFeedback('{message_id}', '{model}', false)">👎</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add JavaScript for feedback handling
        st.markdown("""
        <script>
        function handleFeedback(messageId, model, isPositive) {
            // Use Streamlit's postMessage to communicate with Python
            window.parent.postMessage({
                type: "streamlit:feedback",
                messageId: messageId,
                model: model,
                isPositive: isPositive
            }, "*");
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Display loading indicator if processing
        if st.session_state.processing:
            st.markdown("""
            <div class="loading-indicator">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # File upload area
        with st.expander("Upload a file for analysis"):
            st.markdown('<div class="file-upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "csv", "md", "py", "js", "html", "json", "xml"])
            
            if uploaded_file:
                if st.button("Process File"):
                    with st.spinner("Processing file..."):
                        success, message = handle_file_upload(uploaded_file)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display file info if available
            if st.session_state.uploaded_file_info:
                file_info = st.session_state.uploaded_file_info
                st.markdown(f"""
                <div class="file-preview">
                    <div class="file-preview-header">
                        <strong>{file_info['filename']}</strong>
                        <span>{file_info['size_human']}</span>
                    </div>
                    <div>Type: {file_info['mime_type']}</div>
                    {f"<div>Preview: {file_info.get('text_preview', 'No preview available')}</div>" if file_info.get('has_text', False) else ""}
                </div>
                """, unsafe_allow_html=True)
        
        # Input area
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        
        # Use a callback to handle the message sending
        def handle_send():
            if st.session_state.user_input and not st.session_state.processing:
                try:
                    process_user_input(st.session_state.user_input)
                    # We'll clear the input in the next rerun via callback
                    st.session_state.clear_input = True
                except Exception as e:
                    st.error(f"Error processing message: {str(e)}")
                    st.session_state.processing = False
        
        # Initialize clear_input flag if not exists
        if 'clear_input' not in st.session_state:
            st.session_state.clear_input = False
            
        # Clear input if needed (from previous send)
        if st.session_state.clear_input:
            st.session_state.user_input = ""
            st.session_state.clear_input = False
            
        # Create the input widget
        user_input = st.text_area("Your message", height=100, key="user_input")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.button("Send", on_click=handle_send, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Performance metrics
        with st.expander("Performance Metrics"):
            metrics = {}
            try:
                if 'app' in st.session_state and hasattr(st.session_state.app, 'get_performance_metrics'):
                    metrics = st.session_state.app.get_performance_metrics()
            except Exception as e:
                st.error(f"Error getting performance metrics: {str(e)}")
            
            if "overall" in metrics:
                st.markdown("#### Overall")
                st.write(f"Total requests: {metrics['overall']['total_requests']}")
                st.write(f"Avg response time: {metrics['overall']['average_response_time']:.2f}s")
                st.write(f"Success rate: {metrics['overall']['success_rate']:.1f}%")
            
            if "cache" in metrics:
                st.markdown("#### Cache")
                st.write(f"Active entries: {metrics['cache'].get('active_entries', 0)}")
                st.write(f"Hit rate: {metrics['cache'].get('hit_rate', 0):.1f}%")
        
        # Model performance
        with st.expander("Model Performance"):
            if "models" in metrics:
                for model, model_metrics in metrics["models"].items():
                    st.markdown(f"#### {model}")
                    st.write(f"Requests: {model_metrics['requests']}")
                    st.write(f"Avg time: {model_metrics['average_response_time']:.2f}s")
                    st.write(f"Success: {model_metrics['success_rate']:.1f}%")
        
        # Fallback statistics
        with st.expander("Fallback Statistics"):
            fallback_stats = {}
            try:
                if 'app' in st.session_state and hasattr(st.session_state.app, 'get_fallback_statistics'):
                    fallback_stats = st.session_state.app.get_fallback_statistics()
            except Exception as e:
                st.error(f"Error getting fallback statistics: {str(e)}")
                
            for primary, fallbacks in fallback_stats.items():
                if fallbacks:
                    st.markdown(f"#### When {primary} fails:")
                    for fallback in fallbacks:
                        st.write(f"- {fallback['model']}: {fallback['success_rate']:.1f}")

# Run the app
if __name__ == "__main__":
    main()

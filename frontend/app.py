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

# Custom CSS for dark theme and better UI
st.markdown("""
<style>
    /* Main theme colors and styling */
    :root {
        --primary-color: #7C4DFF;
        --secondary-color: #00B8D4;
        --background-color: #121212;
        --surface-color: #1E1E1E;
        --on-surface-color: #E0E0E0;
        --error-color: #CF6679;
        --success-color: #03DAC6;
        --border-radius: 8px;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* General styling */
    .stApp {
        background-color: var(--background-color);
        color: var(--on-surface-color);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
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
        font-size: 2rem;
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
        background-color: rgba(124, 77, 255, 0.2);
        border-left: 4px solid var(--primary-color);
        margin-left: 2rem;
        margin-right: 0.5rem;
    }
    
    .assistant-message {
        background-color: rgba(0, 184, 212, 0.1);
        border-left: 4px solid var(--secondary-color);
        margin-right: 2rem;
        margin-left: 0.5rem;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: rgba(224, 224, 224, 0.7);
    }
    
    .message-content {
        white-space: pre-wrap;
    }
    
    /* Avatar styling */
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        position: absolute;
        top: 0.75rem;
        background-size: cover;
        background-position: center;
    }
    
    .user-avatar {
        left: -40px;
        background-color: var(--primary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    
    .assistant-avatar {
        right: -40px;
        background-color: var(--secondary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
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
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--surface-color);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        padding: 0.5rem 1rem;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(124, 77, 255, 0.2);
        border-bottom: 2px solid var(--primary-color) !important;
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
        transition: background-color 0.2s;
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
        border: 2px dashed rgba(124, 77, 255, 0.5);
        border-radius: var(--border-radius);
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    
    .file-upload-area:hover {
        border-color: var(--primary-color);
    }
    
    /* File preview */
    .file-preview {
        background-color: rgba(0, 184, 212, 0.1);
        border-radius: var(--border-radius);
        padding: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .file-preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .user-message {
            margin-left: 0.5rem;
        }
        
        .assistant-message {
            margin-right: 0.5rem;
        }
        
        .avatar {
            display: none;
        }
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
async def process_user_input(user_input):
    if not user_input.strip():
        return
    
    # Add user message to chat
    add_message("user", user_input)
    
    # Set processing flag
    st.session_state.processing = True
    
    # Get selected model from sidebar
    model = st.session_state.get('selected_model', None)
    
    # Check if we should get responses from all models
    use_multiple = st.session_state.get('use_multiple', False)
    
    # Check if we should synthesize responses
    synthesize = st.session_state.get('synthesize', False)
    
    # Process the prompt
    response = await st.session_state.app.process_prompt(
        prompt=user_input,
        model=model,
        use_multiple=use_multiple,
        synthesize=synthesize,
        conversation_id=st.session_state.conversation_id,
        user_id=st.session_state.user_id,
        file_path=st.session_state.uploaded_file_path,
        temperature=st.session_state.get('temperature', 0.7),
        max_tokens=st.session_state.get('max_tokens', 1000)
    )
    
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
    
    # Clear processing flag
    st.session_state.processing = False

# Function to handle file upload
async def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        # Read file content
        file_content = uploaded_file.getvalue()
        
        # Process the file
        result = await st.session_state.app.process_file(file_content, uploaded_file.name)
        
        if result["success"]:
            st.session_state.uploaded_file_info = result["file_info"]
            st.session_state.uploaded_file_path = result["file_info"]["path"]
            return True, f"File uploaded: {uploaded_file.name}"
        else:
            return False, f"Error uploading file: {result.get('error', 'Unknown error')}"
    
    return False, "No file selected"

# Function to handle feedback
def handle_feedback(message_id, model, is_positive):
    rating = 5 if is_positive else 1
    st.session_state.app.add_feedback(message_id, model, rating, user_id=st.session_state.user_id)
    
    # Show feedback confirmation
    st.toast(f"{'Positive' if is_positive else 'Negative'} feedback recorded. Thank you!", icon="✅")

# Function to save conversation
def save_conversation():
    filepath = st.session_state.app.save_conversation(st.session_state.conversation_id)
    if filepath:
        st.toast("Conversation saved successfully!", icon="✅")
    else:
        st.toast("Failed to save conversation", icon="❌")

# Function to load conversation
def load_conversation(conversation_id):
    success = st.session_state.app.load_conversation(conversation_id)
    if success:
        # Update session state with loaded conversation
        st.session_state.conversation_id = conversation_id
        st.session_state.messages = []
        
        # Get conversation history
        history = st.session_state.app.get_conversation_history(conversation_id)
        
        # Convert history to messages format
        for message in history:
            role = message["role"]
            content = message["content"]
            model = message.get("model") if role == "assistant" else None
            add_message(role, content, model)
        
        st.toast("Conversation loaded successfully!", icon="✅")
        return True
    else:
        st.toast("Failed to load conversation", icon="❌")
        return False

# Function to clear conversation
def clear_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.toast("Conversation cleared", icon="🗑️")

# Function to get model recommendations
def get_model_recommendations():
    return st.session_state.app.get_model_recommendations()

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
        st.markdown("### Settings")
        
        # Model selection
        available_models = st.session_state.app.get_available_models()
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
        synthesis_available = st.session_state.app.is_synthesis_available()
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
        st.markdown("### History")
        if st.button("Save Conversation"):
            save_conversation()
        
        if st.button("Clear Conversation"):
            clear_conversation()
        
        # Model recommendations
        st.markdown("### Model Recommendations")
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
            <div style="text-align: center; padding: 2rem; color: rgba(224, 224, 224, 0.6);">
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
                    <div class="user-avatar avatar">👤</div>
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
                    <div class="assistant-avatar avatar">🤖</div>
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
                        asyncio.run(handle_file_upload(uploaded_file))
            
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
        user_input = st.text_area("Your message", height=100, key="user_input")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.button("Send", use_container_width=True)
        
        if send_button and user_input and not st.session_state.processing:
            asyncio.run(process_user_input(user_input))
            # Clear input after sending
            st.session_state.user_input = ""
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Performance metrics
        with st.expander("Performance Metrics"):
            metrics = st.session_state.app.get_performance_metrics()
            
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
            fallback_stats = st.session_state.app.get_fallback_statistics()
            for primary, fallbacks in fallback_stats.items():
                if fallbacks:
                    st.markdown(f"#### When {primary} fails:")
                    for fallback in fallbacks:
                        st.write(f"- {fallback['model']}: {fallback['success_rate']:.1f}")

# Run the app
if __name__ == "__main__":
    main()

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

# Custom CSS for professional and aesthetic UI
st.markdown("""
<style>
    /* Main theme colors and styling */
    :root {
        --primary-color: #6C63FF;
        --primary-light: rgba(108, 99, 255, 0.1);
        --primary-dark: #5A52D9;
        --secondary-color: #00BFA6;
        --secondary-light: rgba(0, 191, 166, 0.1);
        --background-color: #0F172A;
        --surface-color: #1E293B;
        --surface-light: #334155;
        --on-surface-color: #F8FAFC;
        --on-surface-secondary: #CBD5E1;
        --error-color: #EF4444;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --info-color: #3B82F6;
        --border-radius: 12px;
        --card-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --transition-speed: 0.3s;
        --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* General styling */
    html, body, [class*="css"] {
        font-family: var(--font-primary);
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--on-surface-color);
    }
    
    /* Streamlit component overrides */
    .stTextInput > div > div > input {
        background-color: var(--surface-color);
        color: var(--on-surface-color);
        border-radius: var(--border-radius);
        border: 1px solid var(--surface-light);
        padding: 1rem;
    }
    
    .stTextArea > div > div > textarea {
        background-color: var(--surface-color);
        color: var(--on-surface-color);
        border-radius: var(--border-radius);
        border: 1px solid var(--surface-light);
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: var(--border-radius);
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all var(--transition-speed);
    }
    
    .stButton > button:hover {
        background-color: var(--primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stCheckbox > div > label {
        color: var(--on-surface-color);
    }
    
    .stExpander > div > div > div > div > div > p {
        color: var(--on-surface-color);
    }
    
    .stSlider > div > div > div {
        color: var(--on-surface-color);
    }
    
    .stSlider > div > div > div > div > div > div {
        background-color: var(--primary-color);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJwYXR0ZXJuIiB4PSIwIiB5PSIwIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHBhdHRlcm5UcmFuc2Zvcm09InJvdGF0ZSgzMCkiPjxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjA1KSI+PC9yZWN0PjwvcGF0dGVybj48L2RlZnM+PHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNwYXR0ZXJuKSI+PC9yZWN0Pjwvc3ZnPg==');
        opacity: 0.3;
    }
    
    .main-header h1 {
        margin: 0;
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }
    
    .main-header-subtitle {
        color: white;
        opacity: 0.9;
        font-size: 1.1rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* Chat container styling */
    .chat-container {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--card-shadow);
        max-height: 650px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
    }
    
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: var(--surface-color);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: var(--surface-light);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* Message styling */
    .message {
        margin-bottom: 1.5rem;
        padding: 1rem;
        border-radius: var(--border-radius);
        position: relative;
        animation: fadeIn 0.3s ease-in-out;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message:hover {
        transform: translateY(-2px);
    }
    
    .user-message {
        background-color: var(--primary-light);
        border-left: 4px solid var(--primary-color);
        margin-left: 3rem;
        margin-right: 1rem;
    }
    
    .assistant-message {
        background-color: var(--secondary-light);
        border-left: 4px solid var(--secondary-color);
        margin-right: 3rem;
        margin-left: 1rem;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        color: var(--on-surface-secondary);
    }
    
    .message-sender {
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .message-timestamp {
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    .message-content {
        white-space: pre-wrap;
        line-height: 1.6;
        color: var(--on-surface-color);
    }
    
    /* Avatar styling */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        position: absolute;
        top: 1rem;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .user-avatar {
        left: -50px;
        background: linear-gradient(135deg, #6C63FF, #5A52D9);
    }
    
    .assistant-avatar {
        right: -50px;
        background: linear-gradient(135deg, #00BFA6, #00A896);
    }
    
    /* Input area styling */
    .input-area {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
    }
    
    .input-area::before {
        content: "";
        position: absolute;
        top: -2px;
        left: 5%;
        right: 5%;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
        border-radius: 100%;
    }
    
    /* Sidebar styling */
    .sidebar .stButton button {
        width: 100%;
        border-radius: var(--border-radius);
        margin-bottom: 0.75rem;
        background-color: var(--surface-light);
        color: var(--on-surface-color);
        border: none;
        transition: all var(--transition-speed);
    }
    
    .sidebar .stButton button:hover {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Section headers */
    .sidebar h3 {
        color: var(--on-surface-color);
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--surface-light);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--surface-color);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        padding: 0.75rem 1.25rem;
        border: none !important;
        color: var(--on-surface-secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-light);
        color: var(--primary-color) !important;
        font-weight: 600;
        border-bottom: 2px solid var(--primary-color) !important;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { transform: scale(0.8); opacity: 0.6; }
        50% { transform: scale(1); opacity: 1; }
        100% { transform: scale(0.8); opacity: 0.6; }
    }
    
    .loading-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1.5rem 0;
        gap: 0.5rem;
    }
    
    .loading-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        animation: pulse 1.5s infinite;
    }
    
    .loading-dot:nth-child(2) {
        animation-delay: 0.2s;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    
    .loading-dot:nth-child(3) {
        animation-delay: 0.4s;
        background: linear-gradient(135deg, var(--secondary-color), var(--secondary-color));
    }
    
    /* Feedback buttons */
    .feedback-buttons {
        display: flex;
        gap: 0.75rem;
        margin-top: 0.75rem;
        justify-content: flex-end;
    }
    
    .feedback-button {
        background: none;
        border: none;
        cursor: pointer;
        padding: 0.35rem 0.75rem;
        border-radius: var(--border-radius);
        transition: all var(--transition-speed);
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.9rem;
    }
    
    .feedback-button:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .feedback-button.positive {
        color: var(--success-color);
    }
    
    .feedback-button.negative {
        color: var(--error-color);
    }
    
    /* File upload area */
    .file-upload-area {
        border: 2px dashed rgba(108, 99, 255, 0.3);
        border-radius: var(--border-radius);
        padding: 2rem 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        transition: all var(--transition-speed);
        background-color: rgba(108, 99, 255, 0.05);
    }
    
    .file-upload-area:hover {
        border-color: var(--primary-color);
        background-color: rgba(108, 99, 255, 0.1);
    }
    
    /* File preview */
    .file-preview {
        background-color: var(--secondary-light);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--secondary-color);
    }
    
    .file-preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--on-surface-secondary);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        opacity: 0.8;
    }
    
    .empty-state-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .empty-state-subtitle {
        font-size: 1.1rem;
        opacity: 0.8;
        max-width: 500px;
        line-height: 1.6;
    }
    
    /* Stats cards */
    .stats-card {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-color);
        transition: all var(--transition-speed);
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow);
    }
    
    .stats-card-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: var(--on-surface-color);
    }
    
    .stats-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 992px) {
        .main-header {
            flex-direction: column;
            align-items: flex-start;
            padding: 1.25rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .user-message {
            margin-left: 1rem;
        }
        
        .assistant-message {
            margin-right: 1rem;
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            font-size: 1rem;
        }
        
        .user-avatar {
            left: -40px;
        }
        
        .assistant-avatar {
            right: -40px;
        }
    }
    
    @media (max-width: 768px) {
        .avatar {
            display: none;
        }
        
        .user-message, .assistant-message {
            margin-left: 0;
            margin-right: 0;
        }
        
        .chat-container {
            padding: 1rem;
        }
        
        .message {
            padding: 0.75rem;
        }
    }
    
    /* Code blocks */
    code {
        font-family: 'JetBrains Mono', monospace;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-size: 0.9em;
    }
    
    pre {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1em;
        border-radius: var(--border-radius);
        overflow-x: auto;
        border-left: 3px solid var(--primary-color);
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
        font-size: 0.9em;
        color: var(--on-surface-color);
    }
    
    /* Syntax highlighting */
    .token.comment,
    .token.prolog,
    .token.doctype,
    .token.cdata {
        color: #6c7a89;
    }
    
    .token.punctuation {
        color: #f8f8f2;
    }
    
    .namespace {
        opacity: 0.7;
    }
    
    .token.property,
    .token.tag,
    .token.constant,
    .token.symbol,
    .token.deleted {
        color: #ff79c6;
    }
    
    .token.boolean,
    .token.number {
        color: #bd93f9;
    }
    
    .token.selector,
    .token.attr-name,
    .token.string,
    .token.char,
    .token.builtin,
    .token.inserted {
        color: #50fa7b;
    }
    
    .token.operator,
    .token.entity,
    .token.url,
    .language-css .token.string,
    .style .token.string {
        color: #f8f8f2;
    }
    
    .token.atrule,
    .token.attr-value,
    .token.keyword {
        color: #8be9fd;
    }
    
    .token.function,
    .token.class-name {
        color: #ffb86c;
    }
    
    .token.regex,
    .token.important,
    .token.variable {
        color: #f1fa8c;
    }
    
    .token.important,
    .token.bold {
        font-weight: bold;
    }
    
    .token.italic {
        font-style: italic;
    }
    
    .token.entity {
        cursor: help;
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
        <div class="main-header-subtitle">
            Harness the power of multiple AI models in one elegant interface
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
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-card-title">Best Overall Model</div>
                <div class="stats-card-value">{best_model}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Categories with recommendations
        for category, models in recommendations.items():
            if category != "overall_best" and models:
                with st.expander(f"{category.capitalize()} Queries"):
                    for model_data in models:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>{model_data['model']}</span>
                            <span style="color: var(--primary-color); font-weight: 600;">{model_data.get('score', 0):.1f}</span>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-title">Start a Conversation</div>
                <div class="empty-state-subtitle">
                    Ask anything and get responses from multiple AI models. 
                    Compare different perspectives or get a synthesized answer.
                </div>
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
                        <div class="message-sender">You</div>
                        <div class="message-timestamp">{timestamp}</div>
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
                        <div class="message-sender">Assistant{model_display}</div>
                        <div class="message-timestamp">{timestamp}</div>
                    </div>
                    <div class="message-content">{content}</div>
                    <div class="feedback-buttons">
                        <button class="feedback-button positive" onclick="handleFeedback('{message_id}', '{model}', true)">
                            <span>👍</span> Helpful
                        </button>
                        <button class="feedback-button negative" onclick="handleFeedback('{message_id}', '{model}', false)">
                            <span>👎</span> Not helpful
                        </button>
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
        user_input = st.text_area("Your message", height=100, key="user_input", placeholder="Type your message here...")
        
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
            metrics = {}
            try:
                if 'app' in st.session_state and hasattr(st.session_state.app, 'get_performance_metrics'):
                    metrics = st.session_state.app.get_performance_metrics()
            except Exception as e:
                st.error(f"Error getting performance metrics: {str(e)}")
            
            if "overall" in metrics:
                st.markdown("#### Overall")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">Total Requests</div>
                        <div class="stats-card-value">{metrics['overall']['total_requests']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">Success Rate</div>
                        <div class="stats-card-value">{metrics['overall']['success_rate']:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-card-title">Avg Response Time</div>
                    <div class="stats-card-value">{metrics['overall']['average_response_time']:.2f}s</div>
                </div>
                """, unsafe_allow_html=True)
            
            if "cache" in metrics:
                st.markdown("#### Cache")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">Active Entries</div>
                        <div class="stats-card-value">{metrics['cache'].get('active_entries', 0)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">Hit Rate</div>
                        <div class="stats-card-value">{metrics['cache'].get('hit_rate', 0):.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Model performance
        with st.expander("Model Performance"):
            if "models" in metrics:
                for model, model_metrics in metrics["models"].items():
                    st.markdown(f"#### {model}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-card-title">Requests</div>
                            <div class="stats-card-value">{model_metrics['requests']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-card-title">Success</div>
                            <div class="stats-card-value">{model_metrics['success_rate']:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-card-title">Avg Time</div>
                        <div class="stats-card-value">{model_metrics['average_response_time']:.2f}s</div>
                    </div>
                    """, unsafe_allow_html=True)
        
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
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stats-card-title">{fallback['model']}</div>
                            <div class="stats-card-value">{fallback['success_rate']:.1f}</div>
                        </div>
                        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()

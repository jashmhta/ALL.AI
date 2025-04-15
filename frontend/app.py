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

# Custom CSS for GenSpark style with black and grey theme
st.markdown("""
<style>
    /* Main theme colors and styling */
    :root {
        --background-color: #121212;
        --surface-color: #1E1E1E;
        --card-color: #252525;
        --text-color: #FFFFFF;
        --secondary-text-color: #AAAAAA;
        --accent-color: #00A3FF;
        --border-radius: 12px;
        --message-border-radius: 18px;
        --card-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* General styling */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Streamlit component overrides */
    .stTextInput > div > div > input {
        background-color: var(--surface-color);
        color: var(--text-color);
        border-radius: var(--border-radius);
        border: 1px solid #333;
        padding: 12px;
    }
    
    .stTextArea > div > div > textarea {
        background-color: var(--surface-color);
        color: var(--text-color);
        border-radius: var(--border-radius);
        border: 1px solid #333;
        padding: 12px;
        font-size: 16px;
        min-height: 120px;
    }
    
    .stButton > button {
        background-color: var(--accent-color);
        color: var(--text-color);
        border-radius: var(--border-radius);
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #0088cc;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
    }
    
    .main-header h1 {
        margin: 0;
        color: var(--text-color);
        font-size: 1.8rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .main-header h1 img {
        width: 32px;
        height: 32px;
    }
    
    /* Chat container styling */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 20px;
        max-height: 600px;
        overflow-y: auto;
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        margin-bottom: 20px;
    }
    
    /* Message styling - GenSpark style */
    .message-row {
        display: flex;
        width: 100%;
        margin-bottom: 16px;
    }
    
    .message-row.user {
        justify-content: flex-end;
    }
    
    .message-row.assistant {
        justify-content: flex-start;
    }
    
    .message {
        max-width: 80%;
        padding: 16px;
        border-radius: var(--message-border-radius);
        position: relative;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background-color: #2A2A2A;
        color: var(--text-color);
        border-radius: var(--message-border-radius);
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message {
        background-color: var(--card-color);
        color: var(--text-color);
        border-radius: var(--message-border-radius);
        border-bottom-left-radius: 4px;
    }
    
    .message-content {
        white-space: pre-wrap;
        line-height: 1.6;
        font-size: 15px;
    }
    
    /* Copy button */
    .copy-button {
        display: inline-block;
        padding: 4px 10px;
        background-color: rgba(0, 0, 0, 0.2);
        color: var(--secondary-text-color);
        border-radius: 4px;
        font-size: 12px;
        margin-top: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .copy-button:hover {
        background-color: rgba(0, 0, 0, 0.4);
        color: var(--text-color);
    }
    
    /* Mixture of Agents section */
    .mixture-header {
        font-size: 18px;
        font-weight: bold;
        margin-top: 28px;
        margin-bottom: 16px;
        color: var(--text-color);
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .model-card {
        background-color: var(--card-color);
        border-radius: var(--border-radius);
        padding: 16px;
        margin-bottom: 16px;
        position: relative;
        box-shadow: var(--card-shadow);
        border-left: 4px solid transparent;
        transition: all 0.2s ease;
    }
    
    .model-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    .model-card.gpt {
        border-left-color: #10A37F;
    }
    
    .model-card.claude {
        border-left-color: #9C5FFF;
    }
    
    .model-card.gemini {
        border-left-color: #4285F4;
    }
    
    .model-card.llama {
        border-left-color: #00E8FC;
    }
    
    .model-card.openrouter {
        border-left-color: #FF6B6B;
    }
    
    .model-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    
    .model-icon {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        background-color: #333;
        color: white;
        font-weight: bold;
    }
    
    .model-icon.gpt {
        background-color: #10A37F;
    }
    
    .model-icon.claude {
        background-color: #9C5FFF;
    }
    
    .model-icon.gemini {
        background-color: #4285F4;
    }
    
    .model-icon.llama {
        background-color: #00E8FC;
        color: #000;
    }
    
    .model-icon.openrouter {
        background-color: #FF6B6B;
    }
    
    .model-name {
        font-weight: bold;
        font-size: 16px;
    }
    
    .model-content {
        font-size: 15px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    .model-indicator {
        position: absolute;
        top: 16px;
        left: -8px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #00A3FF;
    }
    
    .dismiss-button {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .dismiss-button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Input area styling */
    .input-area {
        display: flex;
        align-items: center;
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 12px;
        margin-top: 20px;
        border: 1px solid #333;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
    }
    
    .input-area:focus-within {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 2px rgba(0, 163, 255, 0.2);
    }
    
    .input-box {
        flex-grow: 1;
        background-color: transparent;
        border: none;
        color: var(--text-color);
        padding: 10px;
        outline: none;
        font-size: 16px;
        resize: none;
        min-height: 60px;
    }
    
    .send-button {
        background-color: var(--accent-color);
        border: none;
        color: var(--text-color);
        cursor: pointer;
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .send-button:hover {
        background-color: #0088cc;
        transform: translateY(-2px);
    }
    
    .send-button svg {
        width: 16px;
        height: 16px;
    }
    
    /* Thinking indicator */
    .thinking-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        margin: 12px 0;
        color: var(--secondary-text-color);
        font-size: 15px;
        animation: fadeIn 0.5s ease;
    }
    
    .thinking-dot {
        width: 8px;
        height: 8px;
        background-color: var(--secondary-text-color);
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    
    .thinking-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .thinking-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes pulse {
        0% { opacity: 0.3; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0.3; transform: scale(0.8); }
    }
    
    /* Model selector */
    .model-selector {
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
    }
    
    .model-option {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .model-option:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    .model-radio {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        border: 2px solid #555;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .model-radio.selected {
        border-color: var(--accent-color);
    }
    
    .model-radio.selected::after {
        content: "";
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: var(--accent-color);
        animation: scaleIn 0.2s ease;
    }
    
    @keyframes scaleIn {
        from { transform: scale(0); }
        to { transform: scale(1); }
    }
    
    /* Code blocks */
    pre {
        background-color: #1A1A1A;
        border-radius: 8px;
        padding: 16px;
        overflow-x: auto;
        margin: 12px 0;
        border: 1px solid #333;
    }
    
    code {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .keyword {
        color: #CF99FF;
    }
    
    .function {
        color: #61AFEF;
    }
    
    .string {
        color: #98C379;
    }
    
    .comment {
        color: #7F848E;
    }
    
    .number {
        color: #D19A66;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: var(--secondary-text-color);
        background-color: var(--surface-color);
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
    }
    
    .empty-state h3 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
        color: var(--text-color);
    }
    
    .empty-state p {
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Sidebar styling */
    .sidebar .stButton button {
        width: 100%;
        margin-bottom: 12px;
    }
    
    /* File upload styling */
    .uploadedFile {
        background-color: var(--card-color);
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .uploadedFile .icon {
        color: var(--accent-color);
    }
    
    .uploadedFile .info {
        flex-grow: 1;
    }
    
    .uploadedFile .name {
        font-weight: 500;
    }
    
    .uploadedFile .size {
        font-size: 12px;
        color: var(--secondary-text-color);
    }
    
    .uploadedFile .remove {
        color: #FF5555;
        cursor: pointer;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .message {
            max-width: 90%;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .model-card {
            padding: 12px;
        }
    }
    
    /* Animations */
    @keyframes slideInRight {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .message-row.user .message {
        animation: slideInRight 0.3s ease-out;
    }
    
    .message-row.assistant .message {
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* Memory display styling */
    .memory-container {
        background-color: var(--card-color);
        border-radius: var(--border-radius);
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
    }
    
    .memory-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .memory-title {
        font-weight: bold;
        font-size: 16px;
        color: var(--text-color);
    }
    
    .memory-controls {
        display: flex;
        gap: 8px;
    }
    
    .memory-control {
        background-color: rgba(255, 255, 255, 0.1);
        border: none;
        color: var(--secondary-text-color);
        width: 24px;
        height: 24px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .memory-control:hover {
        background-color: rgba(255, 255, 255, 0.2);
        color: var(--text-color);
    }
    
    .memory-item {
        padding: 8px;
        border-radius: 4px;
        margin-bottom: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        font-size: 14px;
        line-height: 1.4;
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    
    .memory-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .memory-item.user {
        border-left: 2px solid #10A37F;
    }
    
    .memory-item.assistant {
        border-left: 2px solid #9C5FFF;
    }
    
    .memory-item-content {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .memory-item-expanded .memory-item-content {
        white-space: normal;
    }
    
    .memory-item-toggle {
        position: absolute;
        right: 8px;
        top: 8px;
        background: none;
        border: none;
        color: var(--secondary-text-color);
        cursor: pointer;
        font-size: 12px;
    }
    
    .memory-item-toggle:hover {
        color: var(--text-color);
    }
    
    .memory-empty {
        text-align: center;
        padding: 16px;
        color: var(--secondary-text-color);
        font-style: italic;
    }
    
    /* Mixture-of-Agents styling - GenSpark style */
    .mixture-container {
        margin-top: 24px;
    }
    
    .mixture-models {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 16px;
    }
    
    .mixture-model-button {
        background-color: var(--card-color);
        border: 1px solid #333;
        border-radius: 20px;
        padding: 6px 12px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .mixture-model-button:hover {
        background-color: #333;
    }
    
    .mixture-model-button.selected {
        background-color: rgba(0, 163, 255, 0.2);
        border-color: var(--accent-color);
    }
    
    .mixture-model-icon {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
    }
    
    .mixture-responses {
        margin-top: 16px;
    }
    
    .reflection-section {
        background-color: #1A1A1A;
        border-radius: var(--border-radius);
        padding: 16px;
        margin-top: 16px;
        border-left: 4px solid #9C5FFF;
    }
    
    .reflection-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: bold;
        color: #9C5FFF;
    }
    
    .reflection-content {
        font-size: 14px;
        line-height: 1.6;
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

if 'mixture_responses' not in st.session_state:
    st.session_state.mixture_responses = {}

if 'memory_items' not in st.session_state:
    st.session_state.memory_items = []

if 'memory_expanded' not in st.session_state:
    st.session_state.memory_expanded = {}

if 'selected_models' not in st.session_state:
    st.session_state.selected_models = []

# Function to add a message to the chat
def add_message(role, content, model=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    message_id = str(uuid.uuid4())
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "model": model,
        "id": message_id
    })
    
    # Add to memory items (truncated version)
    if len(content) > 100:
        memory_content = content[:100] + "..."
    else:
        memory_content = content
        
    st.session_state.memory_items.append({
        "role": role,
        "content": memory_content,
        "full_content": content,
        "timestamp": timestamp,
        "model": model,
        "id": message_id
    })
    
    return message_id

# Function to process user input
def process_user_input(user_input):
    if not user_input.strip():
        return
    
    # Add user message to chat
    add_message("user", user_input)
    
    # Set processing flag
    st.session_state.processing = True
    
    try:
        # Get selected models
        selected_models = st.session_state.selected_models
        
        # Check if we should get responses from all models
        use_multiple = len(selected_models) > 0
        
        # Check if we should synthesize responses
        synthesize = st.session_state.get('synthesize', True) and use_multiple
        
        # Process the prompt
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(st.session_state.app.process_prompt(
            prompt=user_input,
            model=None if use_multiple else st.session_state.get('selected_model', None),
            use_multiple=use_multiple,
            synthesize=synthesize,
            conversation_id=st.session_state.conversation_id,
            user_id=st.session_state.user_id,
            file_path=st.session_state.uploaded_file_path
        ))
        
        # Store mixture responses
        if use_multiple:
            st.session_state.mixture_responses = {}
            
            # Add individual responses to mixture
            for resp in response.get("responses", []):
                if resp.get("success", False):
                    st.session_state.mixture_responses[resp["model"]] = resp["text"]
            
            # Add synthesis if available
            if synthesize and "synthesis" in response and response["synthesis"]["success"]:
                # Add synthesized response to chat
                synthesis_id = add_message(
                    "assistant", 
                    response["synthesis"]["text"], 
                    f"Synthesis"
                )
                
                # Add reflection about the synthesis
                reflection = generate_reflection(response["responses"], response["synthesis"])
                st.session_state.mixture_responses["reflection"] = reflection
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
        
        # Clear uploaded file after use
        st.session_state.uploaded_file_path = None
        st.session_state.uploaded_file_info = None

# Function to generate reflection about the synthesis
def generate_reflection(responses, synthesis):
    successful_responses = [r for r in responses if r.get("success", False)]
    
    if not successful_responses or not synthesis.get("success", False):
        return "No successful responses to analyze."
    
    # Create a simple reflection
    reflection = "Analysis of AI responses:\n\n"
    
    # Compare response lengths
    lengths = {r["model"]: len(r["text"]) for r in successful_responses}
    avg_length = sum(lengths.values()) / len(lengths)
    
    reflection += f"- Response lengths: "
    for model, length in lengths.items():
        reflection += f"{model} ({length} chars), "
    reflection = reflection[:-2] + f" (avg: {int(avg_length)} chars)\n"
    
    # Identify common themes
    reflection += "- Common elements across responses:\n"
    
    # Simple keyword extraction (in a real app, this would use NLP)
    common_keywords = ["code", "function", "error", "data", "file", "example", "solution"]
    for keyword in common_keywords:
        count = sum(1 for r in successful_responses if keyword.lower() in r["text"].lower())
        if count > len(successful_responses) / 2:
            reflection += f"  * '{keyword}' mentioned in {count}/{len(successful_responses)} responses\n"
    
    # Strengths and weaknesses
    reflection += "\n- Model strengths:\n"
    reflection += "  * GPT models: Detailed explanations and code examples\n"
    reflection += "  * Claude models: Thorough analysis and safety considerations\n"
    reflection += "  * Gemini models: Concise responses with practical solutions\n"
    
    return reflection

# Function to handle file upload
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            # Create a temporary file
            file_path = os.path.join("/tmp", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Store file info
            st.session_state.uploaded_file_path = file_path
            st.session_state.uploaded_file_info = {
                "name": uploaded_file.name,
                "size": uploaded_file.size,
                "type": uploaded_file.type
            }
            
            return True, f"File uploaded: {uploaded_file.name}"
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
        # Create a JSON file with the conversation
        conversation_data = {
            "id": st.session_state.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages
        }
        
        # Save to file
        file_path = f"/tmp/conversation_{st.session_state.conversation_id}.json"
        with open(file_path, "w") as f:
            json.dump(conversation_data, f, indent=2)
        
        # Provide download link
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        b64_content = base64.b64encode(file_content).decode()
        download_filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        href = f'<a href="data:application/json;base64,{b64_content}" download="{download_filename}">Download Conversation</a>'
        
        st.sidebar.markdown(href, unsafe_allow_html=True)
        st.toast("Conversation saved successfully!", icon="✅")
        
        return True
    except Exception as e:
        st.toast(f"Error saving conversation: {str(e)}", icon="❌")
        return False

# Function to clear conversation
def clear_conversation():
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.memory_items = []
    st.session_state.memory_expanded = {}
    st.session_state.mixture_responses = {}
    st.toast("Conversation cleared", icon="🗑️")

# Function to toggle memory item expansion
def toggle_memory_item(item_id):
    if item_id in st.session_state.memory_expanded:
        st.session_state.memory_expanded[item_id] = not st.session_state.memory_expanded[item_id]
    else:
        st.session_state.memory_expanded[item_id] = True

# Function to get model icon
def get_model_icon(model):
    model_lower = model.lower() if model else ""
    
    if "gpt" in model_lower or "openai" in model_lower:
        return "G", "gpt"
    elif "claude" in model_lower or "anthropic" in model_lower:
        return "C", "claude"
    elif "gemini" in model_lower or "google" in model_lower:
        return "G", "gemini"
    elif "llama" in model_lower:
        return "L", "llama"
    elif "openrouter" in model_lower:
        return "O", "openrouter"
    elif "huggingface" in model_lower:
        return "H", "huggingface"
    elif "synthesis" in model_lower:
        return "S", "synthesis"
    else:
        return "AI", ""

# Function to toggle model selection
def toggle_model_selection(model):
    if model in st.session_state.selected_models:
        st.session_state.selected_models.remove(model)
    else:
        st.session_state.selected_models.append(model)

# Main layout
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 ALL.AI - Multi-AI Chat Interface</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Mixture-of-Agents")
        
        # Get available models
        available_models = []
        try:
            if 'app' in st.session_state and hasattr(st.session_state.app, 'get_available_models'):
                available_models = st.session_state.app.get_available_models()
        except Exception as e:
            st.error(f"Error getting available models: {str(e)}")
        
        # Model selection
        if available_models:
            st.markdown("Select AI models to use:")
            
            cols = st.columns(2)
            for i, model in enumerate(available_models):
                col = cols[i % 2]
                icon_text, icon_class = get_model_icon(model)
                
                # Create a custom checkbox with model icon
                is_selected = model in st.session_state.selected_models
                checkbox_label = f'<div class="model-option">'
                checkbox_label += f'<div class="model-radio {"selected" if is_selected else ""}">'
                if is_selected:
                    checkbox_label += f'<div class="model-radio-inner"></div>'
                checkbox_label += f'</div>'
                checkbox_label += f'<div class="model-icon {icon_class}">{icon_text}</div>'
                checkbox_label += f'<div class="model-name">{model}</div>'
                checkbox_label += f'</div>'
                
                if col.checkbox(model, value=is_selected, key=f"model_{model}"):
                    if model not in st.session_state.selected_models:
                        st.session_state.selected_models.append(model)
                else:
                    if model in st.session_state.selected_models:
                        st.session_state.selected_models.remove(model)
            
            # Single model selection if no mixture
            if not st.session_state.selected_models:
                st.markdown("### Single Model Mode")
                st.session_state.selected_model = st.selectbox(
                    "Select a single AI model", 
                    ["Auto"] + available_models,
                    index=0
                )
                if st.session_state.selected_model == "Auto":
                    st.session_state.selected_model = None
            else:
                # Synthesis option
                synthesis_available = False
                try:
                    if 'app' in st.session_state and hasattr(st.session_state.app, 'is_synthesis_available'):
                        synthesis_available = st.session_state.app.is_synthesis_available()
                except Exception as e:
                    st.error(f"Error checking synthesis availability: {str(e)}")
                    
                if synthesis_available:
                    st.session_state.synthesize = st.checkbox("Synthesize responses", value=True)
                else:
                    st.info("Synthesis requires Llama API key")
                    st.session_state.synthesize = False
        else:
            st.error("No AI models available. Please check your API keys.")
        
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
    
    # Main chat area
    col1, col2 = st.columns([7, 3])
    
    with col1:
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
                <h3>👋 Welcome to ALL.AI</h3>
                <p>Start a conversation with multiple AI models or select specific models from the sidebar.</p>
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
                <div class="message-row user">
                    <div class="message user-message">
                        <div class="message-header">
                            <span>You</span>
                            <span>{timestamp}</span>
                        </div>
                        <div class="message-content">{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                icon_text, icon_class = get_model_icon(model)
                model_display = f"{model}" if model else "Assistant"
                
                st.markdown(f"""
                <div class="message-row assistant">
                    <div class="message assistant-message">
                        <div class="message-header">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div class="model-icon {icon_class}">{icon_text}</div>
                                <span>{model_display}</span>
                            </div>
                            <span>{timestamp}</span>
                        </div>
                        <div class="message-content">{content}</div>
                        <div class="feedback-buttons">
                            <button class="feedback-button positive" onclick="handleFeedback('{message_id}', '{model}', true)">👍</button>
                            <button class="feedback-button negative" onclick="handleFeedback('{message_id}', '{model}', false)">👎</button>
                            <button class="copy-button" onclick="copyToClipboard('{message_id}')">Copy</button>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add JavaScript for feedback handling and copy functionality
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
        
        function copyToClipboard(messageId) {
            // Find the message content
            const messageElement = document.querySelector(`[data-message-id="${messageId}"] .message-content`);
            if (messageElement) {
                const text = messageElement.innerText;
                navigator.clipboard.writeText(text)
                    .then(() => {
                        // Show a temporary "Copied!" message
                        const copyButton = document.querySelector(`[data-message-id="${messageId}"] .copy-button`);
                        if (copyButton) {
                            const originalText = copyButton.innerText;
                            copyButton.innerText = "Copied!";
                            setTimeout(() => {
                                copyButton.innerText = originalText;
                            }, 2000);
                        }
                    })
                    .catch(err => {
                        console.error('Failed to copy: ', err);
                    });
            }
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Display loading indicator if processing
        if st.session_state.processing:
            st.markdown("""
            <div class="thinking-indicator">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <span>Thinking...</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display mixture responses if available
        if st.session_state.mixture_responses:
            st.markdown('<div class="mixture-container">', unsafe_allow_html=True)
            st.markdown('<div class="mixture-header">Individual AI Responses</div>', unsafe_allow_html=True)
            
            for model, response in st.session_state.mixture_responses.items():
                if model == "reflection":
                    continue
                    
                icon_text, icon_class = get_model_icon(model)
                
                st.markdown(f"""
                <div class="model-card {icon_class}">
                    <div class="model-header">
                        <div class="model-icon {icon_class}">{icon_text}</div>
                        <div class="model-name">{model}</div>
                    </div>
                    <div class="model-content">{response}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display reflection if available
            if "reflection" in st.session_state.mixture_responses:
                st.markdown(f"""
                <div class="reflection-section">
                    <div class="reflection-header">
                        <span>🔍</span>
                        <span>Reflection</span>
                    </div>
                    <div class="reflection-content">{st.session_state.mixture_responses["reflection"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # File upload area
        with st.expander("Upload a file for analysis"):
            uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "csv", "md", "py", "js", "html", "json", "xml"])
            
            if uploaded_file:
                if st.button("Process File"):
                    with st.spinner("Processing file..."):
                        success, message = handle_file_upload(uploaded_file)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            
            # Display file info if available
            if st.session_state.uploaded_file_info:
                file_info = st.session_state.uploaded_file_info
                st.markdown(f"""
                <div class="uploadedFile">
                    <div class="icon">📄</div>
                    <div class="info">
                        <div class="name">{file_info['name']}</div>
                        <div class="size">{file_info['size']} bytes</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Input area
        st.text_area("Your message", key="user_input", height=100)
        
        if st.button("Send", use_container_width=True):
            if st.session_state.user_input and not st.session_state.processing:
                process_user_input(st.session_state.user_input)
                st.session_state.user_input = ""
    
    with col2:
        # Memory display
        st.markdown('<div class="memory-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="memory-header">
            <div class="memory-title">Memory</div>
            <div class="memory-controls">
                <button class="memory-control" title="Clear Memory" onclick="clearMemory()">🗑️</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.memory_items:
            st.markdown('<div class="memory-empty">No conversation history yet.</div>', unsafe_allow_html=True)
        else:
            for i, item in enumerate(st.session_state.memory_items):
                item_id = f"memory_{i}"
                is_expanded = st.session_state.memory_expanded.get(item_id, False)
                
                # Create memory item
                st.markdown(f"""
                <div class="memory-item {item['role']} {'memory-item-expanded' if is_expanded else ''}" id="{item_id}">
                    <div class="memory-item-content">
                        {item['full_content'] if is_expanded else item['content']}
                    </div>
                    <button class="memory-item-toggle" onclick="toggleMemory('{item_id}')">
                        {'-' if is_expanded else '+'}
                    </button>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add JavaScript for memory interactions
        st.markdown("""
        <script>
        function toggleMemory(itemId) {
            // Use Streamlit's postMessage to communicate with Python
            window.parent.postMessage({
                type: "streamlit:toggleMemory",
                itemId: itemId
            }, "*");
        }
        
        function clearMemory() {
            // Use Streamlit's postMessage to communicate with Python
            window.parent.postMessage({
                type: "streamlit:clearMemory"
            }, "*");
        }
        </script>
        """, unsafe_allow_html=True)
        
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
        
        # About section
        with st.expander("About ALL.AI"):
            st.markdown("""
            **ALL.AI** is a Multi-AI Chat Interface that allows you to interact with multiple AI models simultaneously.
            
            Features:
            - Chat with multiple AI models at once
            - Compare responses from different models
            - Synthesize responses for a comprehensive answer
            - Upload files for AI analysis
            - Track conversation memory
            
            This application was developed to provide a seamless experience for interacting with various AI models through a unified interface.
            """)

# Handle custom events from JavaScript
def handle_custom_events():
    # Get the session state
    session_state = st.session_state
    
    # Check for custom events in the query parameters
    query_params = st.experimental_get_query_params()
    
    # Handle feedback event
    if "feedback" in query_params:
        feedback_data = json.loads(query_params["feedback"][0])
        handle_feedback(
            feedback_data["messageId"],
            feedback_data["model"],
            feedback_data["isPositive"]
        )
        # Clear the query parameters
        st.experimental_set_query_params()
    
    # Handle memory toggle event
    if "toggleMemory" in query_params:
        item_id = query_params["toggleMemory"][0]
        toggle_memory_item(item_id)
        # Clear the query parameters
        st.experimental_set_query_params()
    
    # Handle clear memory event
    if "clearMemory" in query_params:
        session_state.memory_items = []
        session_state.memory_expanded = {}
        # Clear the query parameters
        st.experimental_set_query_params()

# Run the app
if __name__ == "__main__":
    # Handle custom events
    handle_custom_events()
    
    # Run the main app
    main()

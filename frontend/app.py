import streamlit as st
import asyncio
import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path to import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MultiAIApp from the backend
from backend.main import MultiAIApp

# Initialize session state variables if they don't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'app' not in st.session_state:
    st.session_state.app = MultiAIApp()

# Function to save chat history
def save_chat_history():
    if st.session_state.messages:
        history_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history")
        os.makedirs(history_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        filepath = os.path.join(history_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(st.session_state.messages, f, indent=2)
        
        st.toast(f"Chat history saved to {filename}")

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = []
    st.toast("Chat history cleared")

# App title and description
st.title("Multi-AI Chat Application")
st.markdown("""
This application allows you to interact with multiple AI models through a unified interface.
Choose a specific AI model or let the system automatically select the best available model.
""")

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background-color: #1E1E1E;
        color: #FAFAFA;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #252526;
    }
    
    /* Input fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #333333;
        color: #FAFAFA;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #444444;
        color: #FAFAFA;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2D2D2D;
    }
    
    /* User messages */
    .stChatMessageContent[data-testid="UserChatMessage"] {
        background-color: #0E639C;
    }
    
    /* Assistant messages */
    .stChatMessageContent[data-testid="AssistantChatMessage"] {
        background-color: #2D2D2D;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with model selection and options
with st.sidebar:
    st.header("Settings")
    
    # Get available models
    available_models = st.session_state.app.get_available_models()
    
    if available_models:
        selected_model = st.selectbox(
            "Choose AI Model",
            ["Auto (with fallback)"] + available_models,
            index=0
        )
        
        use_multiple = st.checkbox("Get responses from all available models", value=False)
        
        # Advanced options
        with st.expander("Advanced Options"):
            temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            max_tokens = st.slider("Max Tokens", min_value=50, max_value=4000, value=1000, step=50)
        
        # History management
        st.header("History")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save History"):
                save_chat_history()
        with col2:
            if st.button("Clear History"):
                clear_chat_history()
    else:
        st.error("No AI models available. Please check your API keys in the .env file.")
        selected_model = None
        use_multiple = False

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "model" in message and message["model"] != "user":
            st.caption(f"Model: {message['model']}")

# Chat input
if available_models:
    prompt = st.chat_input("What would you like to ask?")
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt, "model": "user"})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Process the model selection
                model_param = None if selected_model == "Auto (with fallback)" else selected_model
                
                # Set up the parameters
                params = {
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                # Get response(s) from the AI model(s)
                if use_multiple:
                    # Get responses from all models
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        st.session_state.app.process_prompt(
                            prompt, 
                            use_multiple=True,
                            **params
                        )
                    )
                    
                    # Display all responses
                    for i, response in enumerate(result["responses"]):
                        if response["success"]:
                            st.markdown(f"**{response['model']}**:")
                            st.markdown(response["text"])
                            if i < len(result["responses"]) - 1:
                                st.divider()
                            
                            # Add each response to chat history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": response["text"],
                                "model": response["model"]
                            })
                else:
                    # Get response from selected model
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        st.session_state.app.process_prompt(
                            prompt, 
                            model=model_param,
                            **params
                        )
                    )
                    
                    if response["success"]:
                        st.markdown(response["text"])
                        st.caption(f"Model: {response['model']}")
                        
                        # Add response to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response["text"],
                            "model": response["model"]
                        })
                    else:
                        st.error(response["text"])
else:
    st.warning("Please configure at least one AI API key in the .env file to use this application.")

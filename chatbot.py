
import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Groq AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found. Check your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        }
    ]

# Sidebar
with st.sidebar:
    st.title("Settings")

    model = st.selectbox(
        "Select Model",
        [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b"
        ]
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            }
        ]
        st.rerun()

# Main interface
st.title("🤖 Groq AI Chatbot")
st.caption("Powered by Groq API")

# Display conversation history
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask me anything...")

if user_input:

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate AI response
    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=1024,
                stream=True
            )

            bot_reply = ""

            for chunk in response:
                content = chunk.choices[0].delta.content

                if content:
                    bot_reply += content
                    response_placeholder.markdown(bot_reply + "▌")

            response_placeholder.markdown(bot_reply)

            # Save assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_reply
            })

        except Exception as e:
            st.error(f"Error: {e}")

            # Remove failed user message
            st.session_state.messages.pop()

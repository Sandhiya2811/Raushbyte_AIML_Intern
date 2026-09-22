import sys
from pathlib import Path

# Ensure the src/ folder is importable when launched via Streamlit
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

import llm
from assistant import handle_user_message
from config import ALLOWED_WEBSITES, HISTORY_LIMIT, OLLAMA_MODEL

st.set_page_config(page_title="Smart AI Assistant", page_icon="🤖",
                   layout="centered")

st.title("🤖 Smart AI Assistant")
st.caption("An LLM-powered conversational assistant with safe "
           "Python-based task tools — RaushByte Technologies AI/ML "
           "Internship, Level 3 – Task 1")

# --- Session state ---------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "client" not in st.session_state:
    st.session_state.client = llm.create_client()
if "status" not in st.session_state:
    _, status = llm.check_connection(st.session_state.client)
    st.session_state.status = status


def _render(text: str) -> None:
    """Render a reply, preserving single line breaks."""
    st.markdown(text.replace("\n", "  \n"))


# --- Sidebar ----------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    st.text_input("Model (from .env)", value=OLLAMA_MODEL, disabled=True)
    st.caption(f"Conversation memory: last {HISTORY_LIMIT} messages")

    st.subheader("Model status")
    st.info(st.session_state.status)
    if st.button("Re-check connection"):
        _, status = llm.check_connection(st.session_state.client)
        st.session_state.status = status
        st.rerun()

    if st.button("Clear conversation"):
        st.session_state.history = []
        st.rerun()

    st.subheader("Available tools")
    st.markdown("- Current time / date\n"
                "- Open approved websites\n"
                "- Web search (opens the browser)\n"
                "- Create / read / list notes")
    st.caption("Approved websites: " + ", ".join(ALLOWED_WEBSITES))

# --- Chat -------------------------------------------------------------
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        _render(message["content"])

user_input = st.chat_input(
    "Ask a question or give a command (e.g., 'what is machine learning?' "
    "or 'open github')")

if user_input:
    with st.chat_message("user"):
        _render(user_input)

    reply, should_exit = handle_user_message(
        user_input, st.session_state.client, st.session_state.history)

    with st.chat_message("assistant"):
        _render(reply)

    if should_exit:
        # Keep the farewell visible, then start a fresh conversation
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "content": reply})
        st.info("Session ended — type a new message to start again.")
        st.session_state.history = []
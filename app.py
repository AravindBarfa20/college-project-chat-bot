import os
from typing import List, Dict

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = "llama-3.1-70b-versatile"
SYSTEM_PROMPT = "You are a Helpful College Project Assistant."


def initialize_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def get_api_key() -> str:
    env_api_key = os.getenv("GROQ_API_KEY", "").strip()
    sidebar_api_key = st.sidebar.text_input(
        "Groq API Key",
        value=env_api_key,
        type="password",
        placeholder="gsk_...",
        help="Enter your Groq API key here or set it as the GROQ_API_KEY environment variable.",
    ).strip()
    return sidebar_api_key or env_api_key


def build_conversation(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}, *messages]


def get_assistant_response(client: Groq, messages: List[Dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=build_conversation(messages),
        temperature=0.7,
        max_completion_tokens=1024,
    )
    return response.choices[0].message.content or "I couldn't generate a response."


def main() -> None:
    st.set_page_config(page_title="College Project Assistant", page_icon="🎓", layout="centered")
    initialize_session_state()

    st.title("College Project Assistant")
    st.caption("A Streamlit chatbot powered by Groq and Llama 3.1 70B.")

    with st.sidebar:
        st.header("Configuration")
        api_key = get_api_key()
        st.markdown(f"**Model:** `{MODEL_NAME}`")
        st.markdown("The assistant is configured with a college-project-focused system prompt.")

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask about your project, report, code, or presentation...")

    if not user_prompt:
        return

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    if not api_key:
        error_message = (
            "Missing Groq API key. Add it in the sidebar or set the `GROQ_API_KEY` environment variable."
        )
        with st.chat_message("assistant"):
            st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        return

    try:
        client = Groq(api_key=api_key)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                assistant_reply = get_assistant_response(client, st.session_state.messages)
            st.markdown(assistant_reply)

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    except Exception as exc:
        error_text = str(exc).lower()
        if "api key" in error_text or "authentication" in error_text or "unauthorized" in error_text:
            friendly_error = "Authentication failed. Check that your Groq API key is valid."
        elif "rate limit" in error_text or "too many requests" in error_text:
            friendly_error = "Rate limit reached. Wait a moment and try again."
        elif "connection" in error_text or "timeout" in error_text:
            friendly_error = "Network error while contacting Groq. Check your connection and try again."
        else:
            friendly_error = f"Groq API error: {exc}"

        with st.chat_message("assistant"):
            st.error(friendly_error)

        st.session_state.messages.append({"role": "assistant", "content": friendly_error})


if __name__ == "__main__":
    main()

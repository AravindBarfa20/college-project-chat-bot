import os
from typing import Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = (
    "You are Student Help Assistant, a clear and supportive academic assistant for students. "
    "Help with assignments, reports, coding projects, presentations, viva preparation, "
    "translation, and simplification. When a user asks for explanation, rewrite the answer in "
    "simple language that is easy to understand. When a user asks for translation, preserve the "
    "meaning, improve readability, and keep the result student-friendly."
)
STARTER_PROMPTS = [
    "Help me choose a final-year project topic in AI.",
    "Create a report outline for my college mini project.",
    "Explain this Python error in simple terms.",
    "Translate this paragraph into simple English for me.",
]


def initialize_session_state() -> None:
    defaults = {
        "messages": [],
        "pending_prompt": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(27, 127, 204, 0.15), transparent 28%),
                radial-gradient(circle at top right, rgba(19, 172, 102, 0.14), transparent 25%),
                linear-gradient(180deg, #0b1020 0%, #111827 100%);
        }
        .block-container {
            padding-top: 2.25rem;
            padding-bottom: 2rem;
            max-width: 900px;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(20, 184, 166, 0.16), rgba(59, 130, 246, 0.18));
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 24px;
            padding: 1.4rem 1.3rem;
            margin-bottom: 1rem;
            box-shadow: 0 20px 60px rgba(15, 23, 42, 0.28);
        }
        .hero-title {
            font-size: 2.3rem;
            font-weight: 700;
            margin: 0 0 0.3rem 0;
            color: #f8fafc;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 1rem;
            margin: 0;
        }
        .status-card {
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .status-title {
            color: #e2e8f0;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .status-pill {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 0.6rem;
        }
        .status-ok {
            background: rgba(34, 197, 94, 0.16);
            color: #86efac;
            border: 1px solid rgba(34, 197, 94, 0.25);
        }
        .status-missing {
            background: rgba(248, 113, 113, 0.12);
            color: #fca5a5;
            border: 1px solid rgba(248, 113, 113, 0.2);
        }
        .mini-note {
            color: #cbd5e1;
            font-size: 0.92rem;
            margin: 0;
        }
        div[data-testid="stChatMessage"] {
            border-radius: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def resolve_api_key() -> str:
    secret_key = ""
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        secret_key = ""

    env_key = os.getenv("GROQ_API_KEY", "")
    return (secret_key or env_key).strip()


def build_conversation(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}, *messages]


def get_assistant_response(client: Groq, messages: List[Dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=build_conversation(messages),
        temperature=0.6,
        max_completion_tokens=1024,
    )
    return response.choices[0].message.content or "I couldn't generate a response."


def render_sidebar(api_key: str) -> None:
    with st.sidebar:
        st.header("Workspace")
        status_class = "status-ok" if api_key else "status-missing"
        status_label = "Groq connected" if api_key else "Groq key missing"
        status_help = (
            "The key is loaded securely from Streamlit Secrets or your local .env file."
            if api_key
            else "Add GROQ_API_KEY in Streamlit Secrets for cloud, or in your local .env file."
        )
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-title">Connection</div>
                <div class="status-pill {status_class}">{status_label}</div>
                <p class="mini-note">{status_help}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"**Model:** `{MODEL_NAME}`")
        st.markdown("**Role:** Student Help Assistant")
        if st.button("Clear chat history", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_prompt = None
            st.rerun()


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Student Help Assistant</div>
            <p class="hero-subtitle">
                Study smarter with project guidance, translation help, simple explanations, report support, and viva preparation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_starter_prompts() -> None:
    if st.session_state.messages:
        return

    st.caption("Try one of these to get started")
    columns = st.columns(2)
    for index, prompt in enumerate(STARTER_PROMPTS):
        if columns[index % 2].button(prompt, use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.rerun()


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def classify_error(exc: Exception) -> str:
    error_text = str(exc).lower()
    if "api key" in error_text or "authentication" in error_text or "unauthorized" in error_text:
        return "Authentication failed. Check the configured Groq API key in your environment or Streamlit Secrets."
    if "rate limit" in error_text or "too many requests" in error_text:
        return "Rate limit reached. Wait a moment and try again."
    if "connection" in error_text or "timeout" in error_text:
        return "Network error while contacting Groq. Check connectivity and try again."
    if "model_decommissioned" in error_text or "decommissioned" in error_text:
        return "The selected Groq model is no longer available. Update the configured model name."
    return f"Groq API error: {exc}"


def process_user_prompt(prompt: str, api_key: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        error_message = (
            "No Groq API key is configured. Add `GROQ_API_KEY` to your local `.env` file or Streamlit Secrets."
        )
        with st.chat_message("assistant"):
            st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        return

    try:
        client = Groq(api_key=api_key)
        with st.chat_message("assistant"):
            with st.spinner("Thinking through your project..."):
                assistant_reply = get_assistant_response(client, st.session_state.messages)
            st.markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as exc:
        friendly_error = classify_error(exc)
        with st.chat_message("assistant"):
            st.error(friendly_error)
        st.session_state.messages.append({"role": "assistant", "content": friendly_error})


def pop_pending_prompt() -> Optional[str]:
    prompt = st.session_state.pending_prompt
    if prompt:
        st.session_state.pending_prompt = None
        return prompt
    return None


def main() -> None:
    st.set_page_config(page_title="Student Help Assistant", page_icon="🎓", layout="centered")
    initialize_session_state()
    inject_styles()

    api_key = resolve_api_key()
    render_sidebar(api_key)
    render_header()
    render_starter_prompts()
    render_chat_history()

    chat_prompt = st.chat_input("Ask for project help, translation, explanations, reports, or presentation support...")
    prompt = pop_pending_prompt() or chat_prompt

    if prompt:
        process_user_prompt(prompt, api_key)


if __name__ == "__main__":
    main()

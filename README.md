# College Project Chat Bot

A production-ready NLP chatbot built with Python, Streamlit, and the Groq API.

## Features

- ChatGPT-like interface using Streamlit chat components
- Groq integration with `llama-3.1-70b-versatile`
- Session-based chat memory for follow-up questions
- API key support via environment variable or sidebar input
- Error handling for authentication, rate limits, and connectivity issues

## Local Setup

1. Create a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your Groq API key to `.env`.
4. Start the app:

   ```bash
   streamlit run app.py
   ```

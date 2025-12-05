import streamlit as st
from langgraph_pipeline import run_pipeline, initialize_vectorstore
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Neuradynamics Assessment", layout="wide")

st.title("Weather + PDF AI Agent")
st.markdown("Ask about weather or any question from the PDF document!")

if "vectorstore_initialized" not in st.session_state:
    with st.spinner("Loading PDF document..."):
        try:
            initialize_vectorstore()
            st.session_state.vectorstore_initialized = True
            st.success("PDF loaded successfully!")
        except FileNotFoundError:
            st.warning("PDF file (pdf_doc.pdf) not found. Ask weather queries instead.")
            st.session_state.vectorstore_initialized = False
        except Exception as e:
            st.error(f"Error loading PDF: {str(e)}")
            st.session_state.vectorstore_initialized = False

if not os.getenv("OPENWEATHER_API_KEY"):
    st.warning("OpenWeatherMap API key not set. Add the API Key.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.header("Chat with LLM")

for sender, message in st.session_state.chat_history:
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(message)

user_input = st.chat_input("Ask a question")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    
    with st.spinner("Thinking..."):
        try:
            response = run_pipeline(user_input)
            st.session_state.chat_history.append(("AI", response))
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.chat_history.append(("AI", error_msg))
            st.error(error_msg)
    
    st.rerun()

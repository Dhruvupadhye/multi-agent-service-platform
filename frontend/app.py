import streamlit as st
import requests

# Base URL for your FastAPI backend
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Multi-Agent Office Platform", page_icon="🤖", layout="wide")
st.title("🤖 Multi-Agent Office Platform")

# Create tabs for our different features
tab1, tab2, tab3 = st.tabs([
    "🎤 The Master Assistant", 
    "📚 Document RAG Assistant", 
    "📄 Upload Documents"
])

# --- TAB 1: Master Assistant (Voice Orchestration) ---
with tab1:
    st.header("The Master Assistant")
    st.write("Tell the Assistant what to do: draft an email, check your inbox, search your documents, or schedule a meeting!")
    
    # Streamlit's native microphone recording widget
    audio_value = st.audio_input("Record your command")
    
    if audio_value:
        with st.spinner("Supervisor Agent is analyzing your command..."):
            # Send the audio bytes directly to your FastAPI backend
            files = {"file": ("audio.wav", audio_value, "audio/wav")}
            response = requests.post(f"{API_BASE}/agents/orchestrate-voice/", files=files)
            
            if response.status_code == 200:
                data = response.json()
                intent = data.get("intent")
                
                # Handle Email Summarization Intent
                if intent == "SUMMARIZE_EMAILS":
                    st.success("Inbox Processed!")
                    st.info(data.get("action_result"))
                
                # Handle Scheduling Intent
                elif intent == "SCHEDULE_EVENT":
                    st.success("Event Scheduled!")
                    st.info(data.get("action_result"))
                    event_link = data.get("event_link")
                    if event_link:
                        st.markdown(f"[🔗 View on Google Calendar]({event_link})")
                
                # Handle Drafting Intents (Research or Compose)
                else:
                    st.success("Email Drafted Successfully!")
                    final_email = data.get("final_email", {})
                    
                    st.subheader("Subject")
                    st.code(final_email.get("subject", "No subject generated"))
                    
                    st.subheader("Body")
                    st.text_area("Draft", final_email.get("body", ""), height=250)
                    
                    st.caption(f"Detected Recipient: {final_email.get('recipient_hint')} | Tone: {final_email.get('tone')}")
            else:
                st.error("Failed to process audio. Please ensure your backend is running.")

# --- TAB 2: Document RAG Assistant ---
with tab2:
    st.header("Ask the Assistant")
    st.write("Ask a question about your uploaded documents. If it doesn't know, it will search the web!")
    
    query = st.text_input("Enter your query:")
    if st.button("Ask Agent"):
        if query:
            with st.spinner("Thinking..."):
                response = requests.get(f"{API_BASE}/agents/ask-assistant/", params={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    st.markdown(f"### Answer:\n{data.get('answer')}")
                    
                    st.caption(f"Source: `{data.get('source')}`")
                    with st.expander("Context Preview"):
                        st.write(data.get("context_preview"))
                else:
                    st.error("Failed to fetch an answer.")
        else:
            st.warning("Please enter a query.")

# --- TAB 3: Upload Documents ---
with tab3:
    st.header("Upload a PDF to your Knowledge Base")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Extracting text and generating summary..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                response = requests.post(f"{API_BASE}/media/upload-document/", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Document successfully processed and added to ChromaDB!")
                    st.markdown("### Document Summary")
                    st.write(data.get("summary"))
                else:
                    st.error("Failed to process document.")
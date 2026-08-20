🤖 Multi-Agent Office Platform
An AI-powered, voice-enabled multi-agent office automation platform. Built with FastAPI, Streamlit, and LangGraph, this framework automates daily office tasks like email processing, calendar scheduling, and document analysis, all orchestrated through voice commands.

🌟 Key Features
🎙️ Voice-Controlled Orchestrator: Speak directly into the UI. The LangGraph Supervisor Agent analyzes your intent and intelligently routes the command to the correct specialized agent.

📧 Smart Email Agent: Fetches unread emails via the Gmail API, filters out spam using a custom-trained Machine Learning classifier, and summarizes the rest.

📅 Reminder & Calendar Agent: Extracts meeting details from natural language and automatically schedules events on your Google Calendar.

📱 Real-Time Notifications: Pushes email digests and meeting confirmations directly to your phone via Twilio's WhatsApp API.

📚 Document RAG Agent: Upload PDFs to build a local knowledge base (ChromaDB) and ask the assistant questions about your documents. Falls back to web search if the answer isn't locally available.

✍️ Email Composer Agent: Drafts professional emails based on your voice instructions, utilizing data retrieved from your document knowledge base if needed.

🛠️ Tech Stack:
Backend (The Brain) :

Framework: FastAPI

AI/Orchestration: LangChain, LangGraph, OpenAI (gpt-4o-mini)

Vector Database: ChromaDB (Local)

Machine Learning: scikit-learn, joblib (Custom Spam Classifier)

Integrations: Google Workspace APIs (Gmail, Calendar), Twilio API (WhatsApp)

Frontend (The Face) :

Framework: Streamlit

Audio Processing: Streamlit audio input & local Whisper/API transcription

Markdown
## 📂 Project Structure

```text
multi-agent_office_platform/
│
├── app/                     # Backend API & Agent Logic
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configurations & settings
│   ├── agents/              # LangChain & LangGraph agents
│   │   ├── supervisor_agent.py
│   │   ├── email_agent.py
│   │   ├── reminder_agent.py
│   │   ├── composer_agent.py
│   │   ├── assistant_agent.py
│   │   └── document_agent.py
│   ├── models/              # ML Models (Spam Classifier)
│   │   └── train_classifier.py
│   ├── routes/              # API Endpoints
│   │   ├── agent_routes.py
│   │   ├── email_routes.py
│   │   └── media_routes.py
│   └── utils/               # Helper modules and integrations
│       ├── calendar_helper.py
│       ├── gmail_helper.py
│       ├── logger.py
│       ├── notifier.py
│       ├── vector_db.py
│       └── voice_helper.py
│
├── frontend/                # Streamlit UI
│   └── app.py               
│
├── .env                     # API Keys & Secrets
├── credentials.json         # Google Cloud OAuth Credentials
└── requirements.txt         # Python dependencies
```
🚀 Installation & Setup
1. Prerequisites
Python 3.10+

A Google Cloud Console Project with the Gmail API and Google Calendar API enabled.

A Twilio developer account for WhatsApp notifications.

An OpenAI API Key.

2. Clone the Repository
Bash
git clone https://github.com/Dhruvupadhye/multi-agent-service-platform.git
cd multi-agent-office-platform
3. Create a Virtual Environment & Install Dependencies
Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
4. Environment Variables
Create a .env file in the root directory and add your keys:

Code snippet
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+1234567890
5. Google API Credentials
Download your OAuth 2.0 Client IDs from Google Cloud Console.

Save the file as credentials.json in the root directory.

On the first run, the app will open a browser window to authenticate and generate token.json and calendar_token.json.

6. Train the Spam Classifier
Before running the platform, you must generate the .pkl model file used by the Email Agent.

Bash
python app/models/train_classifier.py
💻 Running the Application
This platform requires the backend and frontend to run concurrently. Open two separate terminal windows.

Terminal 1: Start the FastAPI Backend

Bash
uvicorn app.main:app --reload
Terminal 2: Start the Streamlit Frontend

Bash
streamlit run frontend/app.py
🎯 Usage Examples
Navigate to the local Streamlit URL (usually http://localhost:8501) and test the platform using your voice:

Check Emails: "Hey, check my inbox and summarize my unread emails."

Schedule Meetings: "Book a code review with the engineering team for tomorrow at 3 PM."

Draft Emails: "Draft an urgent email to the marketing team asking for the Q3 graphics by Friday."

Query Documents: Upload a PDF in the Upload Documents tab, then ask: "What are the key takeaways from the Q2 financial report?"
Schedule Meetings: "Book a code review with the engineering team for tomorrow at 3 PM."

Draft Emails: "Draft an urgent email to the marketing team asking for the Q3 graphics by Friday."

Query Documents: Upload a PDF in the Upload Documents tab, then ask: "What are the key takeaways from the Q2 financial report?"

import joblib
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.utils.vector_db import vector_db
from app.utils.notifier import notifier
from app.utils.logger import logger
from app.config import settings
from app.utils.gmail_helper import gmail_helper

class EmailAgent:
    def __init__(self):
        self.classifier = joblib.load("app/models/spam_classifier.pkl")
        self.llm = ChatOpenAI(
    temperature=0.2,
    model="gpt-4o-mini",
    api_key=settings.OPENAI_API_KEY
)
        self.chroma_collection = vector_db.get_or_create_collection("email_summaries")

    def classify(self, text: str) -> str:
        # 1. ML Model Classification
        category = self.classifier.predict([text])[0]
        return category

    def summarize(self, email_body: str) -> str:
        # 2. LangChain Summarization
        prompt = PromptTemplate.from_template(
            "Summarize the following email in 2 crisp sentences for a busy professional:\n\nEmail: {email}"
        )
        chain = prompt | self.llm
        response = chain.invoke({"email": email_body})
        return response.content

    def process_emails(self, emails: list):
        summary_report = []

        # Sort priority: 'important' first, then 'casual', ignore 'spam'
        for mail in emails:
            content = f"{mail['subject']} {mail['body']}"
            category = self.classify(content)

            # Discard spam
            if category == "spam":
                logger.info(f"Email ID {mail['id']} classified as SPAM. Discarding.")
                continue

            summary = self.summarize(mail['body'])

            # Store in ChromaDB Vector DB
            self.chroma_collection.add(
                documents=[summary],
                metadatas=[{"category": category, "email_id": mail['id']}],
                ids=[mail['id']]
            )

            summary_report.append({"id": mail['id'], "category": category, "summary": summary})

        # Send digest via WhatsApp/Notification
        if summary_report:
            formatted_msg = "*--- Daily Email Digest ---*\n" + "\n".join(
                [f"• [{item['category'].upper()}] {item['summary']}" for item in summary_report]
            )
            notifier.send_whatsapp(formatted_msg)
        return summary_report

    def search_emails(self, query: str, max_results: int = 5) -> dict:
        logger.info(f"EmailAgent searching emails for query: {query}")
        emails = gmail_helper.search_emails(query=query, max_results=max_results)
        if not emails:
            return {
                "count": 0,
                "summary": f"No emails found matching '{query}'.",
                "emails": []
            }
        
        email_items = []
        for mail in emails:
            sender = mail.get("sender", "Unknown Sender")
            subject = mail.get("subject", "No Subject")
            snippet = mail.get("body", "")[:150]
            date_str = mail.get("date", "")
            date_info = f" ({date_str})" if date_str else ""
            email_items.append(f"• From: {sender}{date_info}\n  Subject: {subject}\n  Snippet: {snippet}")
        
        summary_text = f"Found {len(emails)} email(s) matching your search:\n\n" + "\n\n".join(email_items)
        return {
            "count": len(emails),
            "summary": summary_text,
            "emails": emails
        }

email_agent = EmailAgent()
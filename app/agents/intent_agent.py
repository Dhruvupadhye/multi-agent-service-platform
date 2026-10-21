import re
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import settings
from app.utils.logger import logger

class IntentType(str, Enum):
    GENERAL_QUERY = "GENERAL_QUERY"
    COMPOSE_EMAIL = "COMPOSE_EMAIL"
    SUMMARIZE_EMAILS = "SUMMARIZE_EMAILS"
    EMAIL_SEARCH = "EMAIL_SEARCH"
    SCHEDULE_EVENT = "SCHEDULE_EVENT"
    CALENDAR_VIEW = "CALENDAR_VIEW"
    SET_REMINDER = "SET_REMINDER"
    DOCUMENT_QUERY = "DOCUMENT_QUERY"
    RESEARCH = "RESEARCH"
    CONVERSATIONAL_ASSISTANT = "CONVERSATIONAL_ASSISTANT"
    UNKNOWN_OR_AMBIGUOUS = "UNKNOWN_OR_AMBIGUOUS"
    INVALID_OR_EMPTY = "INVALID_OR_EMPTY"

class ExtractedEntities(BaseModel):
    recipient: Optional[str] = Field(default=None, description="Recipient of email or meeting")
    date: Optional[str] = Field(default=None, description="Date mentioned (e.g. tomorrow, Friday, 2026-10-22)")
    time: Optional[str] = Field(default=None, description="Time mentioned (e.g. 10 AM, 3 PM)")
    topic: Optional[str] = Field(default=None, description="Subject matter or query topic")
    action: Optional[str] = Field(default=None, description="Action verb requested (e.g. draft, summarize, find, schedule, view, remind)")
    document_name: Optional[str] = Field(default=None, description="Specific document or PDF name if mentioned")

class ClassificationResult(BaseModel):
    intent: IntentType = Field(description="The primary classified intent")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reason: str = Field(description="Brief explanation of why this intent was selected")
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities, description="Extracted entities")
    requires_clarification: bool = Field(default=False, description="True if command is ambiguous or incomplete")
    clarification_question: Optional[str] = Field(default=None, description="Clarification question to ask user if ambiguous")
    secondary_intents: List[str] = Field(default_factory=list, description="Any secondary intents in compound requests")

class IntentClassifier:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.parser = JsonOutputParser(pydantic_object=ClassificationResult)
        
        self.prompt = PromptTemplate(
            template="""You are an expert natural language understanding system for an AI executive office assistant.
Your task is to accurately classify user voice commands and extract key entities.

Supported Intents:
1. GENERAL_QUERY: User asks an explanation, definition, comparison, factual question, or concept.
   Examples: "What is artificial intelligence?", "Explain neural networks with an example", "How does cloud computing work?", "What is the difference between Python and Java?"
   -> NOT an email draft.

2. COMPOSE_EMAIL: User EXPLICITLY asks to draft, compose, write, or prepare an email to someone.
   Examples: "Draft an email requesting leave", "Write an email to my manager", "Compose an email thanking the recruiter", "Draft a reply to this email"
   CRITICAL: Mentioning the word "email" does NOT automatically mean COMPOSE_EMAIL!
   - "Summarize my unread emails" -> SUMMARIZE_EMAILS
   - "Find the email about my internship" -> EMAIL_SEARCH
   - "Explain what this email means" -> GENERAL_QUERY / CONVERSATIONAL_ASSISTANT

3. SUMMARIZE_EMAILS: User wants to fetch, read, prioritize, or summarize inbox/unread emails.
   Examples: "Summarize my unread emails", "Show me the important emails I received today", "Give me a summary of my inbox"

4. EMAIL_SEARCH: User wants to search for, locate, or retrieve specific emails.
   Examples: "Find the email containing my internship offer", "Search for emails from my professor", "Find the email I received last Monday about the meeting"

5. SCHEDULE_EVENT: User explicitly asks to book, create, or schedule a NEW meeting or calendar event.
   Examples: "Schedule a meeting tomorrow at 3 PM", "Create a calendar event for Friday", "Book a sync with the team"

6. CALENDAR_VIEW: User asks to see, check, or retrieve their existing schedule or upcoming meetings.
   Examples: "What meetings do I have tomorrow?", "Check my schedule for Friday", "Do I have any meetings today?"
   CRITICAL: Do NOT classify viewing existing schedule as SCHEDULE_EVENT!

7. SET_REMINDER: User asks to set a reminder or be notified about something.
   Examples: "Remind me to submit my assignment tomorrow", "Set a reminder for my interview at 9 AM", "Notify me to call my professor this evening"

8. DOCUMENT_QUERY: User asks a question specifically about uploaded documents, PDFs, or files.
   Examples: "Search the uploaded PDF for project requirements", "What does my document say about the system architecture?", "Find the section explaining database design"

9. RESEARCH: User asks to conduct web research or gather external industry/technical information.
   Examples: "Research recent advances in generative AI", "Compare the major cloud service providers", "Find information about recent advances in robotics"

10. CONVERSATIONAL_ASSISTANT: General advice, productivity tips, casual banter, or context-dependent follow-up questions.
    Examples: "How can I improve my productivity?", "Explain that in simpler terms", "Give me an example", "What do you recommend?"

11. UNKNOWN_OR_AMBIGUOUS: The request is too vague, fragmented, or missing critical information to determine intent.
    Examples: "Schedule it", "Send that thing", "Do what we discussed", "Help me with that"
    Set requires_clarification=true and provide a helpful clarification_question.

12. INVALID_OR_EMPTY: Empty, silence, or unintelligible noise.

Conversation Context (if any):
{context}

User Voice Request: "{user_input}"

Format Instructions:
{format_instructions}
""",
            input_variables=["user_input", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        if api_key:
            self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=api_key)
            self.chain = self.prompt | self.llm | self.parser
        else:
            self.llm = None
            self.chain = None

    def _rule_based_classify(self, text: str, context: Optional[str] = None) -> ClassificationResult:
        """Deterministic semantic fallback classifier for robust routing and offline/unit testing."""
        clean = text.strip()
        lower = clean.lower()

        # 1. Empty or whitespace
        if not clean:
            return ClassificationResult(
                intent=IntentType.INVALID_OR_EMPTY,
                confidence=1.0,
                reason="Empty audio transcription or blank request.",
                requires_clarification=True,
                clarification_question="No speech was detected. Please record your command again."
            )

        # 2. Ambiguous fragmented inputs
        ambiguous_phrases = ["schedule it", "send that", "send it", "do it", "do that", "help me with that", "do what we discussed", "process it"]
        if lower in ambiguous_phrases or (len(lower.split()) <= 2 and lower in ["schedule", "send", "email", "search"]):
            return ClassificationResult(
                intent=IntentType.UNKNOWN_OR_AMBIGUOUS,
                confidence=0.3,
                reason="Request is underspecified and ambiguous.",
                requires_clarification=True,
                clarification_question="Could you please specify what action or details you would like me to handle?"
            )

        # 3. Contextual follow-up patterns
        follow_up_patterns = [
            r"^(explain that|explain this|in simpler terms|give me an example|what do you mean|tell me more|can you elaborate|give an example|provide an example)",
            r"^(what about|and what about|how so|why is that)"
        ]
        if any(re.search(pat, lower) for pat in follow_up_patterns):
            if context:
                return ClassificationResult(
                    intent=IntentType.CONVERSATIONAL_ASSISTANT,
                    confidence=0.9,
                    reason="Follow-up question referencing previous conversation context.",
                    entities=ExtractedEntities(action="clarify_or_example", topic="contextual_follow_up")
                )
            else:
                return ClassificationResult(
                    intent=IntentType.CONVERSATIONAL_ASSISTANT,
                    confidence=0.85,
                    reason="Conversational request or follow-up query.",
                    entities=ExtractedEntities(action="clarify_or_example")
                )

        # 4. Explicit COMPOSE_EMAIL (Must have active drafting/writing intent)
        compose_patterns = [
            r"\b(draft|write|compose|prepare)\s+(an?\s+)?(email|mail|reply|message to)\b",
            r"\b(send|shoot)\s+(an?\s+)?email to\b",
            r"\bdraft a reply\b"
        ]
        if any(re.search(pat, lower) for pat in compose_patterns):
            # Extract recipient and topic
            recip = None
            recip_match = re.search(r"\bto\s+([A-Za-z0-9_\-\.]+@[A-Za-z0-9_\-\.]+|[A-Za-z\s]+?)(?:\s+(?:requesting|regarding|about|for|to)|$)", clean, re.IGNORECASE)
            if recip_match:
                recip = recip_match.group(1).strip()
            return ClassificationResult(
                intent=IntentType.COMPOSE_EMAIL,
                confidence=0.95,
                reason="Explicit instruction to draft or compose an email.",
                entities=ExtractedEntities(recipient=recip, action="compose_email")
            )

        # 5. SUMMARIZE_EMAILS (Fetch or summarize inbox)
        summarize_patterns = [
            r"\b(summarize|summary of|read|check)\s+(my\s+)?(unread\s+)?(emails?|inbox|messages?)\b",
            r"\b(important emails?|new emails?|inbox summary)\b",
            r"\bshow me the (important|unread) emails\b"
        ]
        if any(re.search(pat, lower) for pat in summarize_patterns):
            # Check for compound query (e.g. summarize and check for meeting)
            secondary = []
            if "meeting" in lower or "calendar" in lower:
                secondary.append("MEETING_CHECK")
            return ClassificationResult(
                intent=IntentType.SUMMARIZE_EMAILS,
                confidence=0.95,
                reason="Request to summarize or check inbox emails.",
                entities=ExtractedEntities(action="summarize_inbox"),
                secondary_intents=secondary
            )

        # 6. EMAIL_SEARCH (Search / find specific emails)
        email_search_patterns = [
            r"\b(find|search|look for|get)\s+(the\s+)?(emails?|messages?)\b",
            r"\bsearch\s+my\s+emails?\b",
            r"\bemails?\s+(from|about|containing|with)\b"
        ]
        if any(re.search(pat, lower) for pat in email_search_patterns):
            topic_match = re.search(r"\b(?:about|containing|for|from)\s+(.+)$", clean, re.IGNORECASE)
            topic = topic_match.group(1).strip() if topic_match else None
            return ClassificationResult(
                intent=IntentType.EMAIL_SEARCH,
                confidence=0.92,
                reason="Request to search for specific emails matching criteria.",
                entities=ExtractedEntities(action="search_emails", topic=topic)
            )

        # 7. CALENDAR_VIEW (Check / view existing meetings or schedule)
        calendar_view_patterns = [
            r"\b(what meetings|which meetings|do i have (any )?meetings|show (me )?my (meetings|schedule|calendar)|check my (schedule|calendar)|what('s| is) (on )?my (schedule|calendar))\b",
            r"\bwhat meetings are scheduled\b",
            r"\bany meetings tomorrow\b"
        ]
        if any(re.search(pat, lower) for pat in calendar_view_patterns):
            date_match = re.search(r"\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week)\b", lower)
            date_val = date_match.group(1) if date_match else "upcoming"
            return ClassificationResult(
                intent=IntentType.CALENDAR_VIEW,
                confidence=0.95,
                reason="Inquiry to view or check scheduled calendar events.",
                entities=ExtractedEntities(action="view_calendar", date=date_val)
            )

        # 8. SCHEDULE_EVENT (Create or book a new calendar event)
        schedule_patterns = [
            r"\b(schedule|book|create|set up|add)\s+(a\s+)?(meeting|calendar event|appointment|event|call)\b",
            r"\bcreate a calendar event\b"
        ]
        if any(re.search(pat, lower) for pat in schedule_patterns):
            date_match = re.search(r"\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lower)
            time_match = re.search(r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b", lower)
            return ClassificationResult(
                intent=IntentType.SCHEDULE_EVENT,
                confidence=0.95,
                reason="Explicit request to create a new calendar event or meeting.",
                entities=ExtractedEntities(
                    action="create_event",
                    date=date_match.group(1) if date_match else None,
                    time=time_match.group(1) if time_match else None
                )
            )

        # 9. SET_REMINDER (Reminders / alerts)
        reminder_patterns = [
            r"\b(remind me to|set a reminder|create a reminder|notify me to|alert me to)\b"
        ]
        if any(re.search(pat, lower) for pat in reminder_patterns):
            topic_match = re.search(r"\b(?:remind me to|set a reminder (?:to|for)|notify me to)\s+(.+?)(?:\s+(?:at|tomorrow|on|next)|$)", clean, re.IGNORECASE)
            return ClassificationResult(
                intent=IntentType.SET_REMINDER,
                confidence=0.95,
                reason="Request to set a reminder or time-based notification.",
                entities=ExtractedEntities(
                    action="set_reminder",
                    topic=topic_match.group(1).strip() if topic_match else None
                )
            )

        # 10. DOCUMENT_QUERY (Uploaded documents, PDFs, knowledge base)
        document_patterns = [
            r"\b(uploaded|document|documents|pdf|pdfs|file|files|knowledge base)\b",
            r"\bwhat does (my|the) document say\b",
            r"\bsearch the uploaded\b"
        ]
        if any(re.search(pat, lower) for pat in document_patterns):
            return ClassificationResult(
                intent=IntentType.DOCUMENT_QUERY,
                confidence=0.92,
                reason="Inquiry regarding content within uploaded documents or PDFs.",
                entities=ExtractedEntities(action="query_documents", topic=clean)
            )

        # 11. RESEARCH (Web search, industry trends, recent advances)
        research_patterns = [
            r"\b(research|compare the major|latest developments in|recent advances in|find information about recent)\b",
            r"\bsearch the web for\b"
        ]
        if any(re.search(pat, lower) for pat in research_patterns):
            return ClassificationResult(
                intent=IntentType.RESEARCH,
                confidence=0.90,
                reason="Request requiring external research or information gathering.",
                entities=ExtractedEntities(action="conduct_research", topic=clean)
            )

        # 12. CONVERSATIONAL_ASSISTANT (Productivity, advice, recommendations)
        conversational_patterns = [
            r"\b(how can i improve my productivity|what do you recommend|give me advice|tips for|how do i)\b",
            r"\b(hello|hi|hey|good morning|good afternoon)\b"
        ]
        if any(re.search(pat, lower) for pat in conversational_patterns):
            return ClassificationResult(
                intent=IntentType.CONVERSATIONAL_ASSISTANT,
                confidence=0.88,
                reason="Conversational request, productivity question, or advice.",
                entities=ExtractedEntities(action="conversational_assistance")
            )

        # 13. GENERAL_QUERY (Default for questions, definitions, explanations)
        general_patterns = [
            r"^(what is|what are|explain|describe|define|how does|why is|difference between|tell me about)",
            r"\b(artificial intelligence|machine learning|neural networks|cloud computing|python and java)\b"
        ]
        if any(re.search(pat, lower) for pat in general_patterns) or lower.endswith("?"):
            return ClassificationResult(
                intent=IntentType.GENERAL_QUERY,
                confidence=0.92,
                reason="General question, definition, comparison, or explanation.",
                entities=ExtractedEntities(action="explain_query", topic=clean)
            )

        # Fallback to general query rather than email compose
        return ClassificationResult(
            intent=IntentType.GENERAL_QUERY,
            confidence=0.75,
            reason="Interpreted as a general query request.",
            entities=ExtractedEntities(topic=clean)
        )

    def classify(self, text_input: str, context: Optional[str] = None) -> ClassificationResult:
        """Classify user command using LLM with deterministic fallback."""
        clean_text = text_input.strip() if text_input else ""
        
        # 1. Fast path for empty / blank transcripts
        if not clean_text:
            return ClassificationResult(
                intent=IntentType.INVALID_OR_EMPTY,
                confidence=1.0,
                reason="Empty audio transcription.",
                requires_clarification=True,
                clarification_question="No speech was detected. Please record your command again."
            )

        # 2. Try LLM classification if configured
        if not self.chain:
            logger.info("IntentClassifier: LLM chain not initialized. Using deterministic classifier.")
            return self._rule_based_classify(clean_text, context=context)

        try:
            logger.info(f"IntentClassifier: Classifying input '{clean_text}' via LLM...")
            result_dict = self.chain.invoke({
                "user_input": clean_text,
                "context": context or "No previous conversation context."
            })
            
            # Validate with Pydantic
            validated = ClassificationResult(**result_dict)
            logger.info(f"IntentClassifier LLM Result: {validated.intent} (confidence={validated.confidence})")
            
            # Confidence check: If LLM reports low confidence (< 0.5), enforce clarification
            if validated.confidence < 0.5:
                validated.requires_clarification = True
                if not validated.clarification_question:
                    validated.clarification_question = "Could you please clarify what you'd like me to help you with?"
                    
            return validated
            
        except Exception as e:
            logger.warning(f"IntentClassifier: LLM classification failed ({e}). Using deterministic fallback.")
            fallback_result = self._rule_based_classify(clean_text, context=context)
            logger.info(f"IntentClassifier Fallback Result: {fallback_result.intent}")
            return fallback_result

intent_classifier = IntentClassifier()

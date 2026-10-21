from typing import TypedDict, Optional, Any, Dict, List
from collections import defaultdict
from langgraph.graph import StateGraph, END

# Agent Imports
from app.agents.assistant_agent import assistant_agent
from app.agents.composer_agent import composer_agent
from app.agents.email_agent import email_agent
from app.agents.reminder_agent import reminder_agent
from app.agents.intent_agent import intent_classifier, IntentType, ClassificationResult

# Utility Imports
from app.utils.gmail_helper import gmail_helper
from app.utils.notifier import notifier
from app.utils.logger import logger

class AgentState(TypedDict):
    user_input: str
    intent: str
    confidence: float
    reason: Optional[str]
    entities: Optional[dict]
    requires_clarification: bool
    clarification_question: Optional[str]
    session_id: Optional[str]
    context_preview: Optional[str]
    direct_answer: Optional[str]
    action_result: Optional[str]
    final_email: Optional[dict]
    event_link: Optional[str]
    data: Optional[Any]
    source: Optional[str]
    response_type: Optional[str]

class ConversationSessionManager:
    """Manages rolling conversation history per session for multi-turn voice context."""
    def __init__(self, max_history: int = 5):
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.max_history = max_history

    def get_context_string(self, session_id: str) -> str:
        history = self.sessions.get(session_id, [])
        if not history:
            return ""
        lines = []
        for turn in history[-self.max_history:]:
            lines.append(f"User: {turn.get('user', '')}")
            lines.append(f"Assistant: {turn.get('assistant', '')} (Intent: {turn.get('intent', '')})")
        return "\n".join(lines)

    def add_turn(self, session_id: str, user_text: str, assistant_text: str, intent: str):
        if not session_id:
            session_id = "default"
        self.sessions[session_id].append({
            "user": user_text,
            "assistant": assistant_text,
            "intent": intent
        })
        # Keep only the most recent turns
        if len(self.sessions[session_id]) > self.max_history * 2:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]

    def clear(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

class SupervisorAgent:
    def __init__(self):
        self.session_manager = ConversationSessionManager()
        
        # Build LangGraph workflow
        workflow = StateGraph(AgentState)
        
        # 1. Add all specialized processing nodes
        workflow.add_node("router", self.router_node)
        workflow.add_node("general_assistant", self.general_assistant_node)
        workflow.add_node("conversational_assistant", self.conversational_assistant_node)
        workflow.add_node("document_assistant", self.document_assistant_node)
        workflow.add_node("research_assistant", self.research_assistant_node)
        workflow.add_node("composer", self.composer_node)
        workflow.add_node("email_summarizer", self.email_summarizer_node)
        workflow.add_node("email_searcher", self.email_searcher_node)
        workflow.add_node("event_scheduler", self.event_scheduler_node)
        workflow.add_node("calendar_viewer", self.calendar_viewer_node)
        workflow.add_node("reminder_node", self.reminder_node)
        workflow.add_node("clarification_handler", self.clarification_handler_node)
        
        workflow.set_entry_point("router")
        
        # 2. Conditional routing from router
        workflow.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "general_assistant": "general_assistant",
                "conversational_assistant": "conversational_assistant",
                "document_assistant": "document_assistant",
                "research_assistant": "research_assistant",
                "composer": "composer",
                "email_summarizer": "email_summarizer",
                "email_searcher": "email_searcher",
                "event_scheduler": "event_scheduler",
                "calendar_viewer": "calendar_viewer",
                "reminder_node": "reminder_node",
                "clarification_handler": "clarification_handler"
            }
        )
        
        # 3. Clean termination: Every specialized node finishes at END
        # NOTE: researcher NO LONGER transitions to composer!
        workflow.add_edge("general_assistant", END)
        workflow.add_edge("conversational_assistant", END)
        workflow.add_edge("document_assistant", END)
        workflow.add_edge("research_assistant", END)
        workflow.add_edge("composer", END)
        workflow.add_edge("email_summarizer", END)
        workflow.add_edge("email_searcher", END)
        workflow.add_edge("event_scheduler", END)
        workflow.add_edge("calendar_viewer", END)
        workflow.add_edge("reminder_node", END)
        workflow.add_edge("clarification_handler", END)
        
        self.app = workflow.compile()

    def router_node(self, state: AgentState) -> AgentState:
        session_id = state.get("session_id", "default")
        context_str = self.session_manager.get_context_string(session_id)
        
        classification = intent_classifier.classify(state["user_input"], context=context_str)
        
        state["intent"] = classification.intent.value if hasattr(classification.intent, "value") else str(classification.intent)
        state["confidence"] = classification.confidence
        state["entities"] = classification.entities.model_dump() if hasattr(classification.entities, "model_dump") else {}
        state["requires_clarification"] = classification.requires_clarification
        state["clarification_question"] = classification.clarification_question
        
        logger.info(f"Supervisor Router: Intent={state['intent']}, Confidence={state['confidence']}, Reason={state['reason']}")
        return state

    def route_decision(self, state: AgentState) -> str:
        intent = state.get("intent", "GENERAL_QUERY")
        requires_clarification = state.get("requires_clarification", False)
        confidence = state.get("confidence", 1.0)
        
        logger.info(f"Supervisor Route Decision: Intent='{intent}', Confidence={confidence}, Clarification={requires_clarification}")
        
        # Guard: Ambiguous, invalid, or low-confidence requests
        if requires_clarification or confidence < 0.5 or intent in ("UNKNOWN_OR_AMBIGUOUS", "INVALID_OR_EMPTY"):
            return "clarification_handler"
            
        if intent == "GENERAL_QUERY":
            return "general_assistant"
        elif intent == "CONVERSATIONAL_ASSISTANT":
            return "conversational_assistant"
        elif intent == "DOCUMENT_QUERY":
            return "document_assistant"
        elif intent == "RESEARCH":
            return "research_assistant"
        elif intent == "COMPOSE_EMAIL":
            return "composer"
        elif intent == "SUMMARIZE_EMAILS":
            return "email_summarizer"
        elif intent == "EMAIL_SEARCH":
            return "email_searcher"
        elif intent == "SCHEDULE_EVENT":
            return "event_scheduler"
        elif intent == "CALENDAR_VIEW":
            return "calendar_viewer"
        elif intent == "SET_REMINDER":
            return "reminder_node"
            
        # Safe default: Answer directly rather than composing an email
        logger.warning(f"Unrecognized intent '{intent}', defaulting to general_assistant.")
        return "general_assistant"

    def general_assistant_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: general_assistant executing...")
        session_id = state.get("session_id", "default")
        context_str = self.session_manager.get_context_string(session_id)
        
        result = assistant_agent.answer_general_query(state["user_input"], context=context_str)
        state["direct_answer"] = result["answer"]
        state["action_result"] = result["answer"]
        state["source"] = result.get("source", "general_knowledge")
        state["response_type"] = "answer"
        return state

    def conversational_assistant_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: conversational_assistant executing...")
        session_id = state.get("session_id", "default")
        context_str = self.session_manager.get_context_string(session_id)
        
        result = assistant_agent.answer_conversational(state["user_input"], context=context_str)
        state["direct_answer"] = result["answer"]
        state["action_result"] = result["answer"]
        state["source"] = result.get("source", "conversational_assistant")
        state["response_type"] = "answer"
        return state

    def document_assistant_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: document_assistant executing...")
        result = assistant_agent.answer_document_query(state["user_input"])
        state["direct_answer"] = result["answer"]
        state["action_result"] = result["answer"]
        state["source"] = result.get("source", "uploaded_documents")
        state["context_preview"] = result.get("context_preview", "")
        state["response_type"] = "document_answer"
        return state

    def research_assistant_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: research_assistant executing...")
        result = assistant_agent.conduct_research(state["user_input"])
        state["direct_answer"] = result["answer"]
        state["action_result"] = result["answer"]
        state["source"] = result.get("source", "duckduckgo_web_search")
        state["context_preview"] = result.get("context_preview", "")
        state["response_type"] = "research_answer"
        return state

    def composer_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: composer drafting explicit email...")
        draft = composer_agent.compose_draft(state["user_input"])
        state["final_email"] = draft
        state["action_result"] = f"Email draft prepared for {draft.get('recipient_hint', 'recipient')}: '{draft.get('subject', 'No Subject')}'"
        state["response_type"] = "email_draft"
        return state

    def email_summarizer_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: email_summarizer fetching unread inbox...")
        try:
            raw_emails = gmail_helper.fetch_unread_emails(max_results=5)
            if raw_emails:
                summaries = email_agent.process_emails(raw_emails)
                state["data"] = summaries
                state["action_result"] = f"Successfully fetched and summarized {len(raw_emails)} email(s). Notification digest dispatched."
            else:
                state["data"] = []
                state["action_result"] = "Checked your inbox: You have no unread emails right now."
        except Exception as e:
            logger.error(f"Failed to process emails: {e}")
            state["action_result"] = f"Encountered an issue retrieving emails: {str(e)}"
            
        state["response_type"] = "email_summary"
        return state

    def email_searcher_node(self, state: AgentState) -> AgentState:
        logger.info(f"Supervisor Node: email_searcher executing for '{state['user_input']}'...")
        query = state.get("entities", {}).get("topic") or state["user_input"]
        result = email_agent.search_emails(query=query)
        state["action_result"] = result["summary"]
        state["data"] = result.get("emails", [])
        state["response_type"] = "email_search"
        return state

    def event_scheduler_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: event_scheduler creating calendar event...")
        result = reminder_agent.schedule_event(state["user_input"])
        
        if result["status"] == "success":
            state["action_result"] = f"Successfully scheduled: '{result['summary']}'!"
            state["event_link"] = result.get("event_link")
            
            # Dispatch WhatsApp confirmation
            whatsapp_msg = f"📅 *New Event Scheduled*\n{result['summary']}\nLink: {result.get('event_link', '')}"
            notifier.send_whatsapp(whatsapp_msg)
        else:
            state["action_result"] = f"Failed to schedule event: {result.get('message')}"
            
        state["response_type"] = "calendar_event"
        return state

    def calendar_viewer_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: calendar_viewer retrieving events...")
        result = reminder_agent.list_events(state["user_input"])
        state["action_result"] = result["summary"]
        state["data"] = result.get("events", [])
        state["response_type"] = "calendar_list"
        return state

    def reminder_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: reminder_node setting reminder...")
        result = reminder_agent.set_reminder(state["user_input"])
        state["action_result"] = result["summary"]
        state["event_link"] = result.get("event_link")
        state["response_type"] = "reminder"
        return state

    def clarification_handler_node(self, state: AgentState) -> AgentState:
        logger.info("Supervisor Node: clarification_handler executing...")
        question = state.get("clarification_question") or "Could you please clarify your request or provide more details?"
        state["direct_answer"] = question
        state["action_result"] = question
        state["response_type"] = "clarification"
        return state

    def orchestrate(self, text_input: str, session_id: str = "default") -> dict:
        clean_input = text_input.strip() if text_input else ""
        
        initial_state = {
            "user_input": clean_input,
            "intent": "GENERAL_QUERY",
            "confidence": 1.0,
            "reason": None,
            "entities": {},
            "requires_clarification": False,
            "clarification_question": None,
            "session_id": session_id,
            "context_preview": None,
            "direct_answer": None,
            "action_result": None,
            "final_email": None,
            "event_link": None,
            "data": None,
            "source": None,
            "response_type": None
        }
        
        result = self.app.invoke(initial_state)
        
        # Record successful turn into conversation memory
        assistant_reply = result.get("direct_answer") or result.get("action_result") or ""
        self.session_manager.add_turn(
            session_id=session_id,
            user_text=clean_input,
            assistant_text=assistant_reply,
            intent=result.get("intent", "GENERAL_QUERY")
        )
        
        return {
            "intent": result["intent"],
            "response_type": result.get("response_type", "answer"),
            "direct_answer": result.get("direct_answer"),
            "action_result": result.get("action_result"),
            "final_email": result.get("final_email"),
            "event_link": result.get("event_link"),
            "data": result.get("data"),
            "source": result.get("source"),
            "confidence": result.get("confidence", 1.0),
            "requires_clarification": result.get("requires_clarification", False),
            "clarification_question": result.get("clarification_question")
        }

supervisor_agent = SupervisorAgent()
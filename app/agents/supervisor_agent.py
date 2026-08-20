from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Agent Imports
from app.agents.assistant_agent import assistant_agent
from app.agents.composer_agent import composer_agent
from app.agents.email_agent import email_agent
from app.agents.reminder_agent import reminder_agent  # NEW!

# Utility Imports
from app.utils.gmail_helper import gmail_helper
from app.utils.notifier import notifier  # NEW!
from app.utils.logger import logger

class AgentState(TypedDict):
    user_input: str
    intent: str  
    research_context: Optional[str]
    final_email: Optional[dict]
    action_result: Optional[str]
    event_link: Optional[str]  # NEW!

class SupervisorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        workflow = StateGraph(AgentState)
        
        # Add all specialized nodes
        workflow.add_node("router", self.router_node)
        workflow.add_node("researcher", self.researcher_node)
        workflow.add_node("composer", self.composer_node)
        workflow.add_node("email_summarizer", self.email_summarizer_node)
        workflow.add_node("scheduler", self.scheduler_node)  # NEW!
        
        workflow.set_entry_point("router")
        
        # Update conditional routing
        workflow.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "researcher": "researcher",
                "composer": "composer",
                "email_summarizer": "email_summarizer",
                "scheduler": "scheduler"  # NEW!
            }
        )
        
        # Define edge paths
        workflow.add_edge("researcher", "composer")
        workflow.add_edge("composer", END)
        workflow.add_edge("email_summarizer", END)
        workflow.add_edge("scheduler", END)  # NEW!
        
        self.app = workflow.compile()

    def router_node(self, state: AgentState):
        logger.info("Supervisor: Analyzing user intent...")
        prompt = PromptTemplate.from_template(
            """Analyze the user's voice request: '{input}'. 
            Classify it into EXACTLY ONE of these categories:
            - RESEARCH (needs factual lookup in uploaded documents)
            - SUMMARIZE_EMAILS (wants to fetch, read, or summarize their inbox/emails)
            - SCHEDULE_EVENT (wants to set a reminder, book a meeting, or add to calendar)
            - COMPOSE (wants to draft a new email without looking up documents)
            
            Respond with ONLY the category word."""
        )
        chain = prompt | self.llm
        intent = chain.invoke({"input": state["user_input"]}).content.strip().upper()
        
        state["intent"] = intent
        return state

    def route_decision(self, state: AgentState):
        intent = state.get("intent", "COMPOSE")
        logger.info(f"Supervisor Decision: Route -> {intent}")
        
        if intent == "SUMMARIZE_EMAILS":
            return "email_summarizer"
        elif intent == "SCHEDULE_EVENT":
            return "scheduler"
        elif intent == "RESEARCH":
            return "researcher"
        return "composer"

    def scheduler_node(self, state: AgentState):
        logger.info("Supervisor: Scheduling calendar event...")
        
        result = reminder_agent.schedule_event(state["user_input"])
        
        if result["status"] == "success":
            state["action_result"] = f"Successfully scheduled: {result['summary']}!"
            state["event_link"] = result["event_link"]
            
            # Trigger the Notification Agent (WhatsApp)
            msg = f"📅 *New Event Scheduled*\n{result['summary']}\nLink: {result['event_link']}"
            notifier.send_whatsapp(msg)
        else:
            state["action_result"] = f"Failed to schedule event: {result.get('message')}"
            
        return state

    def email_summarizer_node(self, state: AgentState):
        logger.info("Supervisor: Fetching and summarizing inbox...")
        try:
            raw_emails = gmail_helper.fetch_unread_emails(max_results=5) 
            if raw_emails:
                email_agent.process_emails(raw_emails)
                state["action_result"] = f"Successfully fetched and summarized {len(raw_emails)} emails. Check your WhatsApp!"
            else:
                state["action_result"] = "Checked your inbox, but there are no new emails to summarize right now."
        except Exception as e:
            logger.error(f"Failed to process emails: {e}")
            state["action_result"] = f"Attempted to fetch emails, but encountered an error: {str(e)}"
        return state

    def researcher_node(self, state: AgentState):
        logger.info("Supervisor: Extracting data via RAG Assistant...")
        rag_result = assistant_agent.answer_query(state["user_input"])
        state["research_context"] = rag_result["answer"]
        return state

    def composer_node(self, state: AgentState):
        logger.info("Supervisor: Synthesizing and drafting email...")
        instructions = f"User Request: {state['user_input']}"
        if state.get("research_context"):
            instructions += f"\n\nContext/Data to include:\n{state['research_context']}"
        
        draft = composer_agent.chain.invoke({"transcript": instructions})
        state["final_email"] = draft
        state["action_result"] = "Email drafted successfully."
        return state

    def orchestrate(self, text_input: str) -> dict:
        initial_state = {
            "user_input": text_input,
            "intent": "COMPOSE",
            "research_context": None,
            "final_email": None,
            "action_result": None,
            "event_link": None
        }
        result = self.app.invoke(initial_state)
        
        return {
            "intent": result["intent"],
            "final_email": result.get("final_email"),
            "action_result": result.get("action_result"),
            "event_link": result.get("event_link")
        }

supervisor_agent = SupervisorAgent()
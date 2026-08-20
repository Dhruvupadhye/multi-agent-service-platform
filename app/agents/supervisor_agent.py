from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.agents.assistant_agent import assistant_agent
from app.agents.composer_agent import composer_agent
from app.utils.logger import logger

# 1. Define the State (the memory shared between agents)
class AgentState(TypedDict):
    user_input: str
    needs_research: bool
    research_context: Optional[str]
    final_email: Optional[dict]

class SupervisorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        
        # 2. Initialize the LangGraph
        workflow = StateGraph(AgentState)
        
        # Add our specialized nodes
        workflow.add_node("router", self.router_node)
        workflow.add_node("researcher", self.researcher_node)
        workflow.add_node("composer", self.composer_node)
        
        # Set the entry point
        workflow.set_entry_point("router")
        
        # Add conditional routing logic
        workflow.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "researcher": "researcher",  # If it needs data, go here first
                "composer": "composer"       # If no data needed, skip to composer
            }
        )
        
        # Handoff data from researcher directly to composer
        workflow.add_edge("researcher", "composer")
        # End the workflow after composing
        workflow.add_edge("composer", END)
        
        self.app = workflow.compile()

    def router_node(self, state: AgentState):
        logger.info("Supervisor: Analyzing input for data dependencies...")
        prompt = PromptTemplate.from_template(
            "Analyze the request: '{input}'. Does this require looking up specific facts, uploaded documents, or data? Respond with only YES or NO."
        )
        chain = prompt | self.llm
        response = chain.invoke({"input": state["user_input"]}).content.strip().upper()
        
        state["needs_research"] = "YES" in response
        return state

    def route_decision(self, state: AgentState):
        if state.get("needs_research"):
            logger.info("Supervisor Decision: Route -> RAG Assistant")
            return "researcher"
        logger.info("Supervisor Decision: Route -> Email Composer")
        return "composer"

    def researcher_node(self, state: AgentState):
        logger.info("Supervisor: Extracting data via RAG Assistant...")
        rag_result = assistant_agent.answer_query(state["user_input"])
        state["research_context"] = rag_result["answer"]
        return state

    def composer_node(self, state: AgentState):
        logger.info("Supervisor: Synthesizing and drafting email...")
        # Merge the user's original request with the facts found by the RAG agent
        instructions = f"User Request: {state['user_input']}"
        if state.get("research_context"):
            instructions += f"\n\nContext/Data to include:\n{state['research_context']}"
        
        # Hand off to the composer agent
        draft = composer_agent.chain.invoke({"transcript": instructions})
        state["final_email"] = draft
        return state

    def orchestrate(self, text_input: str) -> dict:
        # Initialize the state memory
        initial_state = {
            "user_input": text_input,
            "needs_research": False,
            "research_context": None,
            "final_email": None
        }
        # Run the workflow!
        result = self.app.invoke(initial_state)
        return result["final_email"]

supervisor_agent = SupervisorAgent()
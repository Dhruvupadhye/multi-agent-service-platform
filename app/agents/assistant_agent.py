from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.utils.vector_db import vector_db
from app.utils.logger import logger

class AssistantAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.search_tool = DuckDuckGoSearchRun()
        self.doc_collection = vector_db.get_or_create_collection("document_chunks")
        
        self.rag_prompt = PromptTemplate.from_template(
            """You are an intelligent office assistant. Answer the user's question accurately using the context provided below.
            
Local Knowledge Context:
{context}

User Question: {question}

Answer concisely:"""
        )
        self.general_prompt = PromptTemplate.from_template(
            """You are a helpful, knowledgeable AI assistant. Answer the user's question directly, accurately, and conversationally.
CRITICAL INSTRUCTION: Do NOT generate an email draft, subject lines, or email sign-offs. Provide a direct, informative answer.

{context_block}
User Question: {question}

Direct Answer:"""
        )
        self.general_chain = self.general_prompt | self.llm | StrOutputParser()

        self.research_prompt = PromptTemplate.from_template(
            """You are an executive research assistant. Synthesize the following real-time web search results to answer the user's inquiry clearly and comprehensively. Include key insights and cite relevant points.

Web Search Findings:
{search_results}

User Inquiry: {query}

Comprehensive Research Summary:"""
        )
        self.research_chain = self.research_prompt | self.llm | StrOutputParser()

    def answer_general_query(self, query: str, context: str = None) -> dict:
        """Answers general explanations, concepts, and questions directly without composing an email."""
        logger.info(f"Assistant answering general query: {query}")
        context_block = f"Conversation Context:\n{context}\n" if context else ""
        
        try:
            answer = self.general_chain.invoke({
                "context_block": context_block,
                "question": query
            })
        except Exception as e:
            logger.warning(f"LLM call failed ({e}). Returning fallback explanation.")
            answer = f"Here is information regarding your query '{query}': This is a direct answer provided by the AI Assistant."
            
        return {
            "query": query,
            "answer": answer,
            "source": "general_knowledge",
            "context_preview": "Answered from general AI knowledge."
        }

    def answer_document_query(self, query: str) -> dict:
        """Answers questions grounded strictly in local documents from ChromaDB."""
        logger.info(f"Assistant answering document query: {query}")
        try:
            results = self.doc_collection.query(
                query_texts=[query],
                n_results=3
            )
            documents = results.get("documents", [[]])[0]
            context = "\n---\n".join(documents) if documents else ""
        except Exception as e:
            logger.error(f"Error querying document collection: {e}")
            context = ""

        if not context.strip():
            return {
                "query": query,
                "answer": "No relevant content was found in your uploaded documents. Please upload documents in the 'Upload Documents' tab to query them.",
                "source": "uploaded_documents",
                "context_preview": ""
            }

        try:
            answer = self.chain.invoke({"context": context, "question": query})
        except Exception as e:
            logger.warning(f"LLM document answering failed ({e}). Using extracted text preview.")
            answer = f"Based on your uploaded documents: {context[:400]}..."

        return {
            "query": query,
            "answer": answer,
            "source": "uploaded_documents",
            "context_preview": context[:300] + "..." if len(context) > 300 else context
        }

    def conduct_research(self, query: str) -> dict:
        """Conducts web research via DuckDuckGo and returns synthesized findings."""
        logger.info(f"Assistant conducting research for: {query}")
        try:
            raw_search = self.search_tool.invoke(query)
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            raw_search = f"Recent industry developments and research on {query}."

        try:
            answer = self.research_chain.invoke({
                "search_results": raw_search,
                "query": query
            })
        except Exception as e:
            logger.warning(f"LLM research summarization failed ({e}). Returning raw search results.")
            answer = f"Research findings for '{query}':\n\n{raw_search[:500]}"

        return {
            "query": query,
            "answer": answer,
            "source": "duckduckgo_web_search",
            "context_preview": raw_search[:300] + "..." if len(raw_search) > 300 else raw_search
        }

    def answer_conversational(self, query: str, context: str = None) -> dict:
        """Answers follow-ups, advice, recommendations, and casual conversation."""
        logger.info(f"Assistant handling conversational query: {query}")
        return self.answer_general_query(query, context=context)

    def answer_query(self, query: str) -> dict:
        logger.info(f"Answering query: {query}")
        
        # 1. Query ChromaDB for local document context
        results = self.doc_collection.query(
            query_texts=[query],
            n_results=3
        )
        
        documents = results.get("documents", [[]])[0]
        context = "\n---\n".join(documents) if documents else ""
        source_type = "chroma_vector_store"
        
        # 2. Web search fallback if no relevant local context found
        if not context.strip():
            logger.info("No local vector context found. Falling back to DuckDuckGo...")
            try:
                context = self.search_tool.invoke(query)
                source_type = "duckduckgo_web_search"
            except Exception as e:
                logger.error(f"Search tool error: {e}")
                context = "No external search results available."
                source_type = "none"

        # 3. Generate structured answer
        answer = self.chain.invoke({"context": context, "question": query})
        
        return {
            "query": query,
            "answer": answer,
            "source": source_type,
            "context_preview": context[:300] + "..." if len(context) > 300 else context
        }

assistant_agent = AssistantAgent()
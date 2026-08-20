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
        self.chain = self.rag_prompt | self.llm | StrOutputParser()

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
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.utils.vector_db import vector_db
from app.utils.logger import logger

class DocumentAgent:
    def __init__(self):
        # Modern LangChain model setup
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.chroma_collection = vector_db.get_or_create_collection("document_chunks")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        
        # LCEL Summarization Chain
        self.prompt = PromptTemplate.from_template(
            "You are an executive assistant. Summarize the following document content clearly and concisely, highlighting key takeaways and actionable items:\n\n{text}"
        )
        self.summary_chain = self.prompt | self.llm | StrOutputParser()

    def process_and_summarize(self, file_path: str, filename: str) -> dict:
        logger.info(f"Document Agent processing: {filename}")
        
        # 1. Extract text from PDF
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # 2. Chunk text for Vector DB
        split_docs = self.text_splitter.split_documents(docs)
        
        # 3. Save chunks to ChromaDB
        documents = [doc.page_content for doc in split_docs]
        metadatas = [{"source": filename, "page": doc.metadata.get("page", 0)} for doc in split_docs]
        ids = [f"{filename}_chunk_{i}" for i in range(len(documents))]
        
        self.chroma_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # 4. Generate Summary across document chunks
        combined_text = "\n\n".join(documents[:10]) # Summarize key segments
        summary_text = self.summary_chain.invoke({"text": combined_text})
        
        return {
            "filename": filename,
            "total_pages": len(docs),
            "summary": summary_text
        }

document_agent = DocumentAgent()
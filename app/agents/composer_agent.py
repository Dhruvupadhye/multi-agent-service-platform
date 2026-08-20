from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.utils.voice_helper import voice_helper
from app.utils.logger import logger

class EmailDraft(BaseModel):
    recipient_hint: str = Field(description="Detected name or department of the recipient")
    subject: str = Field(description="Concise, professional subject line")
    body: str = Field(description="Polished, professional email body based on voice notes")
    tone: str = Field(description="Detected tone: Formal, Friendly, Urgent, etc.")

class ComposerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini")
        self.parser = JsonOutputParser(pydantic_object=EmailDraft)
        
        self.prompt = PromptTemplate(
            template="""You are an executive email assistant. Turn the following voice transcript into a well-structured, professional email draft.
            
Voice Transcript:
{transcript}

Format Instructions:
{format_instructions}
""",
            input_variables=["transcript"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        self.chain = self.prompt | self.llm | self.parser

    def compose_from_voice(self, audio_file_path: str) -> dict:
        # 1. Transcribe voice note
        transcript = voice_helper.transcribe_audio(audio_file_path)
        logger.info(f"Transcribed voice note: {transcript}")
        
        # 2. Structure into email draft
        draft = self.chain.invoke({"transcript": transcript})
        draft["raw_transcript"] = transcript
        return draft

composer_agent = ComposerAgent()
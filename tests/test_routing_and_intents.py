import os
import sys
import io
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.intent_agent import (
    intent_classifier,
    IntentType,
    ClassificationResult,
    ExtractedEntities
)
from app.agents.supervisor_agent import supervisor_agent
from fastapi.testclient import TestClient
from app.main import app

class TestIntentClassificationAndRouting(unittest.TestCase):
    def setUp(self):
        # Reset session context between tests
        supervisor_agent.session_manager.clear("test_session")
        supervisor_agent.session_manager.clear("default")
        self.client = TestClient(app)

    # =========================================================================
    # 1. Minimum Test Cases from Section 11 Matrix
    # =========================================================================

    def test_01_general_query_ai(self):
        cmd = "What is artificial intelligence?"
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.GENERAL_QUERY)
        self.assertFalse(res.requires_clarification)

    def test_02_general_query_neural_networks(self):
        cmd = "Explain neural networks with an example."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.GENERAL_QUERY)
        self.assertFalse(res.requires_clarification)

    def test_03_compose_email_leave(self):
        cmd = "Draft an email requesting leave."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.COMPOSE_EMAIL)
        self.assertFalse(res.requires_clarification)

    def test_04_summarize_emails(self):
        cmd = "Summarize my unread emails."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.SUMMARIZE_EMAILS)
        self.assertFalse(res.requires_clarification)

    def test_05_email_search(self):
        cmd = "Find the email about my internship."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.EMAIL_SEARCH)
        self.assertFalse(res.requires_clarification)

    def test_06_schedule_event(self):
        cmd = "Schedule a meeting tomorrow at 3 PM."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.SCHEDULE_EVENT)
        self.assertFalse(res.requires_clarification)

    def test_07_calendar_retrieval_meetings_tomorrow(self):
        cmd = "What meetings do I have tomorrow?"
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.CALENDAR_VIEW)
        self.assertFalse(res.requires_clarification)

    def test_08_set_reminder(self):
        cmd = "Remind me to submit my assignment tomorrow."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.SET_REMINDER)
        self.assertFalse(res.requires_clarification)

    def test_09_document_query(self):
        cmd = "Search my uploaded PDF for project requirements."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.DOCUMENT_QUERY)
        self.assertFalse(res.requires_clarification)

    def test_10_research(self):
        cmd = "Research recent advances in generative AI."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.RESEARCH)
        self.assertFalse(res.requires_clarification)

    def test_11_conversational_productivity(self):
        cmd = "How can I improve my productivity?"
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.CONVERSATIONAL_ASSISTANT)
        self.assertFalse(res.requires_clarification)

    def test_12_context_dependent_followup(self):
        context = "User: What is artificial intelligence?\nAssistant: AI is computer systems performing intelligent tasks."
        cmd = "Explain that in simpler terms."
        res = intent_classifier._rule_based_classify(cmd, context=context)
        self.assertEqual(res.intent, IntentType.CONVERSATIONAL_ASSISTANT)
        self.assertFalse(res.requires_clarification)

    def test_13_empty_voice_transcription(self):
        cmd = ""
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.INVALID_OR_EMPTY)
        self.assertTrue(res.requires_clarification)
        self.assertIn("No speech", res.clarification_question)

    def test_14_ambiguous_command(self):
        cmd = "schedule it"
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.UNKNOWN_OR_AMBIGUOUS)
        self.assertTrue(res.requires_clarification)

    # =========================================================================
    # 2. Similar Commands with Different Intents & Email Disambiguation
    # =========================================================================

    def test_email_mention_disambiguation(self):
        # Mentioning email should NOT automatically mean compose email!
        r1 = intent_classifier._rule_based_classify("Summarize my unread emails.")
        self.assertEqual(r1.intent, IntentType.SUMMARIZE_EMAILS)

        r2 = intent_classifier._rule_based_classify("Find the email from my manager.")
        self.assertEqual(r2.intent, IntentType.EMAIL_SEARCH)

        r3 = intent_classifier._rule_based_classify("Explain what this email means.")
        self.assertIn(r3.intent, (IntentType.GENERAL_QUERY, IntentType.CONVERSATIONAL_ASSISTANT))

        r4 = intent_classifier._rule_based_classify("Draft a reply to this email.")
        self.assertEqual(r4.intent, IntentType.COMPOSE_EMAIL)

        r5 = intent_classifier._rule_based_classify("Search my emails for the internship offer.")
        self.assertEqual(r5.intent, IntentType.EMAIL_SEARCH)

    def test_calendar_creation_vs_retrieval(self):
        # Distinguish booking a meeting vs checking schedule
        r_create = intent_classifier._rule_based_classify("Create a calendar event for Friday.")
        self.assertEqual(r_create.intent, IntentType.SCHEDULE_EVENT)

        r_view = intent_classifier._rule_based_classify("What meetings are scheduled for tomorrow?")
        self.assertEqual(r_view.intent, IntentType.CALENDAR_VIEW)

        r_check = intent_classifier._rule_based_classify("Check my schedule for Friday.")
        self.assertEqual(r_check.intent, IntentType.CALENDAR_VIEW)

    def test_compound_intent_detection(self):
        cmd = "Summarize my unread emails and tell me whether any mention tomorrow's meeting."
        res = intent_classifier._rule_based_classify(cmd)
        self.assertEqual(res.intent, IntentType.SUMMARIZE_EMAILS)
        self.assertIn("MEETING_CHECK", res.secondary_intents)

    # =========================================================================
    # 3. End-to-End Orchestration & Regression Testing
    # =========================================================================

    @patch("app.agents.assistant_agent.assistant_agent.answer_general_query")
    def test_regression_general_query_does_not_compose_email(self, mock_answer):
        mock_answer.return_value = {
            "query": "What is artificial intelligence?",
            "answer": "Artificial intelligence is the simulation of human intelligence by machines.",
            "source": "general_knowledge"
        }
        
        result = supervisor_agent.orchestrate("What is artificial intelligence?", session_id="test_session")
        
        # Verify: General query must NOT generate an email draft!
        self.assertEqual(result["intent"], "GENERAL_QUERY")
        self.assertEqual(result["response_type"], "answer")
        self.assertIsNone(result["final_email"])
        self.assertIn("simulation of human intelligence", result["direct_answer"])
        mock_answer.assert_called_once()

    @patch("app.agents.composer_agent.composer_agent.compose_draft")
    def test_compose_email_orchestration(self, mock_compose):
        mock_compose.return_value = {
            "recipient_hint": "Professor",
            "subject": "Request for Extension",
            "body": "Dear Professor,\n\nI would like to request an extension on the assignment.\n\nThank you.",
            "tone": "Formal"
        }
        
        result = supervisor_agent.orchestrate("Draft an email to my professor requesting an extension.", session_id="test_session")
        
        self.assertEqual(result["intent"], "COMPOSE_EMAIL")
        self.assertEqual(result["response_type"], "email_draft")
        self.assertIsNotNone(result["final_email"])
        self.assertEqual(result["final_email"]["subject"], "Request for Extension")
        mock_compose.assert_called_once()

    @patch("app.utils.gmail_helper.gmail_helper.fetch_unread_emails")
    def test_summarize_emails_orchestration(self, mock_fetch):
        mock_fetch.return_value = [
            {"id": "1", "subject": "Quarterly Update", "body": "Q3 results are ready for review."}
        ]
        
        result = supervisor_agent.orchestrate("Summarize my unread emails.", session_id="test_session")
        
        self.assertEqual(result["intent"], "SUMMARIZE_EMAILS")
        self.assertEqual(result["response_type"], "email_summary")
        self.assertIsNone(result["final_email"])
        self.assertIn("Successfully fetched", result["action_result"])

    @patch("app.agents.reminder_agent.reminder_agent.list_events")
    def test_calendar_view_orchestration_does_not_create_event(self, mock_list):
        mock_list.return_value = {
            "status": "success",
            "summary": "Here are your scheduled meetings:\n• Project Sync at 10:00 AM",
            "events": [{"summary": "Project Sync", "start": "10:00 AM"}]
        }
        
        result = supervisor_agent.orchestrate("What meetings do I have tomorrow?", session_id="test_session")
        
        self.assertEqual(result["intent"], "CALENDAR_VIEW")
        self.assertEqual(result["response_type"], "calendar_list")
        self.assertIsNone(result["final_email"])
        self.assertIn("Project Sync", result["action_result"])

    @patch("app.agents.reminder_agent.reminder_agent.schedule_event")
    def test_schedule_event_orchestration(self, mock_sched):
        mock_sched.return_value = {
            "status": "success",
            "summary": "Meeting with Client",
            "event_link": "https://calendar.google.com/test_link"
        }
        
        result = supervisor_agent.orchestrate("Schedule a meeting tomorrow at 3 PM.", session_id="test_session")
        
        self.assertEqual(result["intent"], "SCHEDULE_EVENT")
        self.assertEqual(result["response_type"], "calendar_event")
        self.assertEqual(result["event_link"], "https://calendar.google.com/test_link")
        self.assertIsNone(result["final_email"])

    @patch("app.agents.assistant_agent.assistant_agent.answer_document_query")
    def test_document_query_orchestration(self, mock_doc):
        mock_doc.return_value = {
            "query": "Search my uploaded PDF for project requirements.",
            "answer": "The project requirements specify a multi-agent system with fast whisper speech recognition.",
            "source": "uploaded_documents",
            "context_preview": "Project requirements snippet..."
        }
        
        result = supervisor_agent.orchestrate("Search my uploaded PDF for project requirements.", session_id="test_session")
        
        self.assertEqual(result["intent"], "DOCUMENT_QUERY")
        self.assertEqual(result["response_type"], "document_answer")
        self.assertEqual(result["source"], "uploaded_documents")
        self.assertIsNone(result["final_email"])

    @patch("app.agents.assistant_agent.assistant_agent.conduct_research")
    def test_research_orchestration(self, mock_research):
        mock_research.return_value = {
            "query": "Research recent advances in generative AI.",
            "answer": "Recent advances in generative AI include reasoning models and multi-agent coordination.",
            "source": "duckduckgo_web_search",
            "context_preview": "Web snippet..."
        }
        
        result = supervisor_agent.orchestrate("Research recent advances in generative AI.", session_id="test_session")
        
        self.assertEqual(result["intent"], "RESEARCH")
        self.assertEqual(result["response_type"], "research_answer")
        self.assertEqual(result["source"], "duckduckgo_web_search")
        self.assertIsNone(result["final_email"])

    def test_ambiguous_command_triggers_clarification(self):
        result = supervisor_agent.orchestrate("schedule it", session_id="test_session")
        self.assertEqual(result["intent"], "UNKNOWN_OR_AMBIGUOUS")
        self.assertEqual(result["response_type"], "clarification")
        self.assertTrue(result["requires_clarification"])
        self.assertIsNone(result["final_email"])

    # =========================================================================
    # 4. Multi-turn Context and Session Retention
    # =========================================================================

    @patch("app.agents.assistant_agent.assistant_agent.answer_general_query")
    def test_multi_turn_context_and_no_stale_composer_contamination(self, mock_general):
        mock_general.side_effect = [
            {"query": "Explain artificial intelligence.", "answer": "AI is machine learning.", "source": "general_knowledge"},
            {"query": "Give me an example.", "answer": "For example, autonomous self-driving cars.", "source": "general_knowledge"}
        ]
        
        # Turn 1: General question
        res1 = supervisor_agent.orchestrate("Explain artificial intelligence.", session_id="context_test")
        self.assertEqual(res1["intent"], "GENERAL_QUERY")
        
        # Turn 2: Follow-up question relying on context
        res2 = supervisor_agent.orchestrate("Give me an example.", session_id="context_test")
        self.assertEqual(res2["intent"], "CONVERSATIONAL_ASSISTANT")
        self.assertEqual(res2["response_type"], "answer")
        self.assertIsNone(res2["final_email"])

    def test_email_composition_does_not_contaminate_subsequent_general_query(self):
        # Turn 1: Email composition
        with patch("app.agents.composer_agent.composer_agent.compose_draft") as mock_comp:
            mock_comp.return_value = {"recipient_hint": "Boss", "subject": "Vacation", "body": "Vacation note", "tone": "Formal"}
            res1 = supervisor_agent.orchestrate("Draft an email requesting leave.", session_id="bleed_test")
            self.assertEqual(res1["intent"], "COMPOSE_EMAIL")
            self.assertIsNotNone(res1["final_email"])

        # Turn 2: General question MUST NOT become an email draft!
        with patch("app.agents.assistant_agent.assistant_agent.answer_general_query") as mock_gen:
            mock_gen.return_value = {"query": "What is machine learning?", "answer": "ML is a subset of AI.", "source": "general_knowledge"}
            res2 = supervisor_agent.orchestrate("What is machine learning?", session_id="bleed_test")
            self.assertEqual(res2["intent"], "GENERAL_QUERY")
            self.assertEqual(res2["response_type"], "answer")
            self.assertIsNone(res2["final_email"])

    # =========================================================================
    # 5. API Endpoint Tests (Safeguards for Empty Audio & Direct Text)
    # =========================================================================

    def test_api_orchestrate_text_general_query(self):
        response = self.client.post("/api/v1/agents/orchestrate-text/", json={"command": "What is artificial intelligence?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "GENERAL_QUERY")
        self.assertEqual(data["response_type"], "answer")
        self.assertIsNone(data["final_email"])

    def test_api_orchestrate_text_empty(self):
        response = self.client.post("/api/v1/agents/orchestrate-text/", json={"command": ""})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "INVALID_OR_EMPTY")
        self.assertTrue(data["requires_clarification"])

    @patch("app.utils.voice_helper.voice_helper.transcribe_audio")
    def test_api_orchestrate_voice_empty_transcription(self, mock_transcribe):
        mock_transcribe.return_value = ""  # Simulating empty audio transcription
        
        fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....")
        response = self.client.post(
            "/api/v1/agents/orchestrate-voice/",
            files={"file": ("test.wav", fake_audio, "audio/wav")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "INVALID_OR_EMPTY")
        self.assertTrue(data["requires_clarification"])
        self.assertIn("No speech detected", data["direct_answer"])

if __name__ == "__main__":
    unittest.main()

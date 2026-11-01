export type IntentType =
  | "GENERAL_QUERY"
  | "COMPOSE_EMAIL"
  | "SUMMARIZE_EMAILS"
  | "EMAIL_SEARCH"
  | "SCHEDULE_EVENT"
  | "CALENDAR_VIEW"
  | "SET_REMINDER"
  | "DOCUMENT_QUERY"
  | "RESEARCH"
  | "CONVERSATIONAL_ASSISTANT"
  | "UNKNOWN_OR_AMBIGUOUS"
  | "INVALID_OR_EMPTY";

export type ResponseType =
  | "answer"
  | "email_draft"
  | "email_summary"
  | "email_search"
  | "calendar_event"
  | "calendar_list"
  | "reminder"
  | "document_answer"
  | "research_answer"
  | "clarification";

export interface EmailDraft {
  recipient_hint?: string;
  subject?: string;
  body?: string;
  tone?: string;
  raw_transcript?: string;
}

export interface CalendarEventItem {
  id?: string;
  summary?: string;
  start?: { dateTime?: string; date?: string };
  end?: { dateTime?: string; date?: string };
  description?: string;
  htmlLink?: string;
}

export interface EmailItem {
  id: string;
  subject: string;
  sender?: string;
  date?: string;
  body?: string;
  category?: string;
  summary?: string;
}

export interface AgentResponse {
  intent: string;
  response_type: ResponseType | string;
  direct_answer?: string | null;
  action_result?: string | null;
  final_email?: EmailDraft | null;
  event_link?: string | null;
  data?: any;
  source?: string | null;
  confidence?: number;
  requires_clarification?: boolean;
  clarification_question?: string | null;
  raw_transcript?: string | null;
  context_preview?: string | null;
}

export interface BackendHealth {
  status: string;
  project: string;
  version: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isVoice?: boolean;
  rawTranscript?: string;
  status?: "sending" | "sent" | "error";
  responsePayload?: AgentResponse;
  error?: string;
}

export type VoiceState =
  | "idle"
  | "recording"
  | "processing"
  | "thinking"
  | "responding"
  | "error";

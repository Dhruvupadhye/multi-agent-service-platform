import {
  AgentResponse,
  BackendHealth,
  CalendarEventItem,
  CreateCalendarEventRequest,
  CreateReminderRequest,
  DocumentItem,
  DocumentUploadResponse,
  EmailDraft,
  EmailItem,
  EmailSummaryItem,
  ReminderItem,
  SendEmailRequest,
  SendEmailResponse,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

const DEFAULT_TIMEOUT_MS = 60000; // 60 seconds for agent / speech orchestration

export class ApiError extends Error {
  status?: number;
  data?: any;

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } catch (error: any) {
    if (error.name === "AbortError") {
      throw new ApiError(
        `Request timed out after ${timeoutMs / 1000} seconds. The backend may still be processing.`,
        408
      );
    }
    throw new ApiError(
      `Network connection failed. Ensure FastAPI is running at ${API_BASE_URL}.`,
      0
    );
  } finally {
    clearTimeout(id);
  }
}

export const apiClient = {
  getBaseUrl(): string {
    return API_BASE_URL;
  },

  /**
   * Health check to test backend connectivity
   */
  async checkHealth(): Promise<BackendHealth> {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/health`,
      { method: "GET" },
      5000
    );

    if (!res.ok) {
      throw new ApiError(
        `Backend health check failed (${res.status} ${res.statusText})`,
        res.status
      );
    }
    return res.json();
  },

  /**
   * Send a typed natural language command to the LangGraph supervisor
   */
  async sendTextCommand(
    command: string,
    sessionId: string = "default"
  ): Promise<AgentResponse> {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/agents/orchestrate-text/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          command,
          session_id: sessionId,
        }),
      }
    );

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      throw new ApiError(
        `Failed to execute command: ${res.statusText} (${errText || res.status})`,
        res.status,
        errText
      );
    }

    return res.json();
  },

  /**
   * Upload an audio recording to the existing FastAPI voice orchestration endpoint
   */
  async sendVoiceCommand(
    audioBlob: Blob,
    filename: string = "voice_command.wav",
    sessionId: string = "default"
  ): Promise<AgentResponse> {
    const formData = new FormData();
    const safeFilename = filename.endsWith(".wav") ? filename : `${filename}.wav`;
    formData.append("file", audioBlob, safeFilename);

    const url = new URL(`${API_BASE_URL}/api/v1/agents/orchestrate-voice/`);
    url.searchParams.set("session_id", sessionId);

    const res = await fetchWithTimeout(url.toString(), {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      throw new ApiError(
        `Voice command failed: ${res.statusText} (${errText || res.status})`,
        res.status,
        errText
      );
    }

    return res.json();
  },

  // ----------------- Email Workflows -----------------

  /**
   * Retrieve emails with metadata
   */
  async listEmails(query: string = "", maxResults: number = 10): Promise<EmailItem[]> {
    const url = new URL(`${API_BASE_URL}/api/v1/emails/list`);
    if (query) url.searchParams.set("q", query);
    url.searchParams.set("max_results", maxResults.toString());

    const res = await fetchWithTimeout(url.toString(), { method: "GET" });
    if (!res.ok) {
      throw new ApiError(`Failed to load emails (${res.status})`, res.status);
    }
    const data = await res.json();
    return data.data || [];
  },

  /**
   * Compose an email draft using AI
   */
  async composeEmail(prompt: string, recipientHint?: string): Promise<EmailDraft> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/emails/compose`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        recipient_hint: recipientHint,
      }),
    });

    if (!res.ok) {
      const err = await res.text().catch(() => "");
      throw new ApiError(`Draft generation failed: ${err || res.statusText}`, res.status);
    }
    const data = await res.json();
    return data.draft;
  },

  /**
   * Send an email via Gmail API
   */
  async sendEmail(payload: SendEmailRequest): Promise<SendEmailResponse> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/emails/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(err.detail || "Failed to send email", res.status);
    }
    return res.json();
  },

  /**
   * Run the email fetch, spam classification, vector storage, and summary digest workflow
   */
  async fetchAndProcessEmails(): Promise<{
    status: string;
    processed_count: number;
    data: EmailSummaryItem[];
  }> {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/emails/fetch-and-process`,
      { method: "POST" }
    );

    if (!res.ok) {
      throw new ApiError(`Email summary processing failed (${res.status})`, res.status);
    }
    return res.json();
  },

  // ----------------- Calendar Workflows -----------------

  /**
   * Retrieve upcoming calendar events
   */
  async listCalendarEvents(timeMin?: string, maxResults: number = 20): Promise<CalendarEventItem[]> {
    const url = new URL(`${API_BASE_URL}/api/v1/calendar/events`);
    if (timeMin) url.searchParams.set("time_min", timeMin);
    url.searchParams.set("max_results", maxResults.toString());

    const res = await fetchWithTimeout(url.toString(), { method: "GET" });
    if (!res.ok) {
      throw new ApiError(`Failed to load calendar events (${res.status})`, res.status);
    }
    const data = await res.json();
    return data.events || [];
  },

  /**
   * Schedule a new calendar event
   */
  async createCalendarEvent(payload: CreateCalendarEventRequest): Promise<any> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/calendar/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(err.detail || "Failed to schedule event", res.status);
    }
    return res.json();
  },

  // ----------------- Reminders Workflows -----------------

  /**
   * Retrieve list of reminders
   */
  async listReminders(): Promise<ReminderItem[]> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/reminders/list`, {
      method: "GET",
    });

    if (!res.ok) {
      throw new ApiError(`Failed to load reminders (${res.status})`, res.status);
    }
    const data = await res.json();
    return data.reminders || [];
  },

  /**
   * Create a new reminder with optional WhatsApp notification
   */
  async createReminder(payload: CreateReminderRequest): Promise<any> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/reminders/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(err.detail || "Failed to set reminder", res.status);
    }
    return res.json();
  },

  // ----------------- Documents Workflows (RAG) -----------------

  /**
   * Retrieve indexed documents
   */
  async listDocuments(): Promise<DocumentItem[]> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/media/documents`, {
      method: "GET",
    });

    if (!res.ok) {
      throw new ApiError(`Failed to load documents (${res.status})`, res.status);
    }
    const data = await res.json();
    return data.documents || [];
  },

  /**
   * Upload a PDF document for indexing and summarization
   */
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/media/upload-document/`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(err.detail || `Upload failed (${res.status})`, res.status);
    }

    return res.json();
  },

  /**
   * Directly ask the RAG document assistant
   */
  async askAssistant(query: string): Promise<any> {
    const url = new URL(`${API_BASE_URL}/api/v1/agents/ask-assistant/`);
    url.searchParams.set("query", query);

    const res = await fetchWithTimeout(url.toString(), {
      method: "GET",
    });

    if (!res.ok) {
      throw new ApiError(`Assistant query failed (${res.status})`, res.status);
    }

    return res.json();
  },
};

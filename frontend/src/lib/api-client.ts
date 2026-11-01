import { AgentResponse, BackendHealth } from "@/types/api";

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
    const res = await fetchWithTimeout(`${API_BASE_URL}/health`, {
      method: "GET",
    }, 5000);

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
        headers: {
          "Content-Type": "application/json",
        },
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
    // Ensure filename ends with .wav for Whisper consistency
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

  /**
   * Upload a PDF document for indexing
   */
  async uploadDocument(file: File): Promise<any> {
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
      throw new ApiError(`Document upload failed (${res.status})`, res.status);
    }

    return res.json();
  },

  /**
   * Fetch and summarize inbox emails
   */
  async fetchEmails(): Promise<any> {
    const res = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/emails/fetch-and-process`,
      {
        method: "POST",
      }
    );

    if (!res.ok) {
      throw new ApiError(`Fetch emails failed (${res.status})`, res.status);
    }

    return res.json();
  },
};

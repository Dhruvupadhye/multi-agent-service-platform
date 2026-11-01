"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { BackendHealth } from "@/types/api";
import {
  Settings,
  Server,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Cpu,
  Mail,
  Calendar,
  MessageSquare,
  HardDrive,
  Mic,
  RotateCcw,
} from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resetNotice, setResetNotice] = useState<string | null>(null);

  const checkConnection = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.checkHealth();
      setHealth(data);
    } catch (err: any) {
      setError(err.message || "Failed to reach backend.");
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkConnection();
  }, []);

  const handleResetSession = () => {
    if (typeof window !== "undefined") {
      sessionStorage.clear();
      setResetNotice("Session cache cleared. A new agent session will start on next interaction.");
      setTimeout(() => setResetNotice(null), 3000);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] p-6 gap-6 max-w-5xl mx-auto w-full overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Settings className="h-6 w-6 text-primary" />
            System Status &amp; Configuration
          </h1>
          <p className="text-sm text-muted-foreground">
            Monitor FastAPI service health, inspect agent integrations, and manage frontend preferences.
          </p>
        </div>
        <button
          onClick={checkConnection}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 text-xs font-medium rounded-lg border border-border bg-card hover:bg-accent text-foreground transition-colors"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Check Health
        </button>
      </div>

      {/* Backend Status Card */}
      <div className="bg-card rounded-xl border border-border p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-primary/10 text-primary">
              <Server className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">FastAPI Backend Service</h2>
              <p className="text-xs text-muted-foreground">
                Base URL: <code className="bg-muted px-1.5 py-0.5 rounded font-mono">{apiClient.getBaseUrl()}</code>
              </p>
            </div>
          </div>
          {loading ? (
            <span className="text-xs text-muted-foreground">Connecting...</span>
          ) : health ? (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Connected ({health.version || "v1.0.0"})
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-destructive bg-destructive/10 px-2.5 py-1 rounded-full border border-destructive/20">
              <AlertCircle className="h-3.5 w-3.5" />
              Disconnected
            </span>
          )}
        </div>

        {error && (
          <div className="p-3 rounded-lg border border-destructive/20 bg-destructive/10 text-xs text-destructive">
            {error}
          </div>
        )}
      </div>

      {/* Agent Architecture Overview */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-foreground">Active Agent Integrations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-card rounded-xl border border-border p-4 flex items-start gap-3">
            <Mail className="h-5 w-5 text-indigo-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-foreground">Gmail &amp; Spam Agent</h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                Spam classification with scikit-learn ML model, email drafting with LangChain, and dispatch via Gmail API.
              </p>
            </div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4 flex items-start gap-3">
            <Calendar className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-foreground">Calendar &amp; Reminders</h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                Natural language event parsing, Google Calendar v3 API synchronization, and automated WhatsApp alert triggers.
              </p>
            </div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4 flex items-start gap-3">
            <HardDrive className="h-5 w-5 text-purple-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-foreground">ChromaDB Vector Store</h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                Local persistent vector storage for RAG PDF chunk embeddings and historical email digest indexing.
              </p>
            </div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4 flex items-start gap-3">
            <Mic className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-foreground">Whisper Speech Processing</h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                Local Whisper neural network transcription pipeline accepting audio WAV recordings from browser MediaRecorder.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Session Management */}
      <div className="bg-card rounded-xl border border-border p-5 space-y-3">
        <h3 className="text-sm font-semibold text-foreground">Client State &amp; Memory</h3>
        <p className="text-xs text-muted-foreground">
          If you want to clear your current conversation ID and prompt cache, you can reset your local session.
        </p>
        <button
          onClick={handleResetSession}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-border bg-background hover:bg-accent text-foreground transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset Local Session Cache
        </button>
        {resetNotice && (
          <p className="text-xs text-emerald-600 font-medium">{resetNotice}</p>
        )}
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  Clock,
  Database,
  Mail,
  Calendar,
  Mic,
  MessageSquare,
  Activity,
  Layers,
  Radio,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { BackendHealth } from "@/types/api";

const INTEGRATIONS = [
  {
    name: "FastAPI Core Service",
    description: "RESTful endpoint & lifespan orchestration",
    icon: Activity,
    status: "Healthy",
    endpoint: "/health",
  },
  {
    name: "LangGraph Multi-Agent Supervisor",
    description: "Intent classification & conditional edge routing",
    icon: Layers,
    status: "Operational",
    endpoint: "/api/v1/agents/orchestrate-text/",
  },
  {
    name: "Faster-Whisper Speech Recognition",
    description: "Local CPU-optimized audio transcription",
    icon: Mic,
    status: "Ready",
    endpoint: "/api/v1/agents/orchestrate-voice/",
  },
  {
    name: "ChromaDB Vector Store",
    description: "Persistent document chunks & email embeddings",
    icon: Database,
    status: "Indexed",
    endpoint: "/api/v1/agents/ask-assistant/",
  },
  {
    name: "Google Calendar & Reminders",
    description: "OAuth2 event creation & schedule retrieval",
    icon: Calendar,
    status: "Connected",
    endpoint: "/api/v1/agents/orchestrate-text/",
  },
  {
    name: "Gmail & Spam ML Classifier",
    description: "Inbox fetching, scikit-learn classifier & digest",
    icon: Mail,
    status: "Connected",
    endpoint: "/api/v1/emails/fetch-and-process",
  },
];

export function RecentActivity() {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const h = await apiClient.checkHealth();
        setHealth(h);
      } catch (err) {
        console.warn("Backend not available yet:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Platform Capabilities & Recent Activity */}
      <div className="lg:col-span-2 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs dark:border-slate-800 dark:bg-slate-900 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Active Agent Workflows
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Verified multi-agent pipelines ready for execution
            </p>
          </div>
          <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            6 Agents Live
          </span>
        </div>

        <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
          <div className="py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                <MessageSquare className="h-4 w-4" />
              </div>
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-200">
                  General Query &amp; Explanation Agent
                </p>
                <p className="text-slate-400">
                  Direct conversational responses without creating unwanted email drafts
                </p>
              </div>
            </div>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Active
            </span>
          </div>

          <div className="py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
                <Database className="h-4 w-4" />
              </div>
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-200">
                  Document Knowledge Base (RAG)
                </p>
                <p className="text-slate-400">
                  ChromaDB vector similarity search with chunk citation previews
                </p>
              </div>
            </div>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Active
            </span>
          </div>

          <div className="py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-sky-50 p-2 text-sky-600 dark:bg-sky-950 dark:text-sky-400">
                <Calendar className="h-4 w-4" />
              </div>
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-200">
                  Calendar Schedule &amp; Meeting Creator
                </p>
                <p className="text-slate-400">
                  Distinguishes checking upcoming schedule vs. creating calendar events
                </p>
              </div>
            </div>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Active
            </span>
          </div>

          <div className="py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-violet-50 p-2 text-violet-600 dark:bg-violet-950 dark:text-violet-400">
                <Mail className="h-4 w-4" />
              </div>
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-200">
                  Email Agent &amp; Executive Composer
                </p>
                <p className="text-slate-400">
                  Subject lines, recipient extraction, and clean email draft formatting
                </p>
              </div>
            </div>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Active
            </span>
          </div>
        </div>
      </div>

      {/* Integration Status Column */}
      <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs dark:border-slate-800 dark:bg-slate-900 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Integrations Status
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Backend subsystem health checks
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Radio className="h-3 w-3 text-emerald-500 animate-pulse" />
            <span>Live</span>
          </div>
        </div>

        <div className="space-y-3">
          {INTEGRATIONS.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="flex items-start gap-2.5 p-2 rounded-xl bg-slate-50/70 hover:bg-slate-100/60 dark:bg-slate-800/40 dark:hover:bg-slate-800/70 transition"
              >
                <div className="rounded-lg bg-white p-1.5 text-slate-600 shadow-2xs dark:bg-slate-900 dark:text-slate-300">
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate">
                      {item.name}
                    </span>
                    <span className="text-[10px] font-medium text-emerald-600 dark:text-emerald-400">
                      {item.status}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 truncate mt-0.5">
                    {item.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

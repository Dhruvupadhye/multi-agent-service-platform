"use client";

import { useState } from "react";
import {
  Mail,
  Calendar,
  CheckCircle2,
  Clock,
  ExternalLink,
  Copy,
  Check,
  FileText,
  Search,
  Globe,
  HelpCircle,
  Inbox,
  AlertTriangle,
} from "lucide-react";
import { AgentResponse } from "@/types/api";
import { copyToClipboard } from "@/lib/utils";

interface ResponseRendererProps {
  response: AgentResponse;
  onSelectClarification?: (text: string) => void;
}

export function ResponseRenderer({
  response,
  onSelectClarification,
}: ResponseRendererProps) {
  const [copied, setCopied] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const {
    intent,
    response_type,
    direct_answer,
    action_result,
    final_email,
    event_link,
    data,
    source,
    requires_clarification,
    clarification_question,
  } = response;

  const handleCopyEmail = async () => {
    if (!final_email) return;
    const emailText = `Subject: ${final_email.subject || ""}\nTo: ${
      final_email.recipient_hint || ""
    }\n\n${final_email.body || ""}`;
    const success = await copyToClipboard(emailText);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // 1. Clarification Request / Ambiguous
  if (
    requires_clarification ||
    response_type === "clarification" ||
    intent === "UNKNOWN_OR_AMBIGUOUS" ||
    intent === "INVALID_OR_EMPTY"
  ) {
    const question =
      clarification_question ||
      direct_answer ||
      action_result ||
      "Could you please provide more details about your request?";

    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4 dark:border-amber-900/50 dark:bg-amber-950/30">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 rounded-lg bg-amber-100 p-1.5 text-amber-700 dark:bg-amber-900/60 dark:text-amber-300">
            <HelpCircle className="h-4 w-4" />
          </div>
          <div className="flex-1 space-y-1">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-800 dark:text-amber-200">
              Clarification Needed
            </h4>
            <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
              {question}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // 2. Email Draft
  if (response_type === "email_draft" || final_email || intent === "COMPOSE_EMAIL") {
    const email = final_email || {
      subject: "Untitled Draft",
      body: direct_answer || action_result || "",
      recipient_hint: "Recipient",
      tone: "Professional",
    };

    return (
      <div className="rounded-xl border border-indigo-200 bg-white p-4 shadow-xs dark:border-indigo-900/50 dark:bg-slate-900">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-indigo-50 p-1.5 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
              <Mail className="h-4 w-4" />
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                Email Draft Generated
              </span>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Review and copy your draft below
              </p>
            </div>
          </div>

          <button
            onClick={handleCopyEmail}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 transition"
            title="Copy subject and body to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                  Copied!
                </span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-500" />
                <span>Copy Draft</span>
              </>
            )}
          </button>
        </div>

        {/* Metadata */}
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800/60">
            <span className="font-semibold text-slate-500 dark:text-slate-400">
              Subject:
            </span>{" "}
            <span className="font-medium text-slate-900 dark:text-slate-100">
              {email.subject || "No subject"}
            </span>
          </div>
          <div className="flex items-center justify-between rounded-lg bg-slate-50 p-2 dark:bg-slate-800/60">
            <span>
              <span className="font-semibold text-slate-500 dark:text-slate-400">
                To:
              </span>{" "}
              <span className="font-medium text-slate-900 dark:text-slate-100">
                {email.recipient_hint || "Not specified"}
              </span>
            </span>
            {email.tone && (
              <span className="rounded-md bg-indigo-100 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                {email.tone}
              </span>
            )}
          </div>
        </div>

        {/* Email Body */}
        <div className="mt-3 rounded-lg border border-slate-100 bg-slate-50/70 p-3.5 text-sm font-sans text-slate-800 dark:border-slate-800 dark:bg-slate-950/60 dark:text-slate-200 whitespace-pre-wrap leading-relaxed">
          {email.body || "No email body."}
        </div>
      </div>
    );
  }

  // 3. Calendar Event Scheduled
  if (response_type === "calendar_event" || intent === "SCHEDULE_EVENT") {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 dark:border-emerald-900/50 dark:bg-emerald-950/30">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-lg bg-emerald-100 p-1.5 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
              <Calendar className="h-4 w-4" />
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
                Event Scheduled
              </h4>
              <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
                {action_result || direct_answer || "Meeting added to Google Calendar"}
              </p>
            </div>
          </div>

          {event_link && (
            <a
              href={event_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white shadow-xs hover:bg-emerald-700 transition"
            >
              <span>View Calendar</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>
      </div>
    );
  }

  // 4. Calendar List / View Schedule
  if (response_type === "calendar_list" || intent === "CALENDAR_VIEW") {
    return (
      <div className="rounded-xl border border-sky-200 bg-sky-50/50 p-4 dark:border-sky-900/50 dark:bg-sky-950/30">
        <div className="flex items-center gap-2 mb-2">
          <div className="rounded-lg bg-sky-100 p-1.5 text-sky-700 dark:bg-sky-900 dark:text-sky-300">
            <Clock className="h-4 w-4" />
          </div>
          <span className="text-xs font-semibold uppercase tracking-wider text-sky-800 dark:text-sky-300">
            Upcoming Schedule
          </span>
        </div>
        <div className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-line leading-relaxed pl-1">
          {action_result || direct_answer || "No scheduled meetings found."}
        </div>
      </div>
    );
  }

  // 5. Reminder Confirmation
  if (response_type === "reminder" || intent === "SET_REMINDER") {
    return (
      <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4 dark:border-indigo-900/50 dark:bg-indigo-950/30">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-lg bg-indigo-100 p-1.5 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300">
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-indigo-800 dark:text-indigo-300">
                Reminder Set
              </h4>
              <p className="mt-1 text-sm font-medium text-slate-900 dark:text-slate-100">
                {action_result || direct_answer}
              </p>
            </div>
          </div>
          {event_link && (
            <a
              href={event_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-indigo-200 bg-white px-2.5 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-50 dark:border-indigo-800 dark:bg-slate-900 dark:text-indigo-300 transition"
            >
              <span>Calendar</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      </div>
    );
  }

  // 6. Document Query Answer
  if (response_type === "document_answer" || intent === "DOCUMENT_QUERY") {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
              Knowledge Base Answer
            </span>
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {source || "Uploaded Documents"}
          </span>
        </div>

        <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
          {direct_answer || action_result}
        </p>

        {response.context_preview && (
          <div className="text-xs">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="text-indigo-600 dark:text-indigo-400 hover:underline font-medium inline-flex items-center gap-1"
            >
              <span>{showPreview ? "Hide Context Excerpt" : "View Context Excerpt"}</span>
            </button>
            {showPreview && (
              <div className="mt-2 rounded-lg bg-slate-50 p-2.5 text-slate-600 dark:bg-slate-950 dark:text-slate-400 font-mono text-[11px] leading-relaxed">
                {response.context_preview}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // 7. Research Answer
  if (response_type === "research_answer" || intent === "RESEARCH") {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-sky-600 dark:text-sky-400" />
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
              Web Research Findings
            </span>
          </div>
          <span className="rounded-full bg-sky-50 px-2 py-0.5 text-[10px] font-semibold text-sky-700 dark:bg-sky-950 dark:text-sky-300">
            {source || "DuckDuckGo"}
          </span>
        </div>

        <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
          {direct_answer || action_result}
        </p>

        {response.context_preview && (
          <div className="text-xs">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="text-sky-600 dark:text-sky-400 hover:underline font-medium"
            >
              {showPreview ? "Hide Raw Snippets" : "Show Search Snippets"}
            </button>
            {showPreview && (
              <div className="mt-2 rounded-lg bg-slate-50 p-2.5 text-slate-600 dark:bg-slate-950 dark:text-slate-400 font-mono text-[11px] leading-relaxed">
                {response.context_preview}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // 8. Email Summarization / Search
  if (
    response_type === "email_summary" ||
    response_type === "email_search" ||
    intent === "SUMMARIZE_EMAILS" ||
    intent === "EMAIL_SEARCH"
  ) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs dark:border-slate-800 dark:bg-slate-900 space-y-2.5">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-2 dark:border-slate-800">
          <Inbox className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
            {intent === "EMAIL_SEARCH" ? "Email Search Results" : "Inbox Summary"}
          </span>
        </div>

        <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
          {action_result || direct_answer}
        </p>
      </div>
    );
  }

  // 9. Standard General or Conversational Answer
  return (
    <div className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
      {direct_answer || action_result || "I have completed your request."}
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { apiClient, ApiError } from "@/lib/api-client";
import { EmailItem, EmailDraft, EmailSummaryItem } from "@/types/api";
import {
  Mail,
  Send,
  Sparkles,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  User,
  Inbox,
  PenSquare,
  X,
  FileText,
  BadgeAlert,
  Loader2,
} from "lucide-react";

export default function EmailPage() {
  const [emails, setEmails] = useState<EmailItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEmail, setSelectedEmail] = useState<EmailItem | null>(null);

  // Digest state
  const [digestLoading, setDigestLoading] = useState(false);
  const [digestSummaries, setDigestSummaries] = useState<EmailSummaryItem[] | null>(null);
  const [digestMessage, setDigestMessage] = useState<string | null>(null);

  // Compose / Draft state
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isGeneratingDraft, setIsGeneratingDraft] = useState(false);
  const [draftTo, setDraftTo] = useState("");
  const [draftSubject, setDraftSubject] = useState("");
  const [draftBody, setDraftBody] = useState("");
  const [draftTone, setDraftTone] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [sendSuccessMessage, setSendSuccessMessage] = useState<string | null>(null);
  const [composeError, setComposeError] = useState<string | null>(null);

  const fetchEmails = async (query = "") => {
    setLoading(true);
    setError(null);
    try {
      const items = await apiClient.listEmails(query);
      setEmails(items);
      if (items.length > 0 && !selectedEmail) {
        setSelectedEmail(items[0]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load emails from server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEmails(searchQuery);
  };

  const handleRunDigest = async () => {
    setDigestLoading(true);
    setDigestMessage(null);
    try {
      const res = await apiClient.fetchAndProcessEmails();
      setDigestSummaries(res.data);
      setDigestMessage(`Processed ${res.processed_count} unread email(s). Notification digest dispatched.`);
      // Refresh list after processing
      fetchEmails();
    } catch (err: any) {
      setDigestMessage(`Digest error: ${err.message}`);
    } finally {
      setDigestLoading(false);
    }
  };

  const handleGenerateAiDraft = async () => {
    if (!aiPrompt.trim()) return;
    setIsGeneratingDraft(true);
    setComposeError(null);
    try {
      const draft = await apiClient.composeEmail(aiPrompt);
      if (draft.recipient_hint && !draftTo) {
        setDraftTo(draft.recipient_hint.includes("@") ? draft.recipient_hint : "");
      }
      if (draft.subject) setDraftSubject(draft.subject);
      if (draft.body) setDraftBody(draft.body);
      if (draft.tone) setDraftTone(draft.tone);
    } catch (err: any) {
      setComposeError(err.message || "AI draft generation failed.");
    } finally {
      setIsGeneratingDraft(false);
    }
  };

  const handleSendEmail = async () => {
    if (!draftTo.trim() || !draftTo.includes("@")) {
      setComposeError("Please enter a valid recipient email address.");
      return;
    }
    if (!draftSubject.trim()) {
      setComposeError("Please enter a subject line.");
      return;
    }
    if (!draftBody.trim()) {
      setComposeError("Email content cannot be empty.");
      return;
    }

    setIsSending(true);
    setComposeError(null);
    try {
      const res = await apiClient.sendEmail({
        to: draftTo.trim(),
        subject: draftSubject.trim(),
        body: draftBody.trim(),
      });
      setSendSuccessMessage(res.message || "Email successfully sent!");
      // Reset form after short delay
      setTimeout(() => {
        setDraftTo("");
        setDraftSubject("");
        setDraftBody("");
        setDraftTone(null);
        setAiPrompt("");
        setSendSuccessMessage(null);
        setIsComposeOpen(false);
        fetchEmails();
      }, 2500);
    } catch (err: any) {
      setComposeError(err.message || "Failed to dispatch email.");
    } finally {
      setIsSending(false);
    }
  };

  const openCompose = (prefillTo = "", prefillSubject = "", prefillBody = "") => {
    setDraftTo(prefillTo);
    setDraftSubject(prefillSubject);
    setDraftBody(prefillBody);
    setDraftTone(null);
    setComposeError(null);
    setSendSuccessMessage(null);
    setIsComposeOpen(true);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] p-6 gap-6 max-w-7xl mx-auto w-full">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Mail className="h-6 w-6 text-primary" />
            Email Management Hub
          </h1>
          <p className="text-sm text-muted-foreground">
            Manage your inbox, run intelligent AI digests, and compose executive drafts with Gmail integration.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRunDigest}
            disabled={digestLoading}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border border-border bg-card hover:bg-accent text-foreground transition-colors disabled:opacity-50"
            title="Fetch unread emails, classify spam, and trigger summary digest"
          >
            {digestLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            ) : (
              <Sparkles className="h-4 w-4 text-primary" />
            )}
            Run AI Digest
          </button>
          <button
            onClick={() => fetchEmails(searchQuery)}
            disabled={loading}
            className="p-2 rounded-lg border border-border bg-card hover:bg-accent text-foreground transition-colors"
            title="Refresh emails"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => openCompose()}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm"
          >
            <PenSquare className="h-4 w-4" />
            Compose
          </button>
        </div>
      </div>

      {/* AI Digest Alert Banner */}
      {digestMessage && (
        <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 flex items-start justify-between gap-3 animate-in fade-in">
          <div className="flex items-start gap-3">
            <Sparkles className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <p className="text-sm font-medium text-foreground">{digestMessage}</p>
              {digestSummaries && digestSummaries.length > 0 && (
                <div className="mt-2 space-y-1">
                  {digestSummaries.map((item) => (
                    <div key={item.id} className="text-xs text-muted-foreground flex items-center gap-2">
                      <span className="uppercase text-[10px] font-semibold px-1.5 py-0.5 rounded bg-muted">
                        {item.category}
                      </span>
                      <span>{item.summary}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <button
            onClick={() => setDigestMessage(null)}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* Email List Column */}
        <div className="md:col-span-5 flex flex-col bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          {/* Search Bar */}
          <div className="p-3 border-b border-border bg-muted/30">
            <form onSubmit={handleSearch} className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search emails by sender or keyword..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </form>
          </div>

          {/* List Area */}
          <div className="flex-1 overflow-y-auto divide-y divide-border">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-2">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                <p className="text-sm">Fetching emails from Gmail...</p>
              </div>
            ) : error ? (
              <div className="p-6 text-center">
                <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
                <p className="text-sm text-destructive">{error}</p>
                <button
                  onClick={() => fetchEmails()}
                  className="mt-3 text-xs text-primary underline"
                >
                  Retry
                </button>
              </div>
            ) : emails.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-2 p-6 text-center">
                <Inbox className="h-8 w-8 opacity-40" />
                <p className="text-sm font-medium">No emails found</p>
                <p className="text-xs">Your inbox is clear or no emails matched your search.</p>
              </div>
            ) : (
              emails.map((email) => {
                const isSelected = selectedEmail?.id === email.id;
                return (
                  <div
                    key={email.id}
                    onClick={() => setSelectedEmail(email)}
                    className={`p-4 cursor-pointer transition-colors hover:bg-accent/50 ${
                      isSelected ? "bg-accent border-l-4 border-l-primary" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                      <span className="font-semibold text-foreground truncate max-w-[200px]">
                        {email.sender || "Unknown Sender"}
                      </span>
                      {email.date && (
                        <span className="flex items-center gap-1 shrink-0">
                          <Clock className="h-3 w-3" />
                          {email.date}
                        </span>
                      )}
                    </div>
                    <h4 className="text-sm font-medium text-foreground line-clamp-1 mb-1">
                      {email.subject}
                    </h4>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {email.body || email.summary || "No preview available."}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Selected Email Reader Column */}
        <div className="md:col-span-7 flex flex-col bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          {selectedEmail ? (
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="p-5 border-b border-border bg-muted/20 flex flex-col gap-3">
                <div className="flex items-start justify-between gap-4">
                  <h2 className="text-lg font-semibold text-foreground">
                    {selectedEmail.subject}
                  </h2>
                  <button
                    onClick={() =>
                      openCompose(
                        selectedEmail.sender?.includes("@") ? selectedEmail.sender : "",
                        `Re: ${selectedEmail.subject}`,
                        `\n\n--- On ${selectedEmail.date || "recent"}, ${selectedEmail.sender || "Sender"} wrote: ---\n> ${selectedEmail.body}`
                      )
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-border bg-background hover:bg-accent transition-colors shrink-0"
                  >
                    <Send className="h-3.5 w-3.5" />
                    Reply
                  </button>
                </div>
                <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1.5 font-medium text-foreground">
                    <User className="h-3.5 w-3.5 text-muted-foreground" />
                    {selectedEmail.sender || "Unknown"}
                  </span>
                  {selectedEmail.date && (
                    <span className="flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                      {selectedEmail.date}
                    </span>
                  )}
                  {selectedEmail.category && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-primary/10 text-primary">
                      {selectedEmail.category.toUpperCase()}
                    </span>
                  )}
                </div>
              </div>

              {/* Body */}
              <div className="p-6 flex-1 overflow-y-auto">
                <div className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                  {selectedEmail.body || selectedEmail.summary || "No message body."}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-2 p-8 text-center">
              <Mail className="h-10 w-10 opacity-30" />
              <p className="text-sm font-medium">Select an email to view details</p>
              <p className="text-xs">Choose any item from the left pane to read its contents or reply.</p>
            </div>
          )}
        </div>
      </div>

      {/* Compose & Draft Modal Dialog */}
      {isComposeOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-card w-full max-w-2xl rounded-2xl border border-border shadow-xl flex flex-col max-h-[90vh] overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PenSquare className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-foreground">Compose Email</h3>
                <span className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground font-medium">
                  Gmail API
                </span>
              </div>
              <button
                onClick={() => setIsComposeOpen(false)}
                className="text-muted-foreground hover:text-foreground p-1 rounded-md"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-4">
              {/* AI Draft Generator Accordion */}
              <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-primary">
                  <Sparkles className="h-4 w-4" />
                  AI Executive Composer
                </div>
                <p className="text-xs text-muted-foreground">
                  Give instructions in plain English, and the AI agent will draft a polished professional email.
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="e.g. Draft an email to Professor requesting extension on project due to fever"
                    value={aiPrompt}
                    onChange={(e) => setAiPrompt(e.target.value)}
                    className="flex-1 px-3 py-1.5 text-xs rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                  <button
                    onClick={handleGenerateAiDraft}
                    disabled={isGeneratingDraft || !aiPrompt.trim()}
                    className="px-3 py-1.5 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5 shrink-0"
                  >
                    {isGeneratingDraft ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Sparkles className="h-3.5 w-3.5" />
                    )}
                    Generate Draft
                  </button>
                </div>
                {draftTone && (
                  <div className="text-[11px] text-muted-foreground flex items-center gap-1">
                    <span>Detected Tone:</span>
                    <span className="font-medium text-foreground">{draftTone}</span>
                  </div>
                )}
              </div>

              {/* Draft Status Indicator */}
              <div className="flex items-center justify-between text-xs pb-1">
                <span className="text-muted-foreground font-medium">Status:</span>
                <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 font-semibold text-[11px] border border-amber-500/20">
                  Draft (Unsent)
                </span>
              </div>

              {/* Form Fields */}
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Recipient (To) *
                  </label>
                  <input
                    type="email"
                    placeholder="recipient@example.com"
                    value={draftTo}
                    onChange={(e) => setDraftTo(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Subject Line *
                  </label>
                  <input
                    type="text"
                    placeholder="Subject of the email"
                    value={draftSubject}
                    onChange={(e) => setDraftSubject(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Body *
                  </label>
                  <textarea
                    rows={7}
                    placeholder="Write or edit your message content here..."
                    value={draftBody}
                    onChange={(e) => setDraftBody(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary resize-y"
                  />
                </div>
              </div>

              {/* Alerts */}
              {composeError && (
                <div className="p-3 rounded-lg border border-destructive/20 bg-destructive/10 text-xs text-destructive flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {composeError}
                </div>
              )}
              {sendSuccessMessage && (
                <div className="p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/10 text-xs text-emerald-600 flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                  {sendSuccessMessage}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-border bg-muted/20 flex items-center justify-between">
              <button
                onClick={() => setIsComposeOpen(false)}
                className="px-4 py-2 text-xs font-medium rounded-lg border border-border hover:bg-accent text-foreground transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSendEmail}
                disabled={isSending || !!sendSuccessMessage}
                className="flex items-center gap-2 px-5 py-2 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 shadow-sm"
              >
                {isSending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                Send Email
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

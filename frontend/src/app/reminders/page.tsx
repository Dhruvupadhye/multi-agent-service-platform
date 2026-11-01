"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { ReminderItem } from "@/types/api";
import {
  Bell,
  Plus,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Calendar,
  ExternalLink,
  MessageSquare,
  X,
  CheckSquare,
} from "lucide-react";

export default function RemindersPage() {
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create Reminder Modal Form
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split("T")[0];
  });
  const [time, setTime] = useState("09:00");
  const [notes, setNotes] = useState("");
  const [sendWhatsApp, setSendWhatsApp] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [successReminder, setSuccessReminder] = useState<any | null>(null);

  const fetchReminders = async () => {
    setLoading(true);
    setError(null);
    try {
      const items = await apiClient.listReminders();
      setReminders(items);
    } catch (err: any) {
      setError(err.message || "Failed to load reminders.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
  }, []);

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccessEventNull();

    if (!title.trim()) {
      setFormError("Reminder title is required.");
      return;
    }
    if (!date || !time) {
      setFormError("Due date and time are required.");
      return;
    }

    const dueIso = `${date}T${time}:00+05:30`;

    setSubmitting(true);
    try {
      const res = await apiClient.createReminder({
        title: title.trim(),
        datetime_iso: dueIso,
        notes: notes.trim(),
        send_whatsapp: sendWhatsApp,
      });

      setSuccessReminder(res.reminder || { title: title.trim(), scheduled_time: dueIso });
      fetchReminders();

      setTitle("");
      setNotes("");
    } catch (err: any) {
      setFormError(err.message || "Failed to create reminder.");
    } finally {
      setSubmitting(false);
    }
  };

  const setSuccessEventNull = () => {
    setSuccessReminder(null);
  };

  const formatDueTime = (isoString?: string) => {
    if (!isoString) return "No time set";
    try {
      const d = new Date(isoString);
      return d.toLocaleString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] p-6 gap-6 max-w-7xl mx-auto w-full">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Bell className="h-6 w-6 text-primary" />
            Reminders & Action Alerts
          </h1>
          <p className="text-sm text-muted-foreground">
            Schedule prioritized reminders integrated with Google Calendar and automated WhatsApp notifications.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchReminders}
            disabled={loading}
            className="p-2 rounded-lg border border-border bg-card hover:bg-accent text-foreground transition-colors"
            title="Refresh reminders"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => {
              setFormError(null);
              setSuccessEventNull();
              setIsModalOpen(true);
            }}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm"
          >
            <Plus className="h-4 w-4" />
            New Reminder
          </button>
        </div>
      </div>

      {/* Main Reminders Content */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground gap-2">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm">Retrieving reminders from schedule...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center bg-card rounded-xl border border-destructive/20 max-w-lg mx-auto">
            <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
            <h3 className="font-semibold text-foreground mb-1">Unable to Load Reminders</h3>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <button
              onClick={fetchReminders}
              className="px-4 py-2 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : reminders.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground gap-2 p-8 text-center bg-card rounded-xl border border-border">
            <CheckSquare className="h-10 w-10 opacity-40 text-emerald-500" />
            <h3 className="text-base font-semibold text-foreground">No Pending Reminders</h3>
            <p className="text-xs max-w-sm">
              All caught up! You have no upcoming reminders scheduled. Create a new one or ask the voice assistant.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="mt-2 text-xs text-primary font-medium underline"
            >
              Set a new reminder
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reminders.map((rem) => {
              const formattedTime = formatDueTime(rem.scheduled_time);
              return (
                <div
                  key={rem.id}
                  className="bg-card rounded-xl border border-border p-5 shadow-sm hover:border-primary/50 transition-colors flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-600 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        <Clock className="h-3 w-3" />
                        Upcoming
                      </span>
                      <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
                        <MessageSquare className="h-3 w-3 text-emerald-500" />
                        WhatsApp Alert
                      </span>
                    </div>

                    <h3 className="font-semibold text-foreground text-base mb-2">
                      {rem.title}
                    </h3>

                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
                      <Calendar className="h-3.5 w-3.5 text-primary shrink-0" />
                      <span>{formattedTime}</span>
                    </div>

                    {rem.description && (
                      <p className="text-xs text-muted-foreground bg-muted/30 p-2.5 rounded-lg border border-border">
                        {rem.description}
                      </p>
                    )}
                  </div>

                  {rem.event_link && (
                    <div className="mt-4 pt-3 border-t border-border flex justify-end">
                      <a
                        href={rem.event_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary font-medium hover:underline flex items-center gap-1"
                      >
                        Calendar Link <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Reminder Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-card w-full max-w-lg rounded-2xl border border-border shadow-xl flex flex-col max-h-[90vh] overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-foreground">Create New Reminder</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-muted-foreground hover:text-foreground p-1 rounded-md"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleCreateReminder} className="p-6 overflow-y-auto space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Reminder Title / Task *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Submit quarterly progress report to director"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Date *
                  </label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Time *
                  </label>
                  <input
                    type="time"
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Additional Notes (Optional)
                </label>
                <textarea
                  rows={2}
                  placeholder="Additional context or checklist items..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary resize-none"
                />
              </div>

              {/* WhatsApp Notification Toggle */}
              <div className="p-3 rounded-lg border border-border bg-muted/20 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-emerald-500" />
                  <div>
                    <p className="text-xs font-medium text-foreground">WhatsApp Notification</p>
                    <p className="text-[11px] text-muted-foreground">Dispatch an instant alert to configured number</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={sendWhatsApp}
                  onChange={(e) => setSendWhatsApp(e.target.checked)}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
              </div>

              {/* Status and Feedback Messages */}
              {formError && (
                <div className="p-3 rounded-lg border border-destructive/20 bg-destructive/10 text-xs text-destructive flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {formError}
                </div>
              )}

              {successReminder && (
                <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 space-y-1">
                  <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600">
                    <CheckCircle2 className="h-4 w-4" />
                    Reminder Successfully Created!
                  </div>
                  <p className="text-xs text-foreground font-medium">
                    {successReminder.title}
                  </p>
                  <p className="text-[11px] text-muted-foreground">
                    Due at: {formatDueTime(successReminder.scheduled_time)}
                  </p>
                </div>
              )}

              {/* Form Actions */}
              <div className="pt-4 border-t border-border flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg border border-border hover:bg-accent text-foreground transition-colors"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex items-center gap-2 px-5 py-2 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 shadow-sm"
                >
                  {submitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                  Save Reminder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

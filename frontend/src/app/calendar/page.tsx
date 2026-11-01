"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { CalendarEventItem } from "@/types/api";
import {
  Calendar as CalendarIcon,
  Clock,
  Plus,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Loader2,
  CalendarDays,
  FileText,
  X,
} from "lucide-react";

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New Event Form State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [summary, setSummary] = useState("");
  const [date, setDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1); // default tomorrow
    return d.toISOString().split("T")[0];
  });
  const [startTime, setStartTime] = useState("10:00");
  const [endTime, setEndTime] = useState("11:00");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [successEvent, setSuccessEvent] = useState<any | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const items = await apiClient.listCalendarEvents();
      setEvents(items);
    } catch (err: any) {
      setError(err.message || "Failed to load calendar events.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleScheduleEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccessEvent(null);

    if (!summary.trim()) {
      setFormError("Event title/summary is required.");
      return;
    }
    if (!date) {
      setFormError("Event date is required.");
      return;
    }
    if (!startTime || !endTime) {
      setFormError("Start and End times are required.");
      return;
    }

    const startIso = `${date}T${startTime}:00+05:30`;
    const endIso = `${date}T${endTime}:00+05:30`;

    if (new Date(endIso) <= new Date(startIso)) {
      setFormError("End time must be after start time.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await apiClient.createCalendarEvent({
        summary: summary.trim(),
        start_time_iso: startIso,
        end_time_iso: endIso,
        description: description.trim(),
      });

      setSuccessEvent(res);
      // Refresh event list
      fetchEvents();

      // Reset form fields
      setSummary("");
      setDescription("");
    } catch (err: any) {
      setFormError(err.message || "Failed to schedule calendar event.");
    } finally {
      setSubmitting(false);
    }
  };

  const formatEventDate = (startObj?: { dateTime?: string; date?: string }) => {
    if (!startObj) return "Date not specified";
    const raw = startObj.dateTime || startObj.date;
    if (!raw) return "Date not specified";
    try {
      const dt = new Date(raw);
      return dt.toLocaleString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return raw;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] p-6 gap-6 max-w-7xl mx-auto w-full">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <CalendarIcon className="h-6 w-6 text-primary" />
            Calendar & Meeting Schedule
          </h1>
          <p className="text-sm text-muted-foreground">
            View upcoming synchronized meetings, schedule appointments, and coordinate through Google Calendar.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchEvents}
            disabled={loading}
            className="p-2 rounded-lg border border-border bg-card hover:bg-accent text-foreground transition-colors"
            title="Refresh events"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => {
              setFormError(null);
              setSuccessEvent(null);
              setIsModalOpen(true);
            }}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm"
          >
            <Plus className="h-4 w-4" />
            Schedule Meeting
          </button>
        </div>
      </div>

      {/* Main Events Grid */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground gap-2">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm">Retrieving calendar events...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center bg-card rounded-xl border border-destructive/20 max-w-lg mx-auto">
            <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-2" />
            <h3 className="font-semibold text-foreground mb-1">Unable to Load Events</h3>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <button
              onClick={fetchEvents}
              className="px-4 py-2 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground gap-2 p-8 text-center bg-card rounded-xl border border-border">
            <CalendarDays className="h-10 w-10 opacity-40" />
            <h3 className="text-base font-semibold text-foreground">No Upcoming Events</h3>
            <p className="text-xs max-w-sm">
              You currently have no events scheduled on your calendar. Click "Schedule Meeting" to create one.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="mt-2 text-xs text-primary font-medium underline"
            >
              Schedule your first meeting
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {events.map((ev, index) => {
              const startFormatted = formatEventDate(ev.start);
              return (
                <div
                  key={ev.id || index}
                  className="bg-card rounded-xl border border-border p-5 shadow-sm hover:border-primary/50 transition-colors flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-primary/10 text-primary uppercase tracking-wider">
                        Google Calendar
                      </span>
                      {ev.htmlLink && (
                        <a
                          href={ev.htmlLink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:text-foreground transition-colors"
                          title="Open in Google Calendar"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </div>
                    <h3 className="font-semibold text-foreground text-base mb-2 line-clamp-2">
                      {ev.summary || "Untitled Event"}
                    </h3>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
                      <Clock className="h-3.5 w-3.5 text-primary shrink-0" />
                      <span>{startFormatted}</span>
                    </div>
                    {ev.description && (
                      <p className="text-xs text-muted-foreground line-clamp-3 bg-muted/30 p-2.5 rounded-lg border border-border">
                        {ev.description}
                      </p>
                    )}
                  </div>
                  {ev.htmlLink && (
                    <div className="mt-4 pt-3 border-t border-border flex justify-end">
                      <a
                        href={ev.htmlLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary font-medium hover:underline flex items-center gap-1"
                      >
                        View in Calendar <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Schedule Meeting Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-card w-full max-w-lg rounded-2xl border border-border shadow-xl flex flex-col max-h-[90vh] overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CalendarDays className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-foreground">Schedule New Event</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-muted-foreground hover:text-foreground p-1 rounded-md"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleScheduleEvent} className="p-6 overflow-y-auto space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Meeting Title / Summary *
                </label>
                <input
                  type="text"
                  placeholder="e.g. AI Roadmap Sync with Engineering Lead"
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Event Date *
                </label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    Start Time *
                  </label>
                  <input
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">
                    End Time *
                  </label>
                  <input
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Agenda / Description (Optional)
                </label>
                <textarea
                  rows={3}
                  placeholder="Topics, agenda items, or meeting location notes..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary resize-none"
                />
              </div>

              {/* Status and Feedback Messages */}
              {formError && (
                <div className="p-3 rounded-lg border border-destructive/20 bg-destructive/10 text-xs text-destructive flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {formError}
                </div>
              )}

              {successEvent && (
                <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600">
                    <CheckCircle2 className="h-4 w-4" />
                    Event Scheduled Successfully!
                  </div>
                  <p className="text-xs text-foreground font-medium">
                    {successEvent.summary}
                  </p>
                  {successEvent.event_link && (
                    <a
                      href={successEvent.event_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-primary font-medium hover:underline"
                    >
                      Open in Google Calendar <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
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
                  Schedule Event
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

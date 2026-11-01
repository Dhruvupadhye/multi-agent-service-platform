"use client";

import { Mic, Square, Loader2, X, AlertCircle } from "lucide-react";
import { VoiceState } from "@/types/api";
import { cn } from "@/lib/utils";

interface VoiceButtonProps {
  state: VoiceState;
  duration?: number;
  onStart: () => void;
  onStop: () => void;
  onCancel?: () => void;
  disabled?: boolean;
  size?: "default" | "large";
}

export function VoiceButton({
  state,
  duration = 0,
  onStart,
  onStop,
  onCancel,
  disabled = false,
  size = "default",
}: VoiceButtonProps) {
  const isRecording = state === "recording";
  const isProcessing = state === "processing" || state === "thinking";

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  // Recording State with live timer and stop / cancel buttons
  if (isRecording) {
    return (
      <div className="flex items-center gap-2 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 rounded-2xl px-3 py-1.5 shadow-sm animate-in fade-in">
        {/* Animated Sound Wave Indicator */}
        <div className="flex items-center gap-0.5 text-rose-500 h-6 px-1">
          <span className="voice-wave-bar" />
          <span className="voice-wave-bar" />
          <span className="voice-wave-bar" />
          <span className="voice-wave-bar" />
          <span className="voice-wave-bar" />
        </div>

        {/* Live Timer */}
        <span className="text-xs font-mono font-semibold text-rose-600 dark:text-rose-400 min-w-10">
          {formatSeconds(duration)}
        </span>

        {/* Stop / Submit Button */}
        <button
          type="button"
          onClick={onStop}
          className="flex h-8 px-2.5 items-center justify-center gap-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-medium text-xs shadow-xs transition"
          title="Stop and send voice command"
        >
          <Square className="h-3 w-3 fill-current" />
          <span>Done</span>
        </button>

        {/* Cancel Button */}
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex h-8 w-8 items-center justify-center rounded-xl text-slate-500 hover:bg-slate-200/60 dark:text-slate-400 dark:hover:bg-slate-800 transition"
            title="Cancel recording"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }

  // Processing or Thinking State
  if (isProcessing) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-indigo-50 border border-indigo-200 text-indigo-700 dark:bg-indigo-950/40 dark:border-indigo-900 dark:text-indigo-300 text-xs font-medium">
        <Loader2 className="h-4 w-4 animate-spin text-indigo-600 dark:text-indigo-400" />
        <span>{state === "processing" ? "Transcribing..." : "Thinking..."}</span>
      </div>
    );
  }

  // Idle Button
  const isLarge = size === "large";
  return (
    <button
      type="button"
      onClick={onStart}
      disabled={disabled}
      className={cn(
        "relative flex items-center justify-center rounded-xl transition-all shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 disabled:opacity-50 disabled:pointer-events-none",
        isLarge
          ? "h-12 w-12 bg-gradient-to-tr from-indigo-600 to-indigo-500 hover:from-indigo-700 hover:to-indigo-600 text-white shadow-indigo-500/25 shadow-md"
          : "h-9 w-9 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-600 dark:bg-slate-800 dark:hover:bg-indigo-950 dark:hover:text-indigo-400 dark:text-slate-300"
      )}
      title="Record voice command"
      aria-label="Record voice command"
    >
      <Mic className={cn(isLarge ? "h-6 w-6" : "h-4 w-4")} />
    </button>
  );
}

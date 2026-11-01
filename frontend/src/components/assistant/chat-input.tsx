"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, CornerDownLeft } from "lucide-react";
import { VoiceButton } from "./voice-button";
import { VoiceState } from "@/types/api";

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  voiceState: VoiceState;
  voiceDuration: number;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onCancelRecording: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSendMessage,
  voiceState,
  voiceDuration,
  onStartRecording,
  onStopRecording,
  onCancelRecording,
  disabled = false,
  placeholder = "Ask anything, draft an email, schedule a meeting, or query documents...",
}: ChatInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
    }
  }, [text]);

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled || voiceState === "recording") return;
    onSendMessage(trimmed);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isRecording = voiceState === "recording";
  const isBusy = disabled || voiceState === "processing" || voiceState === "thinking";

  return (
    <div className="relative w-full max-w-4xl mx-auto rounded-2xl border border-slate-200 bg-white p-2 sm:p-2.5 shadow-sm transition-all focus-within:border-indigo-400 focus-within:ring-3 focus-within:ring-indigo-100 dark:border-slate-800 dark:bg-slate-900 dark:focus-within:border-indigo-600 dark:focus-within:ring-indigo-950/50">
      {/* If recording, display full voice recording control bar */}
      {isRecording ? (
        <div className="flex items-center justify-between py-2 px-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              Capturing speech...
            </span>
          </div>
          <VoiceButton
            state={voiceState}
            duration={voiceDuration}
            onStart={onStartRecording}
            onStop={onStopRecording}
            onCancel={onCancelRecording}
          />
        </div>
      ) : (
        <div className="flex flex-col">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isBusy}
            rows={1}
            className="w-full resize-none bg-transparent px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none dark:text-slate-100 dark:placeholder:text-slate-500 max-h-44 disabled:opacity-50"
          />

          <div className="flex items-center justify-between pt-1 px-1">
            {/* Left helper info */}
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 dark:text-slate-500">
              <span className="hidden sm:inline">Press Enter to send, Shift+Enter for newline</span>
            </div>

            {/* Right action buttons: Voice & Send */}
            <div className="flex items-center gap-2">
              <VoiceButton
                state={voiceState}
                duration={voiceDuration}
                onStart={onStartRecording}
                onStop={onStopRecording}
                onCancel={onCancelRecording}
                disabled={isBusy}
              />

              <button
                type="button"
                onClick={handleSubmit}
                disabled={!text.trim() || isBusy}
                className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs transition disabled:opacity-40 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                title="Send message"
                aria-label="Send message"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

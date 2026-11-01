"use client";

import { useState } from "react";
import {
  Bot,
  User,
  Mic,
  Copy,
  Check,
  AlertCircle,
  RotateCcw,
} from "lucide-react";
import { ChatMessage as ChatMessageType } from "@/types/api";
import { ResponseRenderer } from "./response-renderer";
import { cn, formatTime, copyToClipboard } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessageType;
  onRetry?: (message: ChatMessageType) => void;
}

export function ChatMessage({ message, onRetry }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const textToCopy =
      message.responsePayload?.direct_answer ||
      message.responsePayload?.action_result ||
      message.content;
    const success = await copyToClipboard(textToCopy);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={cn(
        "group flex w-full gap-3 sm:gap-4 py-3 transition-opacity",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-xl shadow-xs text-xs font-semibold",
          isUser
            ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
            : "bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white shadow-indigo-500/20"
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message Content Container */}
      <div
        className={cn(
          "flex flex-col space-y-1.5 max-w-[85%] sm:max-w-[78%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        {/* Header meta */}
        <div className="flex items-center gap-2 px-1 text-[11px] text-slate-400 dark:text-slate-500">
          <span className="font-semibold text-slate-600 dark:text-slate-400">
            {isUser ? "You" : "Master Assistant"}
          </span>
          <span>•</span>
          <span>{formatTime(message.timestamp)}</span>
          {message.isVoice && (
            <span className="inline-flex items-center gap-0.5 rounded-full bg-indigo-50 px-1.5 py-0.2 text-[10px] font-medium text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
              <Mic className="h-2.5 w-2.5" />
              <span>Voice</span>
            </span>
          )}
        </div>

        {/* Message Bubble */}
        <div
          className={cn(
            "relative rounded-2xl px-4 py-3 shadow-xs transition-all",
            isUser
              ? "bg-indigo-600 text-white rounded-tr-xs"
              : "bg-white border border-slate-200/80 text-slate-900 rounded-tl-xs dark:bg-slate-900 dark:border-slate-800 dark:text-slate-100 w-full"
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          ) : message.error ? (
            <div className="flex items-start gap-2.5 text-rose-600 dark:text-rose-400">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <p className="text-sm font-medium">{message.error}</p>
                {onRetry && (
                  <button
                    onClick={() => onRetry(message)}
                    className="inline-flex items-center gap-1 rounded-md border border-rose-200 bg-rose-50 px-2 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:border-rose-900 dark:bg-rose-950/60 dark:text-rose-300"
                  >
                    <RotateCcw className="h-3 w-3" />
                    <span>Retry Command</span>
                  </button>
                )}
              </div>
            </div>
          ) : message.responsePayload ? (
            <ResponseRenderer response={message.responsePayload} />
          ) : (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          )}
        </div>

        {/* Actions bar */}
        {!isUser && !message.error && (
          <div className="flex items-center gap-1 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300 px-1 py-0.5 rounded transition"
              title="Copy message"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3 text-emerald-500" />
                  <span className="text-emerald-600 font-medium">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

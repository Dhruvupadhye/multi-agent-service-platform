"use client";

import { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  RotateCcw,
  Bot,
  Mail,
  Calendar,
  Search,
  FileText,
  AlertCircle,
  HelpCircle,
  Mic,
} from "lucide-react";
import { ChatMessage as ChatMessageType, VoiceState, AgentResponse } from "@/types/api";
import { ChatMessage } from "@/components/assistant/chat-message";
import { ChatInput } from "@/components/assistant/chat-input";
import { useVoiceRecorder } from "@/hooks/use-voice-recorder";
import { apiClient } from "@/lib/api-client";
import { generateUUID } from "@/lib/utils";

const SAMPLE_PROMPTS = [
  {
    title: "Explain Artificial Intelligence",
    prompt: "What is artificial intelligence and how does it work?",
    icon: Bot,
    category: "General Query",
  },
  {
    title: "Draft an Email",
    prompt: "Draft an email to my manager requesting 2 days of leave next week.",
    icon: Mail,
    category: "Email Composer",
  },
  {
    title: "Check Tomorrow's Schedule",
    prompt: "What meetings do I have tomorrow?",
    icon: Calendar,
    category: "Calendar",
  },
  {
    title: "Schedule a Team Meeting",
    prompt: "Schedule a meeting tomorrow at 3 PM to review project progress.",
    icon: Calendar,
    category: "Scheduler",
  },
  {
    title: "Summarize Inbox",
    prompt: "Summarize my unread emails and show me what's important.",
    icon: Mail,
    category: "Email Agent",
  },
  {
    title: "Search Uploaded Documents",
    prompt: "Search the uploaded PDF for project requirements and key takeaways.",
    icon: FileText,
    category: "Document RAG",
  },
];

export default function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [sessionId, setSessionId] = useState<string>("");
  const [isThinking, setIsThinking] = useState<boolean>(false);
  const [transcriptionNotice, setTranscriptionNotice] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Initialize or restore session ID and check for forward prompt
  useEffect(() => {
    let sid = "";
    if (typeof window !== "undefined") {
      sid = sessionStorage.getItem("masp_session_id") || "";
      if (!sid) {
        sid = generateUUID();
        sessionStorage.setItem("masp_session_id", sid);
      }
      const initialPrompt = sessionStorage.getItem("masp_initial_prompt");
      if (initialPrompt) {
        sessionStorage.removeItem("masp_initial_prompt");
        // Execute initial prompt
        setTimeout(() => {
          handleSendMessage(initialPrompt);
        }, 150);
      }
    }
    setSessionId(sid || generateUUID());
  }, []);

  // Auto-scroll to bottom whenever messages update or assistant is thinking
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  // Voice recording hook with direct backend voice orchestration
  const {
    state: voiceState,
    setState: setVoiceState,
    duration: voiceDuration,
    errorMessage: voiceError,
    startRecording,
    stopRecording,
    cancelRecording,
    resetState: resetVoiceState,
  } = useVoiceRecorder({
    onRecordingComplete: async (audioBlob: Blob) => {
      setVoiceState("thinking");
      setIsThinking(true);
      setTranscriptionNotice(null);

      // Create a temporary user message placeholder
      const tempUserMsgId = generateUUID();
      const userMsg: ChatMessageType = {
        id: tempUserMsgId,
        role: "user",
        content: "🎙️ [Processing voice command...]",
        timestamp: new Date().toISOString(),
        isVoice: true,
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const response: AgentResponse = await apiClient.sendVoiceCommand(
          audioBlob,
          "voice_command.wav",
          sessionId
        );

        // Update the user message with the actual transcript
        const transcriptText = response.raw_transcript || "Voice Command";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === tempUserMsgId
              ? { ...m, content: transcriptText, rawTranscript: transcriptText }
              : m
          )
        );

        // Add the assistant response message
        const assistantMsg: ChatMessageType = {
          id: generateUUID(),
          role: "assistant",
          content: response.direct_answer || response.action_result || "Processed command.",
          timestamp: new Date().toISOString(),
          responsePayload: response,
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setVoiceState("idle");
      } catch (err: any) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === tempUserMsgId
              ? { ...m, content: "🎙️ [Voice command failed]" }
              : m
          )
        );

        const errorMsg: ChatMessageType = {
          id: generateUUID(),
          role: "assistant",
          content: "Failed to process voice command.",
          timestamp: new Date().toISOString(),
          error:
            err.message ||
            "An error occurred while uploading or transcribing your voice note.",
        };
        setMessages((prev) => [...prev, errorMsg]);
        setVoiceState("error");
      } finally {
        setIsThinking(false);
      }
    },
    onError: (err) => {
      console.error("Voice recording error:", err);
    },
  });

  // Handle sending typed text message
  const handleSendMessage = async (command: string) => {
    if (!command.trim() || isThinking) return;

    const userMsgId = generateUUID();
    const userMsg: ChatMessageType = {
      id: userMsgId,
      role: "user",
      content: command,
      timestamp: new Date().toISOString(),
      isVoice: false,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);

    try {
      const response: AgentResponse = await apiClient.sendTextCommand(
        command,
        sessionId
      );

      const assistantMsg: ChatMessageType = {
        id: generateUUID(),
        role: "assistant",
        content: response.direct_answer || response.action_result || "Command executed.",
        timestamp: new Date().toISOString(),
        responsePayload: response,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessageType = {
        id: generateUUID(),
        role: "assistant",
        content: "Error processing request.",
        timestamp: new Date().toISOString(),
        error:
          err.message ||
          "Could not reach the Multi-Agent backend. Please check connection.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  // Start new conversation
  const handleNewConversation = () => {
    const newSid = generateUUID();
    setSessionId(newSid);
    if (typeof window !== "undefined") {
      sessionStorage.setItem("masp_session_id", newSid);
    }
    setMessages([]);
    resetVoiceState();
  };

  // Retry failed message
  const handleRetry = (msg: ChatMessageType) => {
    // Look for previous user message or retry content
    const lastUserMsg = [...messages]
      .reverse()
      .find((m) => m.role === "user");
    if (lastUserMsg) {
      handleSendMessage(lastUserMsg.content);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto w-full px-3 sm:px-6 py-4">
      {/* Top Controls Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Interactive Agent Workspace
            </h2>
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              Session: {sessionId.slice(0, 8)}...
            </p>
          </div>
        </div>

        <button
          onClick={handleNewConversation}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 transition"
          title="Reset conversation state and memory"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>New Session</span>
        </button>
      </div>

      {/* Voice Error Banner */}
      {voiceError && (
        <div className="mt-2 flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700 dark:border-rose-900 dark:bg-rose-950/50 dark:text-rose-300">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{voiceError}</span>
          </div>
          <button
            onClick={resetVoiceState}
            className="text-xs font-semibold underline hover:no-underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Chat Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
        {messages.length === 0 ? (
          /* Empty State */
          <div className="h-full flex flex-col items-center justify-center text-center px-4 py-8 max-w-xl mx-auto">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 to-sky-400 text-white shadow-lg shadow-indigo-500/25 mb-4">
              <Bot className="h-7 w-7" />
            </div>

            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              How can I assist your workflow today?
            </h3>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
              Speak naturally or type your request. The supervisor routes questions, email drafts, meetings, and document queries to specialized agents.
            </p>

            {/* Quick Prompts Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
              {SAMPLE_PROMPTS.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(item.prompt)}
                    className="group rounded-xl border border-slate-200/80 bg-white p-3 hover:border-indigo-400 hover:shadow-xs dark:border-slate-800 dark:bg-slate-900/60 dark:hover:border-indigo-600 text-left transition"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                        {item.category}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
                      {item.title}
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 mt-0.5">
                      "{item.prompt}"
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} onRetry={handleRetry} />
          ))
        )}

        {/* Thinking Indicator */}
        {isThinking && (
          <div className="flex items-center gap-3 py-2 pl-1 animate-pulse">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-xs">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-medium text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 shadow-xs flex items-center gap-2">
              <span className="flex h-2 w-2 rounded-full bg-indigo-600 animate-ping" />
              <span>Orchestrating agents &amp; synthesizing response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar Area */}
      <div className="pt-2">
        <ChatInput
          onSendMessage={handleSendMessage}
          voiceState={voiceState}
          voiceDuration={voiceDuration}
          onStartRecording={startRecording}
          onStopRecording={stopRecording}
          onCancelRecording={cancelRecording}
          disabled={isThinking}
        />
      </div>
    </div>
  );
}

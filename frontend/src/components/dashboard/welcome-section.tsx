"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, Mic, Bot } from "lucide-react";
import { VoiceButton } from "@/components/assistant/voice-button";
import { useVoiceRecorder } from "@/hooks/use-voice-recorder";
import { apiClient } from "@/lib/api-client";
import { generateUUID } from "@/lib/utils";

export function WelcomeSection() {
  const router = useRouter();
  const [command, setCommand] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    state: voiceState,
    setState: setVoiceState,
    duration: voiceDuration,
    startRecording,
    stopRecording,
    cancelRecording,
  } = useVoiceRecorder({
    onRecordingComplete: async (audioBlob: Blob) => {
      setVoiceState("thinking");
      setIsSubmitting(true);
      try {
        const sid =
          (typeof window !== "undefined" &&
            sessionStorage.getItem("masp_session_id")) ||
          generateUUID();
        sessionStorage.setItem("masp_session_id", sid);

        const res = await apiClient.sendVoiceCommand(
          audioBlob,
          "dashboard_voice.wav",
          sid
        );
        // Navigate to assistant with this initial interaction
        router.push("/assistant");
      } catch (err) {
        console.error("Dashboard voice error:", err);
        router.push("/assistant");
      } finally {
        setIsSubmitting(false);
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim() || isSubmitting) return;

    // Send or forward to assistant
    if (typeof window !== "undefined") {
      sessionStorage.setItem("masp_initial_prompt", command.trim());
    }
    router.push("/assistant");
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-950 p-6 sm:p-10 text-white shadow-xl shadow-indigo-950/20">
      {/* Decorative background glow */}
      <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl pointer-events-none" />
      <div className="absolute -left-20 -bottom-20 h-72 w-72 rounded-full bg-sky-500/15 blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-3xl space-y-4">
        {/* Active Badge */}
        <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-indigo-200 backdrop-blur-md border border-white/10">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Multi-Agent Orchestration Platform</span>
        </div>

        {/* Title */}
        <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
          {getGreeting()}, what would you like to achieve today?
        </h1>

        <p className="text-sm sm:text-base text-indigo-100/80 max-w-2xl leading-relaxed">
          Autonomous agents coordinate email composition, inbox summarization, calendar management, and grounded document queries seamlessly.
        </p>

        {/* Command Input Box with Voice */}
        <div className="pt-2">
          <form
            onSubmit={handleSubmit}
            className="flex items-center gap-2 rounded-2xl bg-white/95 p-2 shadow-2xl backdrop-blur-md transition-all focus-within:ring-4 focus-within:ring-indigo-400/30"
          >
            <div className="pl-3 text-slate-400">
              <Bot className="h-5 w-5 text-indigo-600" />
            </div>

            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="Type an instruction, e.g. 'Draft an email to professor' or 'What meetings tomorrow?'"
              className="flex-1 bg-transparent px-2 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
            />

            {/* Voice button */}
            <VoiceButton
              state={voiceState}
              duration={voiceDuration}
              onStart={startRecording}
              onStop={stopRecording}
              onCancel={cancelRecording}
            />

            {/* Submit button */}
            <button
              type="submit"
              disabled={!command.trim() || isSubmitting}
              className="flex h-10 items-center gap-1.5 rounded-xl bg-indigo-600 px-4 text-xs font-semibold text-white shadow-xs hover:bg-indigo-700 transition disabled:opacity-40 disabled:pointer-events-none"
            >
              <span>Execute</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

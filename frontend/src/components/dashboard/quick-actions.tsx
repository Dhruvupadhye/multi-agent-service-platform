"use client";

import { useRouter } from "next/navigation";
import {
  Mail,
  Calendar,
  FileSearch,
  BellRing,
  Globe,
  Sparkles,
  ArrowUpRight,
} from "lucide-react";

const ACTIONS = [
  {
    title: "Draft an Email",
    description: "Compose professional emails with recipient hints and tailored tone.",
    prompt: "Draft an email to my manager requesting project feedback by Thursday.",
    icon: Mail,
    color: "from-indigo-500 to-indigo-600",
    bgLight: "bg-indigo-50 dark:bg-indigo-950/40",
    textLight: "text-indigo-600 dark:text-indigo-400",
  },
  {
    title: "Check & Schedule Meetings",
    description: "Query upcoming Google Calendar events or book new appointments.",
    prompt: "What meetings are scheduled for tomorrow?",
    icon: Calendar,
    color: "from-sky-500 to-sky-600",
    bgLight: "bg-sky-50 dark:bg-sky-950/40",
    textLight: "text-sky-600 dark:text-sky-400",
  },
  {
    title: "Summarize Inbox",
    description: "Fetch unread messages, classify spam with ML, and prepare a digest.",
    prompt: "Summarize my unread emails and highlight priority items.",
    icon: Sparkles,
    color: "from-violet-500 to-violet-600",
    bgLight: "bg-violet-50 dark:bg-violet-950/40",
    textLight: "text-violet-600 dark:text-violet-400",
  },
  {
    title: "Document Knowledge Base",
    description: "Perform grounded vector retrieval across indexed PDF documents.",
    prompt: "Search the uploaded PDF for system architecture requirements.",
    icon: FileSearch,
    color: "from-emerald-500 to-emerald-600",
    bgLight: "bg-emerald-50 dark:bg-emerald-950/40",
    textLight: "text-emerald-600 dark:text-emerald-400",
  },
  {
    title: "Set Smart Reminder",
    description: "Create notifications and scheduled alerts with WhatsApp dispatch.",
    prompt: "Remind me to submit the assignment tomorrow at 10 AM.",
    icon: BellRing,
    color: "from-amber-500 to-amber-600",
    bgLight: "bg-amber-50 dark:bg-amber-950/40",
    textLight: "text-amber-600 dark:text-amber-400",
  },
  {
    title: "Web Research Synthesis",
    description: "Synthesize latest industry advances using live DuckDuckGo search.",
    prompt: "Research recent advances in generative AI and reasoning models.",
    icon: Globe,
    color: "from-blue-500 to-blue-600",
    bgLight: "bg-blue-50 dark:bg-blue-950/40",
    textLight: "text-blue-600 dark:text-blue-400",
  },
];

export function QuickActions() {
  const router = useRouter();

  const handleActionClick = (prompt: string) => {
    if (typeof window !== "undefined") {
      sessionStorage.setItem("masp_initial_prompt", prompt);
    }
    router.push("/assistant");
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            Quick Actions
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            One-click triggers for common office automation workflows
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {ACTIONS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => handleActionClick(item.prompt)}
              className="group relative flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-4 text-left shadow-xs transition-all hover:border-indigo-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-indigo-700"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-xl ${item.bgLight} ${item.textLight} transition-transform group-hover:scale-105`}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="rounded-lg p-1 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowUpRight className="h-4 w-4" />
                  </div>
                </div>

                <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {item.title}
                </h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <div className="mt-4 pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] font-medium text-indigo-600 dark:text-indigo-400">
                <span>Launch agent</span>
                <span className="font-mono text-[10px] text-slate-400">↵</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

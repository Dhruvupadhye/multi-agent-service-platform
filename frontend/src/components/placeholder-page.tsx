import Link from "next/link";
import { LucideIcon, Bot, ArrowRight } from "lucide-react";

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
  badge?: string;
  suggestedPrompt: string;
}

export function PlaceholderPage({
  title,
  description,
  icon: Icon,
  badge = "Phase 2 Module",
  suggestedPrompt,
}: PlaceholderPageProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-xl mx-auto min-h-[60vh]">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400 mb-4 shadow-xs">
        <Icon className="h-8 w-8" />
      </div>

      <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 mb-3">
        {badge}
      </span>

      <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
        {title}
      </h2>

      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
        {description}
      </p>

      {/* Assistant handoff card */}
      <div className="w-full rounded-2xl border border-slate-200/80 bg-white p-4 text-left shadow-xs dark:border-slate-800 dark:bg-slate-900 mb-6">
        <div className="flex items-center gap-2 mb-1.5">
          <Bot className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Available right now via AI Assistant:
          </span>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 italic">
          "{suggestedPrompt}"
        </p>
      </div>

      <Link
        href="/assistant"
        className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-700 transition"
      >
        <span>Open AI Assistant</span>
        <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

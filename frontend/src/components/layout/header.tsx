"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Menu,
  Activity,
  PlusCircle,
  Wifi,
  WifiOff,
  RefreshCw,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { BackendHealth } from "@/types/api";

interface HeaderProps {
  onMobileMenuClick: () => void;
  collapsed: boolean;
}

export function Header({ onMobileMenuClick, collapsed }: HeaderProps) {
  const pathname = usePathname();
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [isChecking, setIsChecking] = useState<boolean>(true);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  const checkStatus = async () => {
    setIsChecking(true);
    try {
      const data = await apiClient.checkHealth();
      setHealth(data);
      setIsOnline(true);
    } catch {
      setIsOnline(false);
      setHealth(null);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    if (pathname === "/") return "Overview Dashboard";
    if (pathname === "/assistant") return "AI Agent Assistant";
    if (pathname === "/email") return "Email Management";
    if (pathname === "/calendar") return "Calendar & Events";
    if (pathname === "/reminders") return "Reminders & Alerts";
    if (pathname === "/documents") return "Document Knowledge Base";
    if (pathname === "/settings") return "Platform Settings";
    return "Multi-Agent Platform";
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200/80 bg-white/80 px-4 sm:px-6 backdrop-blur-md dark:border-slate-800/80 dark:bg-slate-950/80 transition-all">
      <div className="flex items-center gap-3">
        {/* Mobile menu trigger */}
        <button
          onClick={onMobileMenuClick}
          className="flex lg:hidden h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-900"
          aria-label="Toggle menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <h1 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-slate-100 tracking-tight">
            {getPageTitle()}
          </h1>
        </div>
      </div>

      {/* Right Action Items */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Backend Status Indicator */}
        <div
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 transition-colors"
          title={`Backend API: ${apiClient.getBaseUrl()}`}
        >
          {isChecking ? (
            <RefreshCw className="h-3 w-3 animate-spin text-slate-400" />
          ) : isOnline ? (
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          ) : (
            <span className="h-2 w-2 rounded-full bg-rose-500" />
          )}

          <span className="hidden sm:inline text-slate-600 dark:text-slate-300">
            {isChecking
              ? "Connecting..."
              : isOnline
              ? "FastAPI Connected"
              : "Backend Offline"}
          </span>
        </div>

        {/* Quick New Chat Button */}
        {pathname !== "/assistant" && (
          <Link
            href="/assistant"
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs sm:text-sm font-medium text-white shadow-xs hover:bg-indigo-700 transition"
          >
            <PlusCircle className="h-4 w-4" />
            <span className="hidden sm:inline">New Voice / Chat</span>
            <span className="sm:hidden">Chat</span>
          </Link>
        )}
      </div>
    </header>
  );
}

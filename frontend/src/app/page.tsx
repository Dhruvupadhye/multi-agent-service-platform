"use client";

import { WelcomeSection } from "@/components/dashboard/welcome-section";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { RecentActivity } from "@/components/dashboard/recent-activity";

export default function DashboardPage() {
  return (
    <div className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">
      {/* Welcome Banner with Voice Command Input */}
      <WelcomeSection />

      {/* Quick Workflows Grid */}
      <QuickActions />

      {/* Capabilities & Integrations */}
      <RecentActivity />
    </div>
  );
}

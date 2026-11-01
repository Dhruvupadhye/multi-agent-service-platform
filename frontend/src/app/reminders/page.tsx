import { BellRing } from "lucide-react";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function RemindersPage() {
  return (
    <PlaceholderPage
      title="Smart Reminders & WhatsApp Alerts"
      description="The dedicated reminder board will launch in Phase 2. The Reminder Agent currently schedules reminders and sends WhatsApp notifications via Twilio."
      icon={BellRing}
      badge="Phase 2 Workflow"
      suggestedPrompt="Remind me to submit my assignment tomorrow at 10 AM."
    />
  );
}

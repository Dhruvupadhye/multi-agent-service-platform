import { Calendar } from "lucide-react";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function CalendarPage() {
  return (
    <PlaceholderPage
      title="Google Calendar Integration"
      description="The calendar view and drag-and-drop agenda are part of Phase 2. You can query existing meetings and schedule new events right now via voice or text."
      icon={Calendar}
      badge="Phase 2 Workflow"
      suggestedPrompt="What meetings are scheduled for tomorrow?"
    />
  );
}

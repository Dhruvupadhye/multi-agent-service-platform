import { Mail } from "lucide-react";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function EmailPage() {
  return (
    <PlaceholderPage
      title="Email Management & Inbox Digest"
      description="The dedicated email interface is scheduled for Phase 2. The Email Agent is fully active in the backend and accessible via the AI Assistant."
      icon={Mail}
      badge="Phase 2 Workflow"
      suggestedPrompt="Summarize my unread emails and highlight priority messages."
    />
  );
}

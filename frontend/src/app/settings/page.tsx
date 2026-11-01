import { Settings } from "lucide-react";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function SettingsPage() {
  return (
    <PlaceholderPage
      title="Platform Settings & API Configurations"
      description="Settings for OpenAI models, Twilio credentials, Whisper local model sizes, and OAuth tokens are configured via backend environment variables (.env)."
      icon={Settings}
      badge="Configuration"
      suggestedPrompt="How can I improve my productivity?"
    />
  );
}

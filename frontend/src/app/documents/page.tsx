import { FileText } from "lucide-react";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function DocumentsPage() {
  return (
    <PlaceholderPage
      title="Document Knowledge Base & Vector Index"
      description="The dedicated file management table and document previewer are coming in Phase 2. Document vector indexing (ChromaDB) and RAG queries are live via the Assistant."
      icon={FileText}
      badge="Phase 2 Workflow"
      suggestedPrompt="Search the uploaded PDF for project requirements and system architecture."
    />
  );
}

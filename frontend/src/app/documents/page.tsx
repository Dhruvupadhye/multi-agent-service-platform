"use client";

import { useState, useEffect, useRef } from "react";
import { apiClient } from "@/lib/api-client";
import { DocumentItem, DocumentUploadResponse } from "@/types/api";
import {
  FileText,
  Upload,
  Search,
  Sparkles,
  BookOpen,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Loader2,
  FileCheck,
  ChevronDown,
  Layers,
  HelpCircle,
  Send,
} from "lucide-react";

interface QAResult {
  id: string;
  query: string;
  answer: string;
  context_preview?: string;
  source?: string;
  timestamp: string;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [docsError, setDocsError] = useState<string | null>(null);

  // Upload State
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [lastUploaded, setLastUploaded] = useState<DocumentUploadResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Q&A RAG State
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [qaHistory, setQaHistory] = useState<QAResult[]>([]);
  const [qaError, setQaError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    setDocsError(null);
    try {
      const items = await apiClient.listDocuments();
      setDocuments(items);
    } catch (err: any) {
      setDocsError(err.message || "Failed to load indexed documents.");
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("Only PDF documents are supported for RAG indexing.");
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setUploadError("File size exceeds 25 MB limit.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setLastUploaded(null);

    try {
      const res = await apiClient.uploadDocument(file);
      setLastUploaded(res);
      // Refresh documents list
      fetchDocuments();
    } catch (err: any) {
      setUploadError(err.message || "Failed to process and index document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const currentQuery = question.trim();
    setAsking(true);
    setQaError(null);

    try {
      const res = await apiClient.askAssistant(currentQuery);
      const newQa: QAResult = {
        id: Date.now().toString(),
        query: currentQuery,
        answer: res.answer || "No response generated.",
        context_preview: res.context_preview || res.context || undefined,
        source: res.source || "Uploaded Documents",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setQaHistory((prev) => [newQa, ...prev]);
      setQuestion("");
    } catch (err: any) {
      setQaError(err.message || "Failed to query document assistant.");
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] p-6 gap-6 max-w-7xl mx-auto w-full">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            Document Intelligence & RAG
          </h1>
          <p className="text-sm text-muted-foreground">
            Upload PDF documents for automatic chunking, ChromaDB vector indexing, and grounded natural language Q&A.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchDocuments}
            disabled={loadingDocs}
            className="p-2 rounded-lg border border-border bg-card hover:bg-accent text-foreground transition-colors"
            title="Refresh documents"
          >
            <RefreshCw className={`h-4 w-4 ${loadingDocs ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50"
          >
            {isUploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            Upload PDF
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* Left Column: Upload & Indexed Documents */}
        <div className="lg:col-span-5 flex flex-col gap-6 overflow-y-auto">
          {/* Upload Dropzone Card */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors bg-card ${
              isUploading
                ? "border-primary bg-primary/5 cursor-wait"
                : "border-border hover:border-primary/50 hover:bg-accent/30"
            }`}
          >
            <div className="flex flex-col items-center gap-2">
              <div className="p-3 rounded-full bg-primary/10 text-primary">
                {isUploading ? (
                  <Loader2 className="h-6 w-6 animate-spin" />
                ) : (
                  <Upload className="h-6 w-6" />
                )}
              </div>
              <h3 className="font-semibold text-sm text-foreground">
                {isUploading ? "Chunking & Vector Indexing PDF..." : "Upload New PDF Document"}
              </h3>
              <p className="text-xs text-muted-foreground max-w-xs">
                {isUploading
                  ? "PyPDFLoader is extracting text and saving vector embeddings into ChromaDB."
                  : "Click to select or drag and drop a PDF file here (maximum 25 MB)."}
              </p>
            </div>
          </div>

          {/* Upload Status / Feedback */}
          {uploadError && (
            <div className="p-3 rounded-lg border border-destructive/20 bg-destructive/10 text-xs text-destructive flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {uploadError}
            </div>
          )}

          {lastUploaded && (
            <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 space-y-2 animate-in fade-in">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600">
                <CheckCircle2 className="h-4 w-4" />
                Indexed {lastUploaded.filename} ({lastUploaded.total_pages} pages)
              </div>
              {lastUploaded.summary && (
                <div className="text-xs text-foreground bg-background/80 p-3 rounded-lg border border-border">
                  <p className="font-medium mb-1 text-[11px] uppercase tracking-wider text-muted-foreground">
                    Executive Summary:
                  </p>
                  <p className="line-clamp-4 leading-relaxed">{lastUploaded.summary}</p>
                </div>
              )}
            </div>
          )}

          {/* Indexed Documents List */}
          <div className="bg-card rounded-xl border border-border shadow-sm flex flex-col flex-1 min-h-[220px]">
            <div className="p-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">Indexed Knowledge Sources</h3>
              </div>
              <span className="text-xs text-muted-foreground font-medium">
                {documents.length} document{documents.length === 1 ? "" : "s"}
              </span>
            </div>

            <div className="p-4 overflow-y-auto divide-y divide-border">
              {loadingDocs ? (
                <div className="flex items-center justify-center py-8 text-xs text-muted-foreground gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  Loading indexed files...
                </div>
              ) : docsError ? (
                <div className="p-4 text-center text-xs text-destructive">{docsError}</div>
              ) : documents.length === 0 ? (
                <div className="py-8 text-center text-xs text-muted-foreground">
                  <FileText className="h-8 w-8 opacity-40 mx-auto mb-2" />
                  <p className="font-medium">No indexed documents found</p>
                  <p className="text-[11px] mt-0.5">Upload a PDF above to begin asking questions.</p>
                </div>
              ) : (
                documents.map((doc, idx) => (
                  <div key={idx} className="py-3 first:pt-0 last:pb-0">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-medium text-foreground truncate max-w-[200px]" title={doc.filename}>
                        {doc.filename}
                      </span>
                      <div className="flex items-center gap-2 text-muted-foreground text-[11px]">
                        <span className="flex items-center gap-1">
                          <Layers className="h-3 w-3" />
                          {doc.total_chunks} chunks
                        </span>
                        <span>•</span>
                        <span>{doc.pages} pgs</span>
                      </div>
                    </div>
                    {doc.preview && (
                      <p className="text-[11px] text-muted-foreground line-clamp-2">
                        {doc.preview}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: RAG Question & Answer Interface */}
        <div className="lg:col-span-7 flex flex-col bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-border bg-muted/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-semibold text-foreground">Document Q&A Assistant</h3>
            </div>
            <span className="text-[11px] text-muted-foreground bg-muted px-2 py-0.5 rounded">
              ChromaDB RAG
            </span>
          </div>

          {/* Question Input */}
          <div className="p-4 border-b border-border">
            <form onSubmit={handleAskQuestion} className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Ask a question about the uploaded document content..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  disabled={asking}
                  className="w-full pl-9 pr-4 py-2 text-sm rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
                />
              </div>
              <button
                type="submit"
                disabled={asking || !question.trim()}
                className="px-4 py-2 text-xs font-medium rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5 shrink-0 shadow-sm"
              >
                {asking ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                Query
              </button>
            </form>
            {qaError && (
              <p className="text-xs text-destructive mt-2 flex items-center gap-1">
                <AlertCircle className="h-3.5 w-3.5" />
                {qaError}
              </p>
            )}
          </div>

          {/* Answers Feed */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4">
            {asking && (
              <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 flex items-center gap-3 animate-pulse">
                <Loader2 className="h-5 w-5 animate-spin text-primary shrink-0" />
                <div className="text-xs text-muted-foreground">
                  <p className="font-medium text-foreground">Retrieving vector embeddings & formulating answer...</p>
                  <p>Searching document chunks in ChromaDB</p>
                </div>
              </div>
            )}

            {qaHistory.length === 0 && !asking ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground p-8 gap-2">
                <HelpCircle className="h-10 w-10 opacity-30" />
                <h4 className="text-sm font-semibold text-foreground">Ask Document Questions</h4>
                <p className="text-xs max-w-sm">
                  Query project proposals, research papers, reports, or contracts. Answers are strictly grounded in your indexed PDFs with context previews.
                </p>
              </div>
            ) : (
              qaHistory.map((item) => (
                <div
                  key={item.id}
                  className="p-5 rounded-xl border border-border bg-background shadow-sm space-y-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <Search className="h-4 w-4 text-primary shrink-0" />
                      {item.query}
                    </h4>
                    <span className="text-[10px] text-muted-foreground shrink-0">
                      {item.timestamp}
                    </span>
                  </div>

                  <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                    {item.answer}
                  </p>

                  {item.context_preview && (
                    <div className="mt-2 pt-2 border-t border-border">
                      <details className="group">
                        <summary className="text-[11px] font-medium text-primary hover:underline cursor-pointer flex items-center gap-1">
                          <BookOpen className="h-3 w-3" />
                          View Grounded Vector Source
                        </summary>
                        <div className="mt-2 p-3 rounded-lg bg-muted/40 border border-border text-xs text-muted-foreground whitespace-pre-wrap font-mono leading-normal">
                          {item.context_preview}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

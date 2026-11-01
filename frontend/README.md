# Multi-Agent Service Platform — Frontend (Phase 1)

Modern, production-grade Next.js web application replacing the legacy Streamlit interface for the **Multi-Agent Service Platform**.

Built with **Next.js 14 (App Router)**, **React 18**, **TypeScript**, **Tailwind CSS**, **shadcn/ui design patterns**, and **Lucide React**.

---

## Architecture Overview

```text
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                  # Main Workspace Dashboard
│   │   ├── assistant/
│   │   │   └── page.tsx              # AI Assistant chat & voice orchestration interface
│   │   ├── email/page.tsx            # Clean Phase 2 workflow placeholder
│   │   ├── calendar/page.tsx         # Clean Phase 2 workflow placeholder
│   │   ├── reminders/page.tsx        # Clean Phase 2 workflow placeholder
│   │   ├── documents/page.tsx        # Clean Phase 2 workflow placeholder
│   │   ├── settings/page.tsx         # Clean Phase 2 configuration placeholder
│   │   ├── layout.tsx                # App shell layout (Sidebar + Header + Content)
│   │   └── globals.css               # Design tokens, CSS variables & animations
│   ├── components/
│   │   ├── layout/
│   │   │   ├── app-shell.tsx         # Responsive layout wrapper with sidebar collapse
│   │   │   ├── sidebar.tsx           # Collapsible sidebar with active link indicators
│   │   │   └── header.tsx            # Real-time backend status pill & quick actions
│   │   ├── assistant/
│   │   │   ├── chat-message.tsx      # User & Assistant chat bubbles with metadata
│   │   │   ├── chat-input.tsx        # Multiline auto-resizing text + voice trigger
│   │   │   ├── voice-button.tsx      # Browser MediaRecorder state & waveform animation
│   │   │   └── response-renderer.tsx # Typed cards for answers, drafts, calendar, docs
│   │   ├── dashboard/
│   │   │   ├── welcome-section.tsx   # Greeting banner + prompt bar with voice support
│   │   │   ├── quick-actions.tsx     # 1-click trigger cards for agent workflows
│   │   │   └── recent-activity.tsx   # Subsystem health & active agent monitor
│   │   └── placeholder-page.tsx      # Reusable placeholder with assistant handoff
│   ├── lib/
│   │   ├── api-client.ts             # Centralized typed FastAPI client with timeouts
│   │   └── utils.ts                  # cn(), formatting, clipboard helpers
│   ├── hooks/
│   │   └── use-voice-recorder.ts     # MediaRecorder hook with 6-state lifecycle
│   └── types/
│       └── api.ts                    # TypeScript schemas for requests, responses & agents
├── .env.example
├── .env.local
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

---

## Implemented Features (Phase 1)

### 1. Main Dashboard (`/`)
- Collapsible sidebar with desktop collapse toggle and mobile drawer.
- Welcome banner with time-aware greeting and integrated voice/text command bar.
- Quick-action buttons for common operations (Draft Email, Schedule Meeting, Summarize Inbox, Query Knowledge Base, Set Reminder, Web Research).
- Integration status cards displaying backend subsystem health.
- Live backend connection status pill in header with auto-refresh every 30 seconds.

### 2. Conversational AI Assistant (`/assistant`)
- Full conversation history with auto-scroll.
- Support for multiline text input (Enter to send, Shift+Enter for new line).
- Integrated voice recording with waveform visualization and elapsed timer.
- New Session button to clear state and reset conversation session memory.
- Error handling with one-click retry functionality.
- Empty-state quick prompts.

### 3. Voice Interaction Lifecycle
- **Idle**: Microphone ready.
- **Recording**: Audio captured via browser `MediaRecorder` API with live timer and animated waveform.
- **Processing**: Uploading audio directly to FastAPI `/api/v1/agents/orchestrate-voice/`.
- **Thinking**: Backend LangGraph routing & agent synthesis.
- **Responding**: Transcribed prompt displayed alongside typed response card.
- **Error**: Graceful error banners for microphone denial or network issues.

### 4. Specialized Response Rendering
- **General Answer**: Conversational markdown response.
- **Email Draft**: Formatted email card with Subject, Recipient, Tone, and one-click Copy action.
- **Calendar Event**: Event details and direct "View on Google Calendar" link.
- **Calendar Schedule**: Structured list of upcoming events.
- **Reminder**: Confirmation card with calendar and WhatsApp dispatch confirmation.
- **Document Answer**: Grounded answer with source pill and collapsible context preview.
- **Research Answer**: Synthesized web findings with search snippet preview.
- **Clarification**: Actionable warning card requesting user clarification.

---

## Getting Started

### 1. Start the FastAPI Backend
From the project root:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configure Frontend Environment
Ensure `frontend/.env.local` contains:
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Install & Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

import streamlit as st
import requests

# Base URL for your FastAPI backend
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="Multi-Agent Office Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM – Custom CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ═══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════════════════ */
:root {
    /* — Brand Palette — */
    --color-primary:        #4F46E5;
    --color-primary-hover:  #4338CA;
    --color-primary-light:  #EEF2FF;
    --color-primary-subtle: #C7D2FE;

    --color-secondary:      #0EA5E9;
    --color-secondary-light:#E0F2FE;

    --color-success:        #10B981;
    --color-success-light:  #D1FAE5;
    --color-warning:        #F59E0B;
    --color-warning-light:  #FEF3C7;
    --color-error:          #EF4444;
    --color-error-light:    #FEE2E2;
    --color-info:           #3B82F6;
    --color-info-light:     #DBEAFE;

    /* — Surfaces — */
    --bg-page:              #F8FAFC;
    --bg-card:              #FFFFFF;
    --bg-sidebar:           #1E293B;
    --bg-input:             #F8FAFC;

    /* — Text — */
    --text-primary:         #0F172A;
    --text-secondary:       #475569;
    --text-muted:           #94A3B8;
    --text-inverse:         #FFFFFF;

    /* — Borders & Dividers — */
    --border-color:         #E2E8F0;
    --border-color-focus:   var(--color-primary);
    --divider-color:        #F1F5F9;

    /* — Spacing Scale — */
    --space-xs:  0.25rem;
    --space-sm:  0.5rem;
    --space-md:  1rem;
    --space-lg:  1.5rem;
    --space-xl:  2rem;
    --space-2xl: 3rem;

    /* — Typography — */
    --font-sans:       'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono:       'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    --text-xs:   0.75rem;
    --text-sm:   0.875rem;
    --text-base: 1rem;
    --text-lg:   1.125rem;
    --text-xl:   1.25rem;
    --text-2xl:  1.5rem;
    --text-3xl:  1.875rem;

    /* — Radii — */
    --radius-sm:  0.375rem;
    --radius-md:  0.5rem;
    --radius-lg:  0.75rem;
    --radius-xl:  1rem;
    --radius-full: 9999px;

    /* — Shadows — */
    --shadow-xs:  0 1px 2px rgba(0,0,0,0.04);
    --shadow-sm:  0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:  0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
    --shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
    --shadow-xl:  0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);

    /* — Transitions — */
    --transition-fast:   150ms cubic-bezier(0.4,0,0.2,1);
    --transition-base:   200ms cubic-bezier(0.4,0,0.2,1);
    --transition-slow:   300ms cubic-bezier(0.4,0,0.2,1);
}

/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL RESETS & BASE
   ═══════════════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.stApp {
    background-color: var(--bg-page);
    font-family: var(--font-sans);
}

/* Tighten the main content container padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   HEADER AREA
   ═══════════════════════════════════════════════════════════════════════════ */
.hero-header {
    background: linear-gradient(135deg, var(--color-primary) 0%, #7C3AED 100%);
    border-radius: var(--radius-xl);
    padding: var(--space-xl) var(--space-2xl);
    margin-bottom: var(--space-xl);
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 250px;
    height: 250px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-title {
    color: var(--text-inverse);
    font-size: var(--text-3xl);
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    color: rgba(255,255,255,0.8);
    font-size: var(--text-base);
    font-weight: 400;
    margin-top: var(--space-xs);
    position: relative;
    z-index: 1;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(8px);
    color: var(--text-inverse);
    font-size: var(--text-xs);
    font-weight: 600;
    padding: 0.3rem 0.75rem;
    border-radius: var(--radius-full);
    margin-bottom: var(--space-sm);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}
.hero-badge .pulse-dot {
    width: 6px;
    height: 6px;
    background: #34D399;
    border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.5; transform: scale(1.5); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: var(--bg-card);
    padding: 0.4rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-xs);
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-md);
    padding: 0.6rem 1.25rem;
    font-weight: 500;
    font-size: var(--text-sm);
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    border: none;
    white-space: nowrap;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--color-primary-light);
    color: var(--color-primary);
}

.stTabs [aria-selected="true"] {
    background: var(--color-primary) !important;
    color: var(--text-inverse) !important;
    font-weight: 600;
    box-shadow: var(--shadow-sm);
}

/* Hide the default tab highlight bar */
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}

.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CARDS & SECTIONS
   ═══════════════════════════════════════════════════════════════════════════ */
.content-card {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-color);
    padding: var(--space-xl);
    margin-bottom: var(--space-lg);
    box-shadow: var(--shadow-sm);
    transition: box-shadow var(--transition-base);
}
.content-card:hover {
    box-shadow: var(--shadow-md);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: var(--space-lg);
    padding-bottom: var(--space-md);
    border-bottom: 1px solid var(--divider-color);
}
.section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: var(--radius-lg);
    font-size: 1.3rem;
    flex-shrink: 0;
}
.section-icon.voice    { background: #EDE9FE; }
.section-icon.rag      { background: var(--color-secondary-light); }
.section-icon.upload   { background: var(--color-success-light); }
.section-title {
    font-size: var(--text-xl);
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.01em;
}
.section-desc {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.5;
}

/* ═══════════════════════════════════════════════════════════════════════════
   RESULT CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.result-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    margin-top: var(--space-md);
    box-shadow: var(--shadow-sm);
}
.result-card.success {
    border-left: 4px solid var(--color-success);
}
.result-card.info {
    border-left: 4px solid var(--color-info);
}
.result-label {
    font-size: var(--text-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: var(--space-xs);
}
.result-value {
    font-size: var(--text-base);
    color: var(--text-primary);
    line-height: 1.6;
}
.result-meta {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: var(--space-sm);
    padding: 0.35rem 0.75rem;
    background: var(--bg-page);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    color: var(--text-secondary);
}

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: var(--color-primary);
    color: var(--text-inverse);
    border: none;
    border-radius: var(--radius-md);
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    font-size: var(--text-sm);
    font-family: var(--font-sans);
    cursor: pointer;
    transition: all var(--transition-fast);
    box-shadow: 0 1px 3px rgba(79,70,229,0.3);
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    background: var(--color-primary-hover);
    box-shadow: 0 4px 12px rgba(79,70,229,0.35);
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 1px 3px rgba(79,70,229,0.3);
}
.stButton > button:focus {
    outline: 2px solid var(--color-primary-subtle);
    outline-offset: 2px;
}

/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS & FORM ELEMENTS
   ═══════════════════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-input);
    border: 1.5px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 0.65rem 0.85rem;
    font-family: var(--font-sans);
    font-size: var(--text-sm);
    color: var(--text-primary);
    transition: all var(--transition-fast);
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--border-color-focus);
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
    background: var(--bg-card);
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--text-muted);
}

/* Label styling */
.stTextInput label,
.stTextArea label,
.stFileUploader label,
.stAudioInput label {
    font-weight: 600;
    font-size: var(--text-sm);
    color: var(--text-primary);
    margin-bottom: var(--space-xs);
}

/* ═══════════════════════════════════════════════════════════════════════════
   FILE UPLOADER
   ═══════════════════════════════════════════════════════════════════════════ */
.stFileUploader > div {
    border: 2px dashed var(--border-color);
    border-radius: var(--radius-lg);
    transition: border-color var(--transition-fast), background var(--transition-fast);
}
.stFileUploader > div:hover {
    border-color: var(--color-primary-subtle);
    background: var(--color-primary-light);
}

/* ═══════════════════════════════════════════════════════════════════════════
   AUDIO INPUT
   ═══════════════════════════════════════════════════════════════════════════ */
.stAudioInput > div {
    border-radius: var(--radius-lg);
}

/* ═══════════════════════════════════════════════════════════════════════════
   STATUS MESSAGES (success / info / warning / error)
   ═══════════════════════════════════════════════════════════════════════════ */
.stAlert {
    border-radius: var(--radius-md) !important;
    font-size: var(--text-sm);
    font-family: var(--font-sans);
}

div[data-testid="stAlert"] {
    border-radius: var(--radius-md);
}

/* ═══════════════════════════════════════════════════════════════════════════
   EXPANDER
   ═══════════════════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    font-weight: 600;
    font-size: var(--text-sm);
    color: var(--text-primary);
    background: var(--bg-page);
    border-radius: var(--radius-md);
    padding: 0.6rem 0.85rem;
    transition: background var(--transition-fast);
}
.streamlit-expanderHeader:hover {
    background: var(--color-primary-light);
    color: var(--color-primary);
}
.streamlit-expanderContent {
    border-color: var(--border-color);
    padding: var(--space-md);
    background: var(--bg-page);
    border-radius: 0 0 var(--radius-md) var(--radius-md);
}

/* ═══════════════════════════════════════════════════════════════════════════
   CODE BLOCKS
   ═══════════════════════════════════════════════════════════════════════════ */
.stCodeBlock {
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
}

/* ═══════════════════════════════════════════════════════════════════════════
   SPINNER / LOADING
   ═══════════════════════════════════════════════════════════════════════════ */
.stSpinner > div {
    border-top-color: var(--color-primary) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CAPTION / SMALL TEXT
   ═══════════════════════════════════════════════════════════════════════════ */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: var(--text-xs) !important;
    color: var(--text-muted) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   HELPER: CUSTOM DIVIDER
   ═══════════════════════════════════════════════════════════════════════════ */
.custom-divider {
    height: 1px;
    background: var(--divider-color);
    margin: var(--space-lg) 0;
    border: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FEATURE PILLS (for quick-reference hints)
   ═══════════════════════════════════════════════════════════════════════════ */
.feature-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: var(--space-md);
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.3rem 0.75rem;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 500;
    border: 1px solid var(--border-color);
    background: var(--bg-card);
    color: var(--text-secondary);
    transition: all var(--transition-fast);
}
.pill:hover {
    border-color: var(--color-primary-subtle);
    background: var(--color-primary-light);
    color: var(--color-primary);
}

/* ═══════════════════════════════════════════════════════════════════════════
   LINK BUTTON STYLES
   ═══════════════════════════════════════════════════════════════════════════ */
.calendar-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    background: var(--color-primary-light);
    color: var(--color-primary);
    border-radius: var(--radius-md);
    text-decoration: none;
    font-size: var(--text-sm);
    font-weight: 600;
    transition: all var(--transition-fast);
    border: 1px solid var(--color-primary-subtle);
    margin-top: var(--space-sm);
}
.calendar-link:hover {
    background: var(--color-primary);
    color: var(--text-inverse);
    box-shadow: var(--shadow-sm);
}

/* ═══════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: var(--space-2xl) var(--space-xl);
    color: var(--text-muted);
}
.empty-state .empty-icon {
    font-size: 2.5rem;
    margin-bottom: var(--space-sm);
    opacity: 0.5;
}
.empty-state p {
    font-size: var(--text-sm);
    max-width: 360px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ═══════════════════════════════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .hero-header {
        padding: var(--space-lg);
    }
    .hero-title {
        font-size: var(--text-2xl);
    }
    .content-card {
        padding: var(--space-lg);
    }
    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    .feature-pills {
        gap: 0.35rem;
    }
    .pill {
        font-size: 0.7rem;
        padding: 0.2rem 0.55rem;
    }
}

@media (max-width: 480px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .hero-header {
        padding: var(--space-md);
        border-radius: var(--radius-lg);
    }
    .hero-title {
        font-size: var(--text-xl);
    }
    .content-card {
        padding: var(--space-md);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 0.75rem;
        font-size: var(--text-xs);
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: var(--radius-full);
}
::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-badge"><span class="pulse-dot"></span> AI-Powered Workspace</div>
        <h1 class="hero-title">Multi-Agent Office Platform</h1>
        <p class="hero-subtitle">
            Your intelligent assistant for email, documents, and scheduling — powered by
            autonomous AI agents working together.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    [
        "🎤  Master Assistant",
        "📚  Document RAG",
        "📄  Upload Documents",
    ]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: Master Assistant (Voice Orchestration)
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown(
        """
        <div class="content-card">
            <div class="section-header">
                <div class="section-icon voice">🎤</div>
                <div>
                    <h3 class="section-title">The Master Assistant</h3>
                    <p class="section-desc">
                        Tell the Assistant what to do — draft an email, check your inbox,
                        search your documents, or schedule a meeting.
                    </p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Capability pills
    st.markdown(
        """
        <div class="feature-pills">
            <span class="pill">✉️ Draft emails</span>
            <span class="pill">📨 Inbox summary</span>
            <span class="pill">📅 Schedule meetings</span>
            <span class="pill">🔍 Search docs</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Audio input
    audio_value = st.audio_input("🎙️ Record your voice command")

    if audio_value:
        with st.spinner("🧠 Supervisor Agent is analyzing your command…"):
            files = {"file": ("audio.wav", audio_value, "audio/wav")}
            response = requests.post(
                f"{API_BASE}/agents/orchestrate-voice/", files=files
            )

            if response.status_code == 200:
                data = response.json()
                intent = data.get("intent")

                # ── Email Summarization ──────────────────────────────────
                if intent == "SUMMARIZE_EMAILS":
                    st.success("✅ Inbox processed successfully!")
                    st.markdown(
                        f"""
                        <div class="result-card success">
                            <div class="result-label">Inbox Summary</div>
                            <div class="result-value">{data.get("action_result")}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # ── Scheduling ───────────────────────────────────────────
                elif intent == "SCHEDULE_EVENT":
                    st.success("✅ Event scheduled!")
                    st.markdown(
                        f"""
                        <div class="result-card success">
                            <div class="result-label">Event Details</div>
                            <div class="result-value">{data.get("action_result")}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    event_link = data.get("event_link")
                    if event_link:
                        st.markdown(
                            f'<a class="calendar-link" href="{event_link}" '
                            f'target="_blank">📅 View on Google Calendar</a>',
                            unsafe_allow_html=True,
                        )

                # ── Email Drafting ───────────────────────────────────────
                else:
                    st.success("✅ Email drafted successfully!")
                    final_email = data.get("final_email", {})

                    col_subject, col_meta = st.columns([3, 1])
                    with col_subject:
                        st.markdown(
                            f"""
                            <div class="result-card info">
                                <div class="result-label">Subject</div>
                                <div class="result-value" style="font-weight:600;">
                                    {final_email.get("subject", "No subject generated")}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col_meta:
                        st.markdown(
                            f"""
                            <div class="result-card info">
                                <div class="result-label">Details</div>
                                <div class="result-meta">👤 {final_email.get("recipient_hint", "—")}</div>
                                <div class="result-meta">🎯 {final_email.get("tone", "—")}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.text_area(
                        "📝 Email Body",
                        final_email.get("body", ""),
                        height=250,
                        key="email_draft_body",
                    )
            else:
                st.error(
                    "⚠️ Failed to process audio. Please ensure your backend is running."
                )
    else:
        # Empty state when nothing is recorded yet
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">🎙️</div>
                <p>Press the microphone button above to record a voice command.
                The assistant will interpret your request and take action automatically.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Close the content-card div
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Document RAG Assistant
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown(
        """
        <div class="content-card">
            <div class="section-header">
                <div class="section-icon rag">📚</div>
                <div>
                    <h3 class="section-title">Document RAG Assistant</h3>
                    <p class="section-desc">
                        Ask a question about your uploaded documents. If it doesn't
                        know, it will search the web automatically.
                    </p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "🔎 Enter your question",
        placeholder="e.g., What are the key findings in the Q3 report?",
        key="rag_query",
    )

    if st.button("🚀 Ask Agent", key="ask_agent_btn", use_container_width=True):
        if query:
            with st.spinner("🧠 Thinking…"):
                response = requests.get(
                    f"{API_BASE}/agents/ask-assistant/", params={"query": query}
                )
                if response.status_code == 200:
                    data = response.json()

                    # Answer card
                    st.markdown(
                        f"""
                        <div class="result-card success">
                            <div class="result-label">Answer</div>
                            <div class="result-value">{data.get("answer")}</div>
                            <div class="result-meta">📌 Source: {data.get("source")}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    with st.expander("📄 Context Preview"):
                        st.write(data.get("context_preview"))
                else:
                    st.error("⚠️ Failed to fetch an answer. Check backend connectivity.")
        else:
            st.warning("⚠️ Please enter a query to get started.")

    # Empty-state hint
    if not query:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">💡</div>
                <p>Type a question above and click <strong>Ask Agent</strong> to query
                your knowledge base.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Upload Documents
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(
        """
        <div class="content-card">
            <div class="section-header">
                <div class="section-icon upload">📄</div>
                <div>
                    <h3 class="section-title">Upload Documents</h3>
                    <p class="section-desc">
                        Upload a PDF to your knowledge base. The document will be
                        processed, summarized, and indexed for future queries.
                    </p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "📎 Choose a PDF file",
        type=["pdf"],
        key="pdf_uploader",
        help="Supported format: PDF. Max recommended size: 25 MB.",
    )

    if uploaded_file is not None:
        # File info preview
        file_size_kb = uploaded_file.size / 1024
        size_label = (
            f"{file_size_kb:.1f} KB"
            if file_size_kb < 1024
            else f"{file_size_kb / 1024:.2f} MB"
        )
        st.markdown(
            f"""
            <div class="result-card info" style="margin-bottom: var(--space-md);">
                <div class="result-label">Selected File</div>
                <div class="result-value" style="font-weight:600;">📎 {uploaded_file.name}</div>
                <div class="result-meta">📐 {size_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "⚡ Process Document", key="process_doc_btn", use_container_width=True
        ):
            with st.spinner("📖 Extracting text and generating summary…"):
                files = {
                    "file": (uploaded_file.name, uploaded_file, "application/pdf")
                }
                response = requests.post(
                    f"{API_BASE}/media/upload-document/", files=files
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(
                        "✅ Document successfully processed and added to your knowledge base!"
                    )
                    st.markdown(
                        f"""
                        <div class="result-card success">
                            <div class="result-label">Document Summary</div>
                            <div class="result-value">{data.get("summary")}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("⚠️ Failed to process document. Check backend connectivity.")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <p>Drag &amp; drop a PDF file above or click <strong>Browse files</strong>
                to upload a document to your knowledge base.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center; padding: 0.5rem 0 1rem;">
        <span style="font-size:0.75rem; color:var(--text-muted);">
            Multi-Agent Office Platform &nbsp;·&nbsp; Powered by autonomous AI agents
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

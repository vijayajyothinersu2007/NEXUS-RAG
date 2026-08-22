"""NexusRAG visual system for the Streamlit shell."""

ENTERPRISE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: "DM Sans", "Segoe UI", sans-serif;
    letter-spacing: 0;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0F172A;
    color: #F8FAFC;
}

header, header[data-testid="stHeader"], [data-testid="stDecoration"] {
    background: transparent;
    height: 0;
    border: 0;
}

div[data-testid="stAppViewContainer"] > .main {
    background: transparent;
}

div.block-container {
    max-width: 1500px;
    padding-top: 1.25rem;
    padding-bottom: 3rem;
}

div[data-testid="stToolbar"], div[data-testid="stStatusWidget"] {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(circle at 86% 0%, rgba(99, 102, 241, 0.12), transparent 28rem),
        linear-gradient(135deg, #0B0F17 0%, #101722 55%, #0B0F17 100%);
    color: #F8FAFC;
}

/* Form controls use a light editing surface so pasted and typed content stays readable. */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
input[type="text"],
input[type="password"],
textarea {
    background: #F8FAFC !important;
    border-color: #64748B !important;
    color: #1E1E1E !important;
    caret-color: #1E1E1E !important;
    opacity: 1 !important;
}

div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder,
input::placeholder,
textarea::placeholder {
    color: #475569 !important;
    opacity: 1 !important;
}

div[data-testid="stTextInput"] input:disabled,
div[data-testid="stTextArea"] textarea:disabled,
input:disabled,
textarea:disabled {
    background: #CBD5E1 !important;
    color: #1E1E1E !important;
    -webkit-text-fill-color: #1E1E1E !important;
    opacity: 1 !important;
}

div[data-testid="stChatInput"] {
    background: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.22);
}

div[data-testid="stChatInput"]:focus-within {
    border-color: #818CF8;
    box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.35), 0 8px 30px rgba(0, 0, 0, 0.22);
}

div[data-testid="stChatInput"] textarea {
    background: #E2E8F0;
    color: #000000 !important;
    caret-color: #000000;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #475569 !important;
}

div[data-testid="stChatInput"] button {
    background: linear-gradient(110deg, #4F46E5, #7C3AED);
    border-radius: 8px;
}

section[data-testid="stSidebar"] {
    background: rgba(10, 15, 24, 0.94);
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] * {
    color: #E8EEF4 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    color: #F8FAFC !important;
    width: 100%;
    text-align: left;
    border-radius: 8px;
    padding: 0.68rem 0.8rem;
    transition: all 160ms ease;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99, 102, 241, 0.12);
    border-color: rgba(129, 140, 248, 0.28);
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #1E293B;
    border-color: rgba(99, 102, 241, 0.7);
    box-shadow: 0 0 18px rgba(99, 102, 241, 0.14);
    color: #FFFFFF !important;
}

.nx-nav-group {
    color: #A5B4FC;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    margin: 0.3rem 0 0.45rem;
    text-transform: uppercase;
}

.nx-nav-group-secondary {
    color: #64748B;
    margin-top: 1rem;
}

.nx-brand {
    padding: 0.4rem 0.2rem 1.4rem 0.2rem;
}

.nx-brand-logo {
    display: block;
    width: 60px;
    height: 60px;
    margin-bottom: 0.65rem;
    filter: drop-shadow(0 0 9px rgba(99, 102, 241, 0.65));
}

.nx-brand-mark {
    font-family: "Space Grotesk", sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    background: linear-gradient(105deg, #C7D2FE 0%, #818CF8 46%, #C084FC 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.nx-brand-sub {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.15rem;
}

.nx-page-title {
    font-family: "Space Grotesk", sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 0.15rem;
}

.nx-page-sub {
    color: #94A3B8;
    margin-bottom: 1.2rem;
}

.stMarkdown, label, [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
[data-baseweb="tab"], [data-baseweb="select"] *, .stCaption, .stCaption p {
    color: #E2E8F0 !important;
}

h1, h2, h3, h4, h5, h6, .stSubheader {
    color: #F8FAFC !important;
    letter-spacing: 0.01em;
}

[data-baseweb="select"] > div {
    background: #1E293B;
    border-color: #475569;
    color: #FFFFFF;
}

[data-baseweb="popover"] *, [role="listbox"] * {
    color: #F8FAFC !important;
    background-color: #1E293B;
}

button, [data-testid="stFormSubmitButton"] button {
    color: #FFFFFF !important;
}

div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    background: #4F46E5;
    border-color: #6366F1;
}

div[data-testid="stSlider"] [data-testid="stThumbValue"],
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #F8FAFC !important;
}

div[data-testid="stCodeBlock"] {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
}

div[data-testid="stCodeBlock"] pre, div[data-testid="stCodeBlock"] code {
    color: #E2E8F0 !important;
    background: #1E293B !important;
}

div[data-testid="stTabs"] button[role="tab"] {
    color: #E2E8F0 !important;
    background: transparent !important;
    opacity: 1 !important;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #A5B4FC !important;
    border-bottom: 2px solid #6366F1 !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.2);
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #151D2A;
    border-bottom: 1px solid #334155;
    gap: 0.25rem;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #E2E8F0 !important;
    opacity: 1 !important;
}

div[data-testid="stMetric"] {
    background: #151D2A;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.75rem;
}

.nx-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(51, 65, 85, 0.72);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.16);
    backdrop-filter: blur(14px);
    transition: border-color 160ms ease, transform 160ms ease;
}

.nx-card:hover {
    border-color: rgba(129, 140, 248, 0.55);
    transform: translateY(-2px);
}

.nx-metric-label {
    font-size: 0.78rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.nx-metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #F8FAFC;
}

.nx-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.nx-badge-parsed { background: #D5F5E3; color: #196F3D; }
.nx-badge-failed { background: #FADBD8; color: #922B21; }
.nx-badge-uploaded { background: #D6EAF8; color: #1A5276; }

.nx-placeholder {
    background: rgba(15, 23, 42, 0.62);
    border: 1px dashed #334155;
    border-radius: 10px;
    padding: 2rem;
    color: #94A3B8;
}

.nx-excerpt {
    background: rgba(15, 23, 42, 0.7);
    border-left: 4px solid #6366F1;
    padding: 0.8rem 1rem;
    font-family: ui-monospace, Consolas, monospace;
    font-size: 0.85rem;
    white-space: pre-wrap;
}

.nx-graph-frame {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.4rem;
}

.nx-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(51, 65, 85, 0.55);
    padding-bottom: 0.8rem;
    margin-bottom: 1.3rem;
    position: relative;
}

.nx-model-metrics {
    align-items: center;
    display: flex;
    gap: 0.8rem;
    margin-left: auto;
    margin-right: 1rem;
}

.nx-model-metrics span {
    color: #64748B;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
}

.nx-model-metrics strong {
    background: #151D2A;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #E2E8F0;
    font-size: 0.75rem;
    padding: 0.35rem 0.5rem;
}

.nx-citation-card {
    background: #151D2A;
    border: 1px solid #334155;
    border-left: 3px solid #818CF8;
    border-radius: 8px;
    color: #E2E8F0;
    padding: 0.9rem;
}

.nx-status {
    color: #86EFAC;
    font-size: 0.78rem;
}

.nx-status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-right: 0.35rem;
    border-radius: 50%;
    background: #4ADE80;
    box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.12);
}

.nx-alert {
    background: rgba(69, 10, 10, 0.38);
    border: 1px solid rgba(248, 113, 113, 0.45);
    border-left: 3px solid #F87171;
    border-radius: 8px;
    color: #FECACA;
    padding: 0.9rem 1rem;
    margin: 0.75rem 0 1rem;
}

.nx-alert-title {
    color: #FCA5A5;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.nx-alert-detail {
    color: #FDA4AF;
    font-size: 0.85rem;
}

.nx-tab-note {
    color: #94A3B8;
    font-size: 0.88rem;
    padding: 0.55rem 0;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #1E293B;
    border-radius: 10px;
    overflow: hidden;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(110deg, #4F46E5, #7C3AED);
    border: 0;
    transition: transform 160ms ease, box-shadow 160ms ease;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    transform: translateY(-1px);
}

@media (max-width: 720px) {
    .nx-page-title { font-size: 1.6rem; }
    .nx-topbar { align-items: flex-start; gap: 0.5rem; flex-direction: column; }
    .nx-model-metrics { margin-left: 0; flex-wrap: wrap; }
}
</style>
"""

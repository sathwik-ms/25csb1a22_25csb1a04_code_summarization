def _get_optimizer_dfa():
    try:
        from agent_security.workflow_dfa import WorkflowDFA
        dfa = WorkflowDFA()
        for ev in ["validate", "parse", "graph", "green_audit", "audit"]:
            dfa.step(ev)
        return dfa
    except Exception:
        return None


import sys
import streamlit as st
import streamlit.components.v1 as components

# Ensure safe UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from main import run_pipeline
from agent_controller import AgentController
from optimizer_agent import optimize_code
from graph_visualizer import generate_pdg_html


st.set_page_config(
    page_title="Agentic AI Code Intelligence & Security Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme Toggle (persisted in session state) ───
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

_theme = st.session_state.theme_mode  # "dark" or "light"
_is_dark = _theme == "dark"

# ─── CSS Custom Properties: One palette per theme ───
if _is_dark:
    _css_vars = """
    :root {
        --bg-app: radial-gradient(circle at top right, #0f172a, #0b1120 40%, #030712 100%);
        --fg-primary: #f8fafc;
        --fg-secondary: #94a3b8;
        --fg-muted: #cbd5e1;
        --accent: #38bdf8;
        --accent-hover: #38bdf8;
        --surface-0: #030712;
        --surface-1: #0b1120;
        --surface-2: #0f172a;
        --surface-3: #1e293b;
        --surface-4: #334155;
        --surface-5: #475569;
        --border: #334155;
        --border-hover: #38bdf8;
        --hero-bg: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #1e1b4b 100%);
        --hero-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        --hero-title-gradient: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        --badge-bg: rgba(56, 189, 248, 0.12);
        --badge-border: rgba(56, 189, 248, 0.3);
        --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        --trace-bg: #111827;
        --trace-border: #3b82f6;
        --heal-card-bg: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        --heal-label-bg: rgba(15, 23, 42, 0.85);
        --pill-before-bg: rgba(239, 68, 68, 0.2);
        --pill-before-fg: #fca5a5;
        --pill-after-bg: rgba(34, 197, 94, 0.2);
        --pill-after-fg: #86efac;
        --arrow-pill-bg: #0f172a;
        --code-before-fg: #fca5a5;
        --code-after-fg: #86efac;
        --heal-badge-line-bg: rgba(56, 189, 248, 0.15);
        --heal-badge-line-border: rgba(56, 189, 248, 0.4);
        --heal-badge-rule-bg: rgba(129, 140, 248, 0.15);
        --heal-badge-rule-border: rgba(129, 140, 248, 0.4);
        --heal-badge-rule-fg: #a5b4fc;
        --heal-badge-status-bg: rgba(34, 197, 94, 0.15);
        --heal-badge-status-border: rgba(34, 197, 94, 0.4);
        --heal-badge-status-fg: #86efac;
        --before-border: rgba(239, 68, 68, 0.35);
        --before-bg: rgba(239, 68, 68, 0.04);
        --after-border: rgba(34, 197, 94, 0.35);
        --after-bg: rgba(34, 197, 94, 0.04);
        --primary-btn-bg: linear-gradient(90deg, #f43f5e 0%, #fb7185 100%);
        --primary-btn-hover: linear-gradient(90deg, #e11d48 0%, #f43f5e 100%);
        --sidebar-bg: #0f172a;
    }
    """
else:
    _css_vars = """
    :root {
        --bg-app: linear-gradient(135deg, #f8fafc 0%, #eef2f7 40%, #e2e8f0 100%);
        --fg-primary: #0f172a;
        --fg-secondary: #475569;
        --fg-muted: #334155;
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --surface-0: #ffffff;
        --surface-1: #f8fafc;
        --surface-2: #f1f5f9;
        --surface-3: #e2e8f0;
        --surface-4: #cbd5e1;
        --surface-5: #94a3b8;
        --border: #cbd5e1;
        --border-hover: #2563eb;
        --hero-bg: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 50%, #ede9fe 100%);
        --hero-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        --hero-title-gradient: linear-gradient(90deg, #2563eb, #7c3aed, #a855f7);
        --badge-bg: rgba(37, 99, 235, 0.08);
        --badge-border: rgba(37, 99, 235, 0.25);
        --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
        --trace-bg: #f1f5f9;
        --trace-border: #3b82f6;
        --heal-card-bg: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%);
        --heal-label-bg: rgba(241, 245, 249, 0.95);
        --pill-before-bg: rgba(239, 68, 68, 0.1);
        --pill-before-fg: #dc2626;
        --pill-after-bg: rgba(34, 197, 94, 0.1);
        --pill-after-fg: #16a34a;
        --arrow-pill-bg: #f1f5f9;
        --code-before-fg: #dc2626;
        --code-after-fg: #16a34a;
        --heal-badge-line-bg: rgba(37, 99, 235, 0.08);
        --heal-badge-line-border: rgba(37, 99, 235, 0.3);
        --heal-badge-rule-bg: rgba(124, 58, 237, 0.08);
        --heal-badge-rule-border: rgba(124, 58, 237, 0.3);
        --heal-badge-rule-fg: #7c3aed;
        --heal-badge-status-bg: rgba(22, 163, 74, 0.08);
        --heal-badge-status-border: rgba(22, 163, 74, 0.3);
        --heal-badge-status-fg: #16a34a;
        --before-border: rgba(220, 38, 38, 0.3);
        --before-bg: rgba(220, 38, 38, 0.04);
        --after-border: rgba(22, 163, 74, 0.3);
        --after-bg: rgba(22, 163, 74, 0.04);
        --primary-btn-bg: linear-gradient(90deg, #f43f5e 0%, #fb7185 100%);
        --primary-btn-hover: linear-gradient(90deg, #e11d48 0%, #f43f5e 100%);
        --sidebar-bg: #f1f5f9;
    }
    """

# Custom Styling (Glassmorphism — var-driven for Light/Dark)
st.markdown(
    f"""
    <style>
    {_css_vars}
    .stApp {{
        background: var(--bg-app);
        color: var(--fg-primary);
    }}
    /* Sidebar */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {{
        background-color: var(--surface-2) !important;
        color: var(--fg-primary) !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: var(--fg-primary) !important;
    }}
    .hero-banner {{
        padding: 1.4rem 1.8rem;
        border-radius: 16px;
        background: var(--hero-bg);
        border: 1px solid var(--border);
        color: var(--fg-primary);
        margin-bottom: 1.5rem;
        box-shadow: var(--hero-shadow);
    }}
    .hero-banner h1 {{
        margin: 0;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: var(--hero-title-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-banner p {{
        margin: 0.4rem 0 0 0;
        font-size: 0.95rem;
        color: var(--fg-secondary);
    }}
    .author-badge {{
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.2rem 0.75rem;
        border-radius: 9999px;
        background: var(--badge-bg);
        border: 1px solid var(--badge-border);
        color: var(--accent);
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .metric-card {{
        background: var(--surface-3);
        border: 1px solid var(--border);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }}
    .metric-card h3 {{
        margin: 0;
        font-size: 1.8rem;
        color: var(--accent);
    }}
    .metric-card span {{
        font-size: 0.82rem;
        color: var(--fg-secondary);
        text-transform: uppercase;
    }}
    .agent-trace-box {{
        background: var(--trace-bg);
        border-left: 4px solid var(--trace-border);
        padding: 0.6rem 0.9rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.88rem;
    }}
    .stTextArea textarea {{
        font-family: Consolas, monospace !important;
        font-size: 0.88rem !important;
        background: var(--surface-2) !important;
        color: var(--fg-primary) !important;
        border: 1px solid var(--border) !important;
    }}

    /* ─── Streamlit Widget Overrides (Force Consistent Theme) ─── */
    .stButton > button,
    button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {{
        background-color: var(--surface-3) !important;
        color: var(--fg-primary) !important;
        border: 1px solid var(--surface-5) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }}
    .stButton > button:hover,
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {{
        background-color: var(--surface-4) !important;
        color: var(--accent) !important;
        border-color: var(--accent) !important;
    }}
    .stButton > button:active,
    button[kind="secondary"]:active {{
        background-color: var(--surface-2) !important;
    }}
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {{
        background: var(--primary-btn-bg) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {{
        background: var(--primary-btn-hover) !important;
        color: #ffffff !important;
    }}

    /* Expanders */
    div[data-testid="stExpander"],
    .streamlit-expander {{
        background-color: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: var(--card-shadow) !important;
    }}
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] details summary {{
        background-color: var(--surface-3) !important;
        color: var(--fg-primary) !important;
        border: none !important;
        border-radius: 0px !important;
        transition: background-color 0.2s ease !important;
    }}
    div[data-testid="stExpander"] details summary:hover {{
        background-color: var(--surface-4) !important;
        color: var(--accent) !important;
    }}
    div[data-testid="stExpander"] details summary p,
    div[data-testid="stExpander"] details summary span,
    div[data-testid="stExpander"] details summary svg {{
        color: var(--fg-primary) !important;
        fill: var(--fg-primary) !important;
    }}
    div[data-testid="stExpander"] details summary:hover p,
    div[data-testid="stExpander"] details summary:hover span {{
        color: var(--accent) !important;
    }}
    div[data-testid="stExpander"] details summary:hover svg {{
        fill: var(--accent) !important;
    }}
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
        background-color: var(--surface-1) !important;
        color: var(--fg-muted) !important;
        border-top: 1px solid var(--border) !important;
        padding: 1rem !important;
    }}

    /* File Uploader */
    div[data-testid="stFileUploader"] {{
        background: transparent !important;
    }}
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"],
    div[data-testid="stFileUploader"] section {{
        background-color: var(--surface-2) !important;
        border: 1px dashed var(--surface-5) !important;
        border-radius: 10px !important;
        color: var(--fg-muted) !important;
        transition: border-color 0.2s ease !important;
    }}
    div[data-testid="stFileUploader"] section:hover {{
        border-color: var(--accent) !important;
        background-color: var(--surface-3) !important;
    }}
    div[data-testid="stFileUploader"] section button {{
        background-color: var(--surface-3) !important;
        color: var(--fg-primary) !important;
        border: 1px solid var(--surface-5) !important;
        border-radius: 6px !important;
    }}
    div[data-testid="stFileUploader"] section button:hover {{
        background-color: var(--surface-4) !important;
        color: var(--accent) !important;
        border-color: var(--accent) !important;
    }}
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] p {{
        color: var(--fg-secondary) !important;
    }}

    /* Selectbox & Popovers */
    div[data-baseweb="select"] > div {{
        background-color: var(--surface-2) !important;
        border-color: var(--border) !important;
        color: var(--fg-primary) !important;
    }}
    div[data-baseweb="select"] * {{
        color: var(--fg-primary) !important;
    }}
    div[data-baseweb="popover"],
    ul[role="listbox"] {{
        background-color: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
    }}
    li[role="option"] {{
        background-color: var(--surface-2) !important;
        color: var(--fg-primary) !important;
    }}
    li[role="option"]:hover,
    li[aria-selected="true"] {{
        background-color: var(--surface-3) !important;
        color: var(--accent) !important;
    }}

    /* ─── Self-Healing Patch Cards ─── */
    .heal-patch-card {{
        background: var(--heal-card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }}
    .heal-patch-header {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }}
    .heal-badge-line {{
        background: var(--heal-badge-line-bg);
        border: 1px solid var(--heal-badge-line-border);
        color: var(--accent);
        font-weight: 700;
        font-size: 0.78rem;
        padding: 0.2rem 0.65rem;
        border-radius: 6px;
        letter-spacing: 0.3px;
    }}
    .heal-badge-rule {{
        background: var(--heal-badge-rule-bg);
        border: 1px solid var(--heal-badge-rule-border);
        color: var(--heal-badge-rule-fg);
        font-weight: 600;
        font-size: 0.78rem;
        padding: 0.2rem 0.65rem;
        border-radius: 6px;
    }}
    .heal-badge-status {{
        background: var(--heal-badge-status-bg);
        border: 1px solid var(--heal-badge-status-border);
        color: var(--heal-badge-status-fg);
        font-weight: 700;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        text-transform: uppercase;
        margin-left: auto;
    }}
    .heal-patch-desc {{
        color: var(--fg-muted);
        font-size: 0.88rem;
        margin-bottom: 0.85rem;
        line-height: 1.4;
    }}
    .heal-state-grid {{
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 0.8rem;
        align-items: center;
    }}
    @media (max-width: 768px) {{
        .heal-state-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    .heal-state-col {{
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--border);
    }}
    .heal-state-before {{
        border-color: var(--before-border);
        background: var(--before-bg);
    }}
    .heal-state-after {{
        border-color: var(--after-border);
        background: var(--after-bg);
    }}
    .heal-state-label {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.75rem;
        font-size: 0.75rem;
        background: var(--heal-label-bg);
        border-bottom: 1px solid var(--border);
    }}
    .pill-before {{
        background: var(--pill-before-bg);
        color: var(--pill-before-fg);
        border: 1px solid var(--before-border);
        font-weight: 800;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
    }}
    .pill-after {{
        background: var(--pill-after-bg);
        color: var(--pill-after-fg);
        border: 1px solid var(--after-border);
        font-weight: 800;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
    }}
    .pill-state-sub {{
        color: var(--fg-secondary);
        font-size: 0.75rem;
    }}
    .heal-code-box {{
        padding: 0.6rem 0.8rem;
        font-family: 'Consolas', 'Fira Code', monospace;
        font-size: 0.84rem;
        white-space: pre-wrap;
        word-break: break-all;
        line-height: 1.45;
    }}
    .heal-state-before .heal-code-box {{
        color: var(--code-before-fg);
    }}
    .heal-state-after .heal-code-box {{
        color: var(--code-after-fg);
    }}
    .heal-transition-divider {{
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .heal-arrow-pill {{
        background: var(--arrow-pill-bg);
        border: 1px solid var(--border);
        color: var(--accent);
        font-size: 0.76rem;
        font-weight: 600;
        padding: 0.3rem 0.65rem;
        border-radius: 9999px;
        white-space: nowrap;
    }}
    .heal-summary-bar {{
        display: flex;
        gap: 0.6rem;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }}
    .heal-summary-item {{
        background: var(--surface-3);
        border: 1px solid var(--border);
        color: var(--fg-muted);
        padding: 0.25rem 0.7rem;
        border-radius: 6px;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .heal-summary-val {{
        color: var(--accent);
        font-weight: 700;
    }}

    /* ─── Additional Streamlit overrides for Light mode ─── */
    /* Tab labels */
    .stTabs [data-baseweb="tab-list"] button {{
        color: var(--fg-secondary) !important;
    }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: var(--accent) !important;
    }}
    /* Radio buttons & checkbox labels */
    .stRadio label span,
    .stCheckbox label span {{
        color: var(--fg-primary) !important;
    }}
    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown li {{
        color: var(--fg-primary) !important;
    }}
    /* Metric widgets */
    div[data-testid="stMetricValue"] {{
        color: var(--fg-primary) !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: var(--fg-secondary) !important;
    }}
    /* Code blocks */
    .stCodeBlock {{
        border: 1px solid var(--border) !important;
    }}
    /* Caption */
    .stCaption, div[data-testid="stCaptionContainer"] span {{
        color: var(--fg-secondary) !important;
    }}
    /* Toast / alert banner */
    div[data-testid="stAlert"] {{
        border-color: var(--border) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero Header
st.markdown(
    """
    <div class="hero-banner">
        <h1>Agentic AI Code Intelligence & Security Lab</h1>
        <p>AST &bull; PDG &bull; Qwen LLM &bull; 40+ CWE Security Audits &bull; Self-Healing &bull; Hardware Profiler &bull; Autonomous Green Optimizer</p>
        <div class="author-badge">Project by M. Sathwik & N . Sri Harsha</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Preset Samples: Python
PYTHON_SAMPLE_CODES = {
    "Vulnerable & Inefficient (Full Demo)": '''import os

def process_transaction(user_id, token, records):
    # Hardcoded sensitive credential (CWE-321)
    api_key = "sk_live_992384729384729384"
    
    # O(N^2) inefficient nested search
    matches = []
    for r in records:
        for u in user_id:
            if r == u:
                matches.append(r)
                
    # Arbitrary code execution vulnerability (CWE-94)
    payload = eval(token)
    
    # Insecure shell command execution (CWE-78)
    os.system("echo Audit completed for transaction")
    
    return matches, payload
''',
    "Broken Syntax (Self-Healing Demo)": '''def calculate_metrics(values, factor)
    total = 0
    for v in values
        if v > 0
            total += v * factor
    return total
''',
    "Algorithmic Complexity (O(N^2) Loops)": '''def check_duplicates(list_a, list_b):
    duplicates = []
    for item_a in list_a:
        for item_b in list_b:
            if item_a == item_b:
                duplicates.append(item_a)
    return duplicates
''',
    "Clean Business Logic": '''def compute_interest(principal, rate, years):
    """Calculates simple annual interest."""
    interest = (principal * rate * years) / 100.0
    total = principal + interest
    return total
'''
}

# Preset Samples: C++
CPP_SAMPLE_CODES = {
    "C++ Buffer Overflow & Insecure system() Demo": '''#include <iostream>
#include <cstring>
#include <cstdlib>

void process_user_data(const char* input_str) {
    char buffer[16];
    // CWE-120: Buffer Overflow via unbounded strcpy
    strcpy(buffer, input_str);
    
    // CWE-78: Insecure Shell Command Execution
    system("echo Audit completed for transaction");
}

int main() {
    process_user_data("this_string_is_much_longer_than_sixteen_characters");
    return 0;
}
''',
    "C++ Broken Syntax / Missing Semicolons (Self-Healing Demo)": '''#include <vector>

int calculate_metrics(int factor, int count) {
    int total = 0
    for (int i = 0; i < count; i++) {
        if (i % 2 == 0) {
            total += i * factor
        }
    return total;
}
''',
    "C++ O(N²) Nested Loop Complexity Demo": '''#include <iostream>
#include <vector>

int check_duplicates(const std::vector<int>& list_a, const std::vector<int>& list_b) {
    int duplicates = 0;
    // O(N^2) nested loop comparison
    for (size_t i = 0; i < list_a.size(); ++i) {
        for (size_t j = 0; j < list_b.size(); ++j) {
            if (list_a[i] == list_b[j]) {
                duplicates++;
            }
        }
    }
    return duplicates;
}

int main() {
    std::vector<int> a = {1, 2, 3, 4, 5};
    std::vector<int> b = {3, 4, 5, 6, 7};
    std::cout << "Duplicates: " << check_duplicates(a, b) << std::endl;
    return 0;
}
''',
    "C++ Clean RAII & Memory-Safe Logic": '''#include <iostream>
#include <vector>
#include <numeric>

double calculate_average(const std::vector<double>& scores) {
    if (scores.empty()) {
        return 0.0;
    }
    double sum = std::accumulate(scores.begin(), scores.end(), 0.0);
    return sum / static_cast<double>(scores.size());
}

int main() {
    std::vector<double> scores = {92.5, 88.0, 95.5, 78.0};
    std::cout << "Class average: " << calculate_average(scores) << std::endl;
    return 0;
}
'''
}

# Sidebar Controls
with st.sidebar:
    st.subheader("⚙️ Control Panel")

    # ─── Light / Dark Theme Toggle ───
    _theme_col1, _theme_col2 = st.columns([1, 1])
    with _theme_col1:
        if st.button("☀️ Light" if _is_dark else "☀️ Light ✓", use_container_width=True,
                      type="primary" if not _is_dark else "secondary"):
            st.session_state.theme_mode = "light"
            st.rerun()
    with _theme_col2:
        if st.button("🌙 Dark" if not _is_dark else "🌙 Dark ✓", use_container_width=True,
                      type="primary" if _is_dark else "secondary"):
            st.session_state.theme_mode = "dark"
            st.rerun()
    st.markdown("---")

    selected_language = st.radio("Target Programming Language:", ["Python", "C++"], horizontal=True)

    sample_dict = PYTHON_SAMPLE_CODES if selected_language == "Python" else CPP_SAMPLE_CODES
    selected_sample = st.selectbox("Choose a Benchmark Sample:", list(sample_dict.keys()))

    st.markdown("---")
    st.markdown("### 🤖 Multi-Agent Engine")
    st.markdown(
        """
        - **Agent 0:** Self-Healing Guard
        - **Agent 1:** Structural AST/PDG Inspector
        - **Agent 2:** Green Computing Auditor
        - **Agent 3:** Security Threat Hunter (40+ CWEs)
        - **Agent 4:** Multi-Level Communicator
        """
    )
    st.markdown("---")
    st.caption("Active LLM Backend: Groq / `qwen/qwen3.8-27b`")


# Session state persistence
if "agent_context" not in st.session_state:
    st.session_state.agent_context = None

if "opt_result" not in st.session_state:
    st.session_state.opt_result = None

if "folder_report" not in st.session_state:
    st.session_state.folder_report = None


# Input Source Selector
input_mode = st.radio(
    "📥 Select Input Source Mode:",
    ["✍️ Benchmark Presets", "📄 Upload File(s)", "📁 Project Folder (ZIP / Local)"],
    horizontal=True,
)

initial_code = ""

if input_mode == "✍️ Benchmark Presets":
    initial_code = sample_dict.get(selected_sample, "")

elif input_mode == "📄 Upload File(s)":
    uploaded_files = st.file_uploader(
        f"Upload One or Multiple {selected_language} Scripts:",
        type=["py", "cpp", "cc", "cxx", "h", "hpp", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        if len(uploaded_files) == 1:
            try:
                initial_code = uploaded_files[0].getvalue().decode("utf-8")
            except Exception:
                initial_code = uploaded_files[0].getvalue().decode("latin-1")
            st.info(f"Loaded single file: `{uploaded_files[0].name}`")
        else:
            file_names = [f.name for f in uploaded_files]
            col_u1, col_u2 = st.columns([2.5, 1.5])
            with col_u1:
                chosen_file = st.selectbox(f"Select from {len(uploaded_files)} Uploaded Files to View/Edit:", file_names)
            with col_u2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                run_batch_uploads = st.button("📊 Batch Audit All Uploaded Files", use_container_width=True)

            target_f = next((f for f in uploaded_files if f.name == chosen_file), None)
            if target_f:
                try:
                    initial_code = target_f.getvalue().decode("utf-8")
                except Exception:
                    initial_code = target_f.getvalue().decode("latin-1")

            with st.expander("💾 Save Uploaded Files as a New Folder in Project"):
                c_fn, c_fb = st.columns([2.5, 1.5])
                with c_fn:
                    new_folder_tag = st.text_input("New Folder Name:", value="my_uploaded_code")
                with c_fb:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("Save as Project Folder", use_container_width=True):
                        from pathlib import Path
                        clean_fn = "".join(c for c in new_folder_tag if c.isalnum() or c in ("_", "-")) or "custom_folder"
                        target_dir = Path("input_codes") / clean_fn
                        target_dir.mkdir(parents=True, exist_ok=True)
                        for uf in uploaded_files:
                            with open(target_dir / uf.name, "wb") as f_out:
                                f_out.write(uf.getvalue())
                        st.success(f"Successfully saved {len(uploaded_files)} file(s) into `input_codes/{clean_fn}`!")

            if run_batch_uploads:
                with st.spinner("Auditing uploaded files with Multi-Agent Engine..."):
                    from agent_controller import AgentController
                    controller = AgentController()
                    batch_files = []
                    total_vulns = 0
                    sec_scores = []
                    eco_scores = []
                    for uf in uploaded_files:
                        try:
                            content = uf.getvalue().decode("utf-8")
                        except Exception:
                            content = uf.getvalue().decode("latin-1")
                        f_lang = "cpp" if any(uf.name.lower().endswith(ext) for ext in (".cpp", ".cc", ".cxx", ".h", ".hpp", ".c")) else "python"
                        try:
                            f_ctx = controller.run_workflow(content, language=f_lang)
                            findings = f_ctx.security_profile.get("findings", [])
                            sec_s = f_ctx.security_profile.get("security_score", 100)
                            eco_s = f_ctx.green_profile.get("score", 100)
                            total_vulns += len(findings)
                            sec_scores.append(sec_s)
                            eco_scores.append(eco_s)
                            batch_files.append({
                                "file_name": uf.name,
                                "rel_path": uf.name,
                                "language": f_lang,
                                "lines": len(content.splitlines()),
                                "security_score": sec_s,
                                "security_rating": f_ctx.security_profile.get("rating", "Secure"),
                                "vulnerabilities": len(findings),
                                "cwe_list": [f.get("cwe") for f in findings],
                                "eco_score": eco_s,
                                "eco_rating": f_ctx.green_profile.get("rating", "Efficient"),
                                "healed": f_ctx.healing_report.get("is_healed", False),
                                "context": f_ctx,
                            })
                        except Exception as e:
                            batch_files.append({
                                "file_name": uf.name,
                                "rel_path": uf.name,
                                "language": f_lang,
                                "error": str(e),
                            })
                    st.session_state.folder_report = {
                        "folder_path": f"Batch Upload ({len(uploaded_files)} files)",
                        "total_files": len(batch_files),
                        "total_vulnerabilities": total_vulns,
                        "avg_security_score": round(sum(sec_scores)/len(sec_scores), 1) if sec_scores else 100.0,
                        "avg_eco_score": round(sum(eco_scores)/len(eco_scores), 1) if eco_scores else 100.0,
                        "files": batch_files,
                    }
                    st.success("Batch upload audit completed successfully!")
    else:
        st.info("Upload one or multiple code files to analyze.")
        initial_code = sample_dict.get(selected_sample, "")

elif input_mode == "📁 Project Folder (ZIP / Local)":
    from pathlib import Path
    import zipfile
    import io

    # 1. Dual Ingestion Mode Selector (Best of Both Worlds)
    c_src1, c_src2 = st.columns([1.6, 2.4])
    with c_src1:
        folder_source_type = st.radio(
            "Folder Input Method:",
            ["📦 Upload .ZIP Archive", "📂 Local Directory Path"],
            horizontal=True,
            help="Upload a zipped project from your PC or scan an existing directory on disk."
        )

    active_folder = None
    folder_display_name = ""
    recursive_scan = True

    with c_src2:
        if folder_source_type == "📦 Upload .ZIP Archive":
            uploaded_zip = st.file_uploader(
                "Upload a Project Folder as a .ZIP archive:",
                type=["zip"],
                help="Compress any project folder on your PC into a .zip file and drop it here."
            )
            if uploaded_zip is not None:
                clean_folder_name = "".join(c for c in Path(uploaded_zip.name).stem if c.isalnum() or c in ("_", "-")) or "uploaded_folder"
                dest_folder = Path("uploaded_folders") / clean_folder_name
                dest_folder.mkdir(parents=True, exist_ok=True)
                try:
                    with zipfile.ZipFile(io.BytesIO(uploaded_zip.getvalue())) as z:
                        dest_resolved = dest_folder.resolve()
                        for member in z.namelist():
                            member_path = (dest_folder / member).resolve()
                            if not str(member_path).startswith(str(dest_resolved)):
                                raise Exception("Security check failed: Archive contains unsafe path traversal (Zip-Slip)")
                        z.extractall(dest_folder)
                    active_folder = dest_folder
                    folder_display_name = f"Uploaded ZIP: {clean_folder_name}"
                except Exception as err:
                    st.error(f"Error extracting zip archive: {err}")
            else:
                up_dir = Path("uploaded_folders")
                if up_dir.exists():
                    existing_folders = [p for p in up_dir.iterdir() if p.is_dir()]
                    if existing_folders:
                        prev_sel = st.selectbox(
                            "Or select a previously unpacked project:",
                            ["None"] + [p.name for p in existing_folders]
                        )
                        if prev_sel != "None":
                            active_folder = up_dir / prev_sel
                            folder_display_name = f"Unpacked Project: {prev_sel}"
        else:
            col_lp1, col_lp2 = st.columns([3, 1])
            with col_lp1:
                folder_path_input = st.text_input(
                    "Enter Local Folder Path (Relative or Absolute):",
                    value="input_codes",
                    help="Directory to scan for code files. E.g. 'input_codes' or 'input_codes/graph_15_inputs'"
                )
            with col_lp2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                recursive_scan = st.checkbox("Recursive", value=True, help="Scan all subfolders recursively")

            p_cand = Path(folder_path_input)
            if p_cand.exists() and p_cand.is_dir():
                active_folder = p_cand
                folder_display_name = f"Local Folder: {folder_path_input}"
            else:
                st.error(f"Directory not found: `{folder_path_input}`")

    # If an active folder is resolved and available
    if active_folder and active_folder.exists() and active_folder.is_dir():
        py_exts = {".py"}
        cpp_exts = {".cpp", ".cc", ".cxx", ".h", ".hpp", ".c"}
        target_exts = cpp_exts if selected_language == "C++" else py_exts
        all_code_exts = py_exts | cpp_exts

        walk_iter = active_folder.rglob("*") if recursive_scan else active_folder.glob("*")
        discovered_all = [
            p for p in walk_iter
            if p.is_file() and p.suffix.lower() in all_code_exts
            and not any(x.startswith(".") or x in ("venv", "__pycache__", "build", "dist", "node_modules") for x in p.parts)
        ]
        discovered_matching = [p for p in discovered_all if p.suffix.lower() in target_exts]

        if not discovered_matching:
            st.warning(f"No {selected_language} source files found in `{folder_display_name}`.")
            initial_code = sample_dict.get(selected_sample, "")
        else:
            # 2. Folder-Wise Breakdown & Subfolder Grouping
            subfolder_map = {}
            for p in discovered_matching:
                rel_parent = str(p.relative_to(active_folder).parent).replace("\\", "/")
                if rel_parent in (".", ""):
                    sub_key = "📁 root (top-level)"
                else:
                    sub_key = f"📁 {rel_parent}/"
                subfolder_map.setdefault(sub_key, []).append(p)

            total_files = len(discovered_matching)
            total_subfolders = len(subfolder_map)

            st.success(
                f"✅ **{folder_display_name}** loaded! Found **{total_files}** {selected_language} file(s) across **{total_subfolders}** subfolder/module(s)."
            )

            # 3. Work Partitioning: Folder-Wise & Batch-Wise Controls
            st.markdown("##### 🗂️ Work Partitioning: Folder-Wise & Batch-Wise Controls")
            c_fwise, c_bwise = st.columns([2, 2])

            with c_fwise:
                subfolder_options = ["🌐 All Subfolders (Entire Project)"] + sorted(list(subfolder_map.keys()))
                selected_subfolder = st.selectbox(
                    "📁 Filter Scope (Folder-Wise):",
                    subfolder_options,
                    help="Select a specific subfolder module to isolate or inspect the entire project."
                )

            # Target files based on selected folder-wise filter
            if selected_subfolder == "🌐 All Subfolders (Entire Project)":
                active_scope_files = sorted(discovered_matching)
                scope_label = "Entire Project"
            else:
                active_scope_files = sorted(subfolder_map[selected_subfolder])
                scope_label = selected_subfolder

            with c_bwise:
                c_bsize, c_bact = st.columns([1, 1.3])
                with c_bsize:
                    batch_chunk_size = st.selectbox(
                        "Batch Chunk Size:",
                        [5, 10, 25, "All"],
                        index=1,
                        help="Chunk size for batch processing"
                    )
                with c_bact:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    run_batch_btn = st.button(
                        f"📊 Run Batch Audit ({len(active_scope_files)} files)",
                        use_container_width=True,
                        type="secondary"
                    )

            # 4. Single-File Inspection Bridge
            c_sel_f, c_info = st.columns([3, 1])
            with c_sel_f:
                file_map_scope = {str(p.relative_to(active_folder)).replace("\\", "/"): p for p in active_scope_files}
                chosen_rel_path = st.selectbox(
                    f"Select Specific File to View, Edit & Audit ({len(file_map_scope)} files in scope):",
                    list(file_map_scope.keys())
                )
            with c_info:
                st.caption(f"Language: **{selected_language}**")
                st.caption(f"Active Scope: `{scope_label}`")

            # Load selected single file into initial_code
            if chosen_rel_path and chosen_rel_path in file_map_scope:
                chosen_p = file_map_scope[chosen_rel_path]
                try:
                    with open(chosen_p, "r", encoding="utf-8", errors="replace") as f:
                        initial_code = f.read()
                except Exception as e:
                    st.error(f"Failed to read file {chosen_p}: {e}")

            # 5. Execute Batch Audit (Batch-Wise with Live Progress Bar)
            if run_batch_btn:
                prog_bar = st.progress(0.0)
                status_txt = st.empty()
                batch_files_res = []
                total_vulns = 0
                sec_scores = []
                eco_scores = []

                from agent_controller import AgentController
                controller = AgentController()
                lang_code = "cpp" if selected_language == "C++" else "python"

                total_n = len(active_scope_files)
                for idx, f_path in enumerate(active_scope_files):
                    status_txt.markdown(f"Auditing file **{idx + 1}/{total_n}**: `{f_path.name}`...")
                    prog_bar.progress((idx + 1) / total_n)
                    try:
                        with open(f_path, "r", encoding="utf-8", errors="replace") as f_in:
                            content = f_in.read()
                        ctx = controller.run_workflow(content, language=lang_code)
                        findings = ctx.security_profile.get("findings", [])
                        sec_score = ctx.security_profile.get("security_score", 100)
                        eco_score = ctx.green_profile.get("score", 100)

                        total_vulns += len(findings)
                        sec_scores.append(sec_score)
                        eco_scores.append(eco_score)

                        batch_files_res.append({
                            "file_name": f_path.name,
                            "rel_path": str(f_path.relative_to(active_folder)).replace("\\", "/"),
                            "abs_path": str(f_path.resolve()),
                            "subfolder": str(f_path.relative_to(active_folder).parent).replace("\\", "/"),
                            "language": lang_code,
                            "lines": len(content.splitlines()),
                            "security_score": sec_score,
                            "security_rating": ctx.security_profile.get("rating", "Secure"),
                            "vulnerabilities": len(findings),
                            "cwe_list": [f.get("cwe") for f in findings],
                            "eco_score": eco_score,
                            "eco_rating": ctx.green_profile.get("rating", "Efficient"),
                            "healed": ctx.healing_report.get("is_healed", False),
                            "context": ctx,
                        })
                    except Exception as err:
                        batch_files_res.append({
                            "file_name": f_path.name,
                            "rel_path": str(f_path.relative_to(active_folder)).replace("\\", "/"),
                            "abs_path": str(f_path.resolve()),
                            "subfolder": str(f_path.relative_to(active_folder).parent).replace("\\", "/"),
                            "language": lang_code,
                            "error": str(err),
                        })

                status_txt.empty()
                prog_bar.empty()

                avg_sec = round(sum(sec_scores) / len(sec_scores), 1) if sec_scores else 100.0
                avg_eco = round(sum(eco_scores) / len(eco_scores), 1) if eco_scores else 100.0

                st.session_state.folder_report = {
                    "folder_path": f"{folder_display_name} [{scope_label}]",
                    "total_files": len(batch_files_res),
                    "total_vulnerabilities": total_vulns,
                    "avg_security_score": avg_sec,
                    "avg_eco_score": avg_eco,
                    "files": batch_files_res,
                }
                st.success(f"Batch audit of {len(batch_files_res)} files completed successfully!")
                st.rerun()
    else:
        st.info("📂 **Tip:** Select an upload method above to load a zipped archive or local directory.")
        initial_code = sample_dict.get(selected_sample, "")


# Main Input Columns
col_code, col_act = st.columns([2.5, 1])

with col_code:
    code_input = st.text_area(
        f"{selected_language} Source Code to Analyze:",
        value=initial_code,
        height=280,
    )

with col_act:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    run_agentic = st.button("🚀 Run 5-Agent Intelligence Pipeline", use_container_width=True, type="primary")
    run_optimizer = st.button("⚡ Run Green & Secure Optimizer", use_container_width=True)
    if st.session_state.folder_report is not None:
        if st.button("🗑️ Clear Batch Report", use_container_width=True):
            st.session_state.folder_report = None
            st.rerun()


# Trigger Pipeline Execution
if run_agentic:
    if not code_input.strip():
        st.warning(f"Please provide {selected_language} code to analyze.")
    else:
        with st.spinner(f"🤖 5 Specialized Agents Collaborating on {selected_language} Intelligence..."):
            try:
                import importlib
                import sys
                for mod_name in list(sys.modules.keys()):
                    if mod_name.startswith("polyglot") or mod_name.startswith("agent_security") or mod_name in ("agent_controller", "green_computing", "optimizer_agent", "ast_security_transformer", "security_scanner"):
                        try:
                            importlib.reload(sys.modules[mod_name])
                        except Exception:
                            pass
                from agent_controller import AgentController

                controller = AgentController()
                lang_code = "cpp" if selected_language == "C++" else "python"
                ctx = controller.run_workflow(code_input, language=lang_code)
                st.session_state.agent_context = ctx
                st.success("Multi-Agent Intelligence Synthesis Complete!")
            except Exception as e:
                import traceback
                st.error(f"Error during agentic execution: {e}")
                with st.expander("Detailed Traceback"):
                    st.code(traceback.format_exc(), language="python")

# Trigger Optimizer Execution
if run_optimizer:
    if not code_input.strip():
        st.warning(f"Please provide {selected_language} code to optimize.")
    else:
        with st.spinner(f"⚡ Autonomous Optimizer Refactoring & Verifying {selected_language} Code..."):
            try:
                import importlib
                import sys
                for mod_name in list(sys.modules.keys()):
                    if mod_name.startswith("polyglot") or mod_name.startswith("agent_security") or mod_name in ("agent_controller", "green_computing", "optimizer_agent", "ast_security_transformer", "security_scanner"):
                        try:
                            importlib.reload(sys.modules[mod_name])
                        except Exception:
                            pass
                from optimizer_agent import optimize_code

                lang_code = "cpp" if selected_language == "C++" else "python"
                res = optimize_code(code_input, language=lang_code, dfa=_get_optimizer_dfa())
                st.session_state.opt_result = res
                st.success("Autonomous Optimization & Closed-Loop Verification Finished!")
            except Exception as e:
                import traceback
                st.error(f"Error during optimization: {e}")
                with st.expander("Detailed Traceback"):
                    st.code(traceback.format_exc(), language="python")


# Render Folder / Batch Summary if available
if st.session_state.folder_report is not None:
    rep = st.session_state.folder_report
    with st.expander(f"📁 Folder & Batch Audit Report: {rep['folder_path']} ({rep['total_files']} Files)", expanded=True):
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"<div class='metric-card'><h3>{rep['total_files']}</h3><span>Total Files Scanned</span></div>", unsafe_allow_html=True)
        with m2:
            sec_avg = rep['avg_security_score']
            color = "#34d399" if sec_avg >= 80 else ("#fbbf24" if sec_avg >= 50 else "#f87171")
            st.markdown(f"<div class='metric-card'><h3 style='color: {color}'>{sec_avg}/100</h3><span>Avg Security Score</span></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-card'><h3>{rep['total_vulnerabilities']}</h3><span>Total CWEs Found</span></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-card'><h3>{rep['avg_eco_score']}/100</h3><span>Avg Eco Score</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        rep_tabs = st.tabs(["📂 Folder-Wise Breakdown", "📄 All Files Detailed Audit"])

        with rep_tabs[0]:
            folder_stats = {}
            for f in rep["files"]:
                sub = f.get("subfolder") or str(Path(f.get("rel_path", "")).parent).replace("\\", "/")
                if sub in (".", ""):
                    sub = "root (top-level)"
                if sub not in folder_stats:
                    folder_stats[sub] = {"files": 0, "lines": 0, "vulns": 0, "sec_scores": [], "eco_scores": []}
                folder_stats[sub]["files"] += 1
                folder_stats[sub]["lines"] += f.get("lines", 0)
                folder_stats[sub]["vulns"] += f.get("vulnerabilities", 0)
                if f.get("security_score") is not None:
                    folder_stats[sub]["sec_scores"].append(f.get("security_score"))
                if f.get("eco_score") is not None:
                    folder_stats[sub]["eco_scores"].append(f.get("eco_score"))

            fwise_rows = []
            for sname, sdata in sorted(folder_stats.items()):
                avg_s = round(sum(sdata["sec_scores"]) / len(sdata["sec_scores"]), 1) if sdata["sec_scores"] else 100.0
                avg_e = round(sum(sdata["eco_scores"]) / len(sdata["eco_scores"]), 1) if sdata["eco_scores"] else 100.0
                fwise_rows.append({
                    "Subfolder / Module": sname,
                    "Files Count": sdata["files"],
                    "Total Lines": sdata["lines"],
                    "Avg Security Score": f"{avg_s}/100",
                    "Total CWEs Found": sdata["vulns"],
                    "Avg Eco Score": f"{avg_e}/100",
                    "Risk Status": "🟢 Clean / Secure" if avg_s >= 80 else ("🟡 Moderate Risk" if avg_s >= 50 else "🔴 Critical Risk"),
                })
            if fwise_rows:
                import pandas as pd
                df_fwise = pd.DataFrame(fwise_rows)
                st.dataframe(df_fwise, use_container_width=True, hide_index=True)

        with rep_tabs[1]:
            table_rows = []
            for f in rep["files"]:
                table_rows.append({
                    "File": f.get("rel_path") or f.get("file_name"),
                    "Subfolder": f.get("subfolder") or "root",
                    "Language": f.get("language", "unknown").upper(),
                    "Lines": f.get("lines", 0),
                    "Security Score": f"{f.get('security_score', '-')}/100" if f.get('security_score') is not None else "-",
                    "Risk Rating": f.get("security_rating", "-"),
                    "CWE Findings": f.get("vulnerabilities", 0),
                    "Eco Score": f"{f.get('eco_score', '-')}/100" if f.get('eco_score') is not None else "-",
                    "Rating": f.get("eco_rating", "-"),
                    "Self-Healed": "Yes" if f.get("healed") else "No",
                })
            if table_rows:
                import pandas as pd
                df = pd.DataFrame(table_rows)
                st.dataframe(df, use_container_width=True, hide_index=True)

        file_options = [f.get("rel_path") or f.get("file_name") for f in rep["files"] if "context" in f]
        if file_options:
            c_sel, c_btn = st.columns([3, 1])
            with c_sel:
                selected_batch_file = st.selectbox("🔍 Load specific file results into 5-Agent Pipeline Tabs below:", file_options)
            with c_btn:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("Load File Results", use_container_width=True):
                    chosen_rec = next((f for f in rep["files"] if (f.get("rel_path") or f.get("file_name")) == selected_batch_file), None)
                    if chosen_rec and "context" in chosen_rec:
                        st.session_state.agent_context = chosen_rec["context"]
                        st.success(f"Loaded '{selected_batch_file}' into detailed tabs below!")
                        st.rerun()


# Render Results Tabs
ctx = st.session_state.agent_context
opt = st.session_state.opt_result

if ctx is not None or opt is not None:
    tabs = st.tabs([
        "🧠 Multi-Agent Intelligence",
        "🛡️ Security & CWE Audit",
        "🌐 Interactive PDG Graph",
        "🌿 Green & Hardware Profiler",
        "🌳 AST Structure",
        "⚡ Green & Secure Optimizer"
    ])

    # ─────────────────────────────────────────────────────────────
    # TAB 1: Multi-Agent Intelligence & Summaries
    # ─────────────────────────────────────────────────────────────
    with tabs[0]:
        if ctx is None:
            st.info("Run the 5-Agent Pipeline to view multi-level summaries and live thought trace.")
        else:
            # Self-healing banner if repaired
            healing = ctx.healing_report
            if healing.get('is_healed'):
                text_repairs = healing.get('repairs', [])
                details = healing.get('repair_details', [])

                # Fallback synthesis if repair_details is empty
                if not details and text_repairs:
                    import re
                    raw_lines = ctx.raw_code.splitlines() if getattr(ctx, 'raw_code', None) else []
                    clean_lines = ctx.healed_code.splitlines() if getattr(ctx, 'healed_code', None) else []
                    for r in text_repairs:
                        m = re.search(r'Line (\d+)', str(r))
                        line_idx = int(m.group(1)) if m else None
                        before_val = raw_lines[line_idx - 1] if line_idx and line_idx <= len(raw_lines) else ""
                        after_val = clean_lines[line_idx - 1] if line_idx and line_idx <= len(clean_lines) else ""
                        details.append({
                            'line': line_idx or '?',
                            'rule': 'SYN-001: Syntax Repair',
                            'description': str(r),
                            'before': before_val,
                            'after': after_val,
                            'action': 'Autonomously Healed'
                        })

                lines_touched = sorted(set(d.get('line', 0) for d in details if isinstance(d.get('line'), int)))
                lines_str = ", ".join(f"Line {ln}" for ln in lines_touched) if lines_touched else f"{len(text_repairs)} location(s)"

                st.warning(
                    f"🩹 **Self-Healing Guard Triggered:** Autonomously repaired **{len(text_repairs)}** syntax defect(s) across **{lines_str}**. "
                    "Input code successfully normalized to 100% AST-compliant representation."
                )

                with st.expander("🔍 View Self-Healing Patch Details & State Transitions", expanded=True):
                    import html as _html_mod

                    summary_html = f'''<div class="heal-summary-bar">
  <div class="heal-summary-item">🔧 Defects Healed: <span class="heal-summary-val">{len(text_repairs)}</span></div>
  <div class="heal-summary-item">📝 Lines Modified: <span class="heal-summary-val">{lines_str}</span></div>
  <div class="heal-summary-item">🛡️ Status: <span class="heal-summary-val" style="color:#86efac;">100% AST Valid</span></div>
</div>'''
                    st.markdown(summary_html, unsafe_allow_html=True)

                    if details:
                        for d in details:
                            line_no = d.get('line', '?')
                            rule_esc = _html_mod.escape(str(d.get('rule', 'Syntax Repair')))
                            desc_esc = _html_mod.escape(str(d.get('description', '')))
                            before_esc = _html_mod.escape(str(d.get('before', '')).rstrip())
                            after_esc = _html_mod.escape(str(d.get('after', '')).rstrip())
                            action_esc = _html_mod.escape(str(d.get('action', 'Healed')))

                            card_html = f'''<div class="heal-patch-card">
  <div class="heal-patch-header">
    <span class="heal-badge-line">Line {line_no}</span>
    <span class="heal-badge-rule">{rule_esc}</span>
    <span class="heal-badge-status">HEALED</span>
  </div>
  <div class="heal-patch-desc">{desc_esc}</div>
  <div class="heal-state-grid">
    <div class="heal-state-col heal-state-before">
      <div class="heal-state-label">
        <span class="pill-before">BEFORE</span>
        <span class="pill-state-sub">Malformed Syntax</span>
      </div>
      <div class="heal-code-box">{before_esc if before_esc else "<em>(empty line)</em>"}</div>
    </div>
    <div class="heal-transition-divider">
      <div class="heal-arrow-pill">➔ {action_esc}</div>
    </div>
    <div class="heal-state-col heal-state-after">
      <div class="heal-state-label">
        <span class="pill-after">AFTER</span>
        <span class="pill-state-sub">AST Validated</span>
      </div>
      <div class="heal-code-box">{after_esc if after_esc else "<em>(empty line)</em>"}</div>
    </div>
  </div>
</div>'''
                            st.markdown(card_html, unsafe_allow_html=True)
                    else:
                        for r in text_repairs:
                            st.write(f"- {r}")

            st.markdown("### 📋 3-in-1 Documentation Suite")
            doc_col1, doc_col2 = st.columns([1.2, 1])

            with doc_col1:
                st.markdown("#### 1. Executive Summary")
                st.info(ctx.executive_summary)

                st.markdown("#### 2. Technical Developer Walkthrough")
                st.markdown(ctx.developer_walkthrough)

            with doc_col2:
                doc_title = "3. Production Docstrings (Doxygen /** ... */)" if getattr(ctx, 'language', 'python') == 'cpp' else "3. Production Docstrings (Google/Sphinx)"
                st.markdown(f"#### {doc_title}")
                st.code(ctx.docstrings, language="cpp" if getattr(ctx, 'language', 'python') == 'cpp' else "python")

            st.markdown("---")
            st.markdown("### 🔬 Live Cognitive Thought Trace")
            st.caption("Inspect how Agent 0 through Agent 4 observe, analyze, decide, and act in real time.")
            
            for event in ctx.thought_trace:
                phase_color = {
                    "OBSERVE": "#38bdf8",
                    "ANALYZE": "#818cf8",
                    "DECIDE": "#fbbf24",
                    "ACT": "#34d399"
                }.get(event.phase.value, "#94a3b8")

                st.markdown(
                    f"""
                    <div class="agent-trace-box" style="border-left-color: {phase_color};">
                        <strong style="color: {phase_color};">[{event.phase.value}]</strong>
                        <span style="color: #94a3b8; font-size: 0.8rem; margin-left: 6px;">{event.time_str}</span> &bull;
                        <span style="font-weight: 600; color: #f1f5f9;">{event.agent_id}</span><br/>
                        <span style="color: #cbd5e1;">{event.message}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ─────────────────────────────────────────────────────────────
    # TAB 2: Security & CWE Audit
    # ─────────────────────────────────────────────────────────────
    with tabs[1]:
        if ctx is None:
            st.info("Run the 5-Agent Pipeline to view full security audit results.")
        else:
            sec = ctx.security_profile
            findings = sec.get("findings", [])
            tainted = sec.get("tainted_flows", [])

            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                score = sec.get("security_score", 100)
                score_color = "#34d399" if score >= 80 else ("#fbbf24" if score >= 50 else "#f87171")
                st.markdown(f"<div class='metric-card'><h3 style='color: {score_color}'>{score}/100</h3><span>Security Health Score</span></div>", unsafe_allow_html=True)
            with m2:
                rating = sec.get("rating", "Secure")
                st.markdown(f"<div class='metric-card'><h3>{rating}</h3><span>Risk Rating</span></div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-card'><h3>{len(findings)}</h3><span>Vulnerabilities</span></div>", unsafe_allow_html=True)
            with m4:
                st.markdown(f"<div class='metric-card'><h3>{len(tainted)}</h3><span>Tainted Data Flows</span></div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            st.info(sec.get("summary", ""))

            # Taint Tracking Alerts
            if tainted:
                st.markdown("#### 🚨 PDG Taint Tracking Alerts (Untrusted Flow to Sinks)")
                for t in tainted:
                    st.error(f"**Tainted Flow:** {t.get('description')} (Variable: `{t.get('variable')}` from `{t.get('source_node')}` &rarr; `{t.get('sink_node')}`)")

            # Vulnerabilities List
            st.markdown("#### 🔍 Detected CWE Vulnerabilities")
            if not findings:
                st.success("✅ Clean bill of health! No known CWE vulnerabilities found in code.")
            else:
                for f in findings:
                    sev = f.get("severity", "MEDIUM")
                    sev_badge = "🔴 CRITICAL" if sev == "CRITICAL" else ("🟠 HIGH" if sev == "HIGH" else "🟡 MEDIUM")
                    with st.expander(f"{sev_badge} - Line {f.get('line')}: {f.get('cwe')} ({f.get('category')})"):
                        st.markdown(f"**Defect:** {f.get('message')}")
                        st.markdown(f"**Remediation:** `{f.get('remediation')}`")

            # Remediation Summary
            if sec.get("remediations"):
                st.markdown("#### 💡 Automated Hardening Advice")
                for rem in sec.get("remediations", []):
                    st.write(f"- {rem}")

    # ─────────────────────────────────────────────────────────────
    # TAB 3: Static & High-Contrast PDG Graph
    # ─────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### 🌐 Program Dependence Graph (Static & Clean)")
        st.caption("Structured, motionless dependency graph with zero jitter. Zoom, pan, and click nodes to inspect semantic control and data dependencies.")

        active_graph = ctx.pdg_graph if ctx else None
        active_taints = ctx.security_profile.get("tainted_flows", []) if ctx else []

        if not active_graph:
            from pdg_extractor import extract_pdg_graph
            active_graph = extract_pdg_graph(code_input)

        if active_graph.get("status") == "ok":
            import importlib
            import graph_visualizer
            importlib.reload(graph_visualizer)
            num_nodes = len(active_graph.get("nodes", {}))
            if num_nodes >= 60:
                pdg_height = "760px"
                frame_height = 790
            elif num_nodes >= 25:
                pdg_height = "640px"
                frame_height = 670
            else:
                pdg_height = "550px"
                frame_height = 580
            html_vis = graph_visualizer.generate_pdg_html(active_graph, tainted_flows=active_taints, height=pdg_height, theme=_theme)
            components.html(html_vis, height=frame_height)
        else:
            st.error(f"Failed to generate PDG: {active_graph.get('error')}")

    # ─────────────────────────────────────────────────────────────
    # TAB 4: Green Computing & Hardware Profiler
    # ─────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### 🌿 Green Computing & Runtime Hardware Profiling")
        
        green = ctx.green_profile if ctx else {}
        hw = ctx.hardware_profile if ctx else {}

        # Top row: Hardware real-time metrics
        if hw:
            st.markdown("#### ⚡ Real-Time Dynamic Hardware Performance")
            exec_mode_badge = hw.get('execution_mode', 'standard')
            backend_badge = hw.get('profiler_backend', 'sandbox')
            st.caption(f"**Execution Engine:** `{backend_badge}` &bull; **Mode:** `{exec_mode_badge}`")

            if hw.get('blocked'):
                st.warning(
                    f"🛡️ **Live Execution Prevented by Security Gatekeeper** ({backend_badge})\n\n"
                    f"**Gatekeeper Interception:** {hw.get('summary', 'Critical vulnerability / Shell injection detected in code')}\n\n"
                    "🔒 **Why are metrics 0.00?** To protect your machine from hostile shell tampering or command injection (e.g. CWE-78), "
                    "the AST Gatekeeper intercepts untrusted code before execution. "
                    "Hardware metrics (CPU, RAM, Energy) are intentionally held at **0.00** because execution was prevented before reaching the CPU.\n\n"
                    "⚡ **Remediation:** Run the **⚡ Green & Secure Optimizer** (Tab 6) to sanitize vulnerabilities into secure alternatives, then re-profile for live hardware benchmarks."
                )
            elif hw.get('timed_out'):
                st.warning(
                    f"⏱️ **Execution Halted by Watchdog:** {hw.get('summary', 'Execution exceeded runtime threshold')}"
                )
            elif hw.get('memory_exceeded'):
                st.warning(
                    f"💥 **Execution Halted by Memory Guard:** {hw.get('summary', 'Peak RAM exceeded memory ceiling')}"
                )

            h1, h2, h3, h4 = st.columns(4)
            h1.metric("Execution Latency", f"{hw.get('latency_ms', 0):.2f} ms")
            h2.metric("CPU Execution Time", f"{hw.get('cpu_time_ms', 0):.2f} ms", f"{hw.get('cpu_percent', 0)}% CPU")
            h3.metric("Peak Memory (RAM)", f"{hw.get('peak_ram_mb', 0):.4f} MB")
            h4.metric("Dynamic Energy", f"{hw.get('dynamic_energy_kwh', 0):.8f} kWh")

        st.markdown("#### 🍃 Static Green Computing Profile")
        if green:
            g1, g2, g3 = st.columns(3)
            g1.metric("Eco-Efficiency Score", f"{green.get('score', 100)}/100")
            g2.metric("Rating", green.get("rating", "Efficient"))
            g3.metric("Estimated CO2e", f"{green.get('estimated_co2_kg', 0):.8f} kg")

            st.info(green.get("summary", ""))

            st.markdown("#### Recommendations for Sustainable Code")
            for rec in green.get("recommendations", []):
                st.write(f"- {rec}")

            # Charts
            if "chart_data" in green:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Control Flow Distribution")
                    st.bar_chart({"Value": green["chart_data"].get("Control Flow", {})})
                with c2:
                    st.markdown("##### Efficiency Signals")
                    st.bar_chart({"Value": green["chart_data"].get("Efficiency Signals", {})})

    # ─────────────────────────────────────────────────────────────
    # TAB 5: AST Structure
    # ─────────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("### 🌳 Abstract Syntax Tree (AST) Hierarchy")
        ast_text = ctx.ast_context if ctx else ""
        if not ast_text:
            if selected_language == "C++":
                try:
                    from polyglot.parser_factory import ParserFactory, SupportedLanguage
                    parsed = ParserFactory.parse(code_input, language=SupportedLanguage.CPP)
                    ast_text = AgentController._format_cpp_ast(parsed.root_node) if parsed.root_node else "C++ AST"
                except Exception as e:
                    ast_text = f"C++ AST extraction failed: {e}"
            else:
                from ast_extractor import extract_ast_context
                ast_text = extract_ast_context(code_input)
        st.code(ast_text, language="text")

    # ─────────────────────────────────────────────────────────────
    # TAB 6: Autonomous Green & Secure Optimizer (Placed at Last)
    # ─────────────────────────────────────────────────────────────
    with tabs[5]:
        if opt is None:
            # If agent pipeline was run, offer 1-click optimization
            st.info("Click **⚡ Run Green & Secure Optimizer** to refactor, secure, and verify your code.")
            if st.button("Optimize Current Code Now"):
                with st.spinner(f"Optimizing {selected_language}..."):
                    lang_code = "cpp" if selected_language == "C++" else "python"
                    opt = optimize_code(code_input, language=lang_code, dfa=_get_optimizer_dfa())
                    st.session_state.opt_result = opt
                    st.rerun()
        else:
            # Show Optimizer Results
            verif_badge = "🟢 VERIFIED PASSED" if opt.verified else "🟡 BEST-EFFORT REFACTORED"
            st.markdown(f"### Closed-Loop Verification: {verif_badge}")
            st.caption(opt.verification_notes)

            # Score Delta Cards
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.markdown(f"<div class='metric-card'><h3>{opt.original_eco_score} &rarr; {opt.optimized_eco_score}</h3><span>Eco Score (Delta: +{opt.eco_delta})</span></div>", unsafe_allow_html=True)
            with s2:
                st.markdown(f"<div class='metric-card'><h3>{opt.original_sec_score} &rarr; {opt.optimized_sec_score}</h3><span>Security Score (Delta: +{opt.sec_delta})</span></div>", unsafe_allow_html=True)
            with s3:
                st.markdown(f"<div class='metric-card'><h3>{len(opt.vulnerabilities_fixed)}</h3><span>CWEs Fixed</span></div>", unsafe_allow_html=True)
            with s4:
                st.markdown(f"<div class='metric-card'><h3>{len(opt.algorithmic_improvements)}</h3><span>Optimizations</span></div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

            # Side-by-Side Comparison
            col_orig, col_opt = st.columns(2)
            code_lang = getattr(opt, "language", None) or ("cpp" if selected_language == "C++" else "python")
            with col_orig:
                st.markdown("#### ❌ Original Code")
                st.code(opt.original_code, language=code_lang)
            with col_opt:
                st.markdown("#### ✅ Refactored & Hardened Code")
                st.code(opt.optimized_code, language=code_lang)

            # Unified Diff
            if opt.diff:
                with st.expander("🔍 View Unified Code Diff", expanded=True):
                    st.code(opt.diff, language="diff")

            # Improvements breakdown
            b1, b2 = st.columns(2)
            with b1:
                st.markdown("#### 🛡️ Security Fixes Applied")
                if opt.vulnerabilities_fixed:
                    for v in opt.vulnerabilities_fixed:
                        st.success(f"Fixed: {v}")
                else:
                    st.write("No security vulnerabilities required patching.")
            with b2:
                st.markdown("#### 🌿 Algorithmic Improvements")
                for a in opt.algorithmic_improvements:
                    st.info(f"Speedup: {a}")

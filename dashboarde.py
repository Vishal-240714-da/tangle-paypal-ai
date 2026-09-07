import os
import json

import pandas as pd
import streamlit as st

from agents.review_manager import review_case


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TANGLE | Finance Investigation",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

AGENT_RESULTS_FILE = os.path.join(
    DATA_DIR,
    "agent_results.csv",
)

REVIEW_QUEUE_FILE = os.path.join(
    DATA_DIR,
    "review_queue.csv",
)


# ============================================================
# ENTERPRISE UI / CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background: #F4F6F8;
        color: #172033;
    }

    .main {
        background: #F4F6F8;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.25rem;
        padding-bottom: 4rem;
    }

    p,
    li,
    span,
    div,
    label {
        font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    h1,
    h2,
    h3,
    h4 {
        color: #172033 !important;
        letter-spacing: -0.02em;
    }

    h1 {
        font-weight: 800 !important;
    }

    h2 {
        font-weight: 750 !important;
    }

    h3 {
        font-weight: 700 !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E4E7EC;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.25rem;
    }

    section[data-testid="stSidebar"] * {
        color: #344054;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
    }

    .sidebar-brand {
        padding: 4px 2px 20px 2px;
        border-bottom: 1px solid #EAECF0;
        margin-bottom: 20px;
    }

    .sidebar-brand-name {
        font-size: 23px;
        font-weight: 850;
        color: #102A56;
        letter-spacing: -0.04em;
    }

    .sidebar-brand-subtitle {
        color: #667085;
        font-size: 10px;
        line-height: 1.45;
        margin-top: 4px;
    }

    .sidebar-section {
        color: #667085;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        margin-top: 18px;
        margin-bottom: 10px;
    }

    .active-filter-box {
        background: #F8FAFC;
        border: 1px solid #E4E7EC;
        border-radius: 10px;
        padding: 11px 13px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .active-filter-label {
        color: #667085;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .active-filter-count {
        color: #102A56;
        font-size: 24px;
        font-weight: 800;
        margin-top: 2px;
    }


    /* ========================================================
       APPLICATION HEADER
       ======================================================== */

    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 14px;
        padding: 17px 21px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.025);
    }

    .app-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .app-logo {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: #102A56;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        font-weight: 850;
        letter-spacing: -0.04em;
    }

    .app-name {
        color: #102A56;
        font-size: 21px;
        font-weight: 850;
        line-height: 1;
    }

    .app-description {
        color: #667085;
        font-size: 10px;
        margin-top: 4px;
    }

    .system-status {
        display: flex;
        align-items: center;
        gap: 7px;
        color: #475467;
        font-size: 11px;
        font-weight: 650;
        background: #F8FAFC;
        border: 1px solid #EAECF0;
        border-radius: 20px;
        padding: 7px 11px;
    }

    .system-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #12B76A;
        display: inline-block;
    }


    /* ========================================================
       PAGE HEADINGS
       ======================================================== */

    .page-kicker {
        color: #667085;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.10em;
        margin-bottom: 4px;
    }

    .page-title {
        color: #172033;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 4px;
    }

    .page-description {
        color: #667085;
        font-size: 13px;
        line-height: 1.55;
        margin-bottom: 20px;
    }


    /* ========================================================
       SECTION HEADERS
       ======================================================== */

    .section-header {
        margin-top: 24px;
        margin-bottom: 13px;
    }

    .section-title {
        color: #172033;
        font-size: 17px;
        font-weight: 750;
        letter-spacing: -0.015em;
    }

    .section-description {
        color: #667085;
        font-size: 11px;
        margin-top: 3px;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 16px 17px;
        min-height: 112px;
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.025);
    }

    .kpi-label {
        color: #667085;
        font-size: 9px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.075em;
    }

    .kpi-value {
        color: #172033;
        font-size: 25px;
        font-weight: 820;
        letter-spacing: -0.035em;
        margin-top: 7px;
        line-height: 1.1;
    }

    .kpi-description {
        color: #98A2B3;
        font-size: 10px;
        margin-top: 6px;
    }

    .kpi-accent {
        border-top: 3px solid #102A56;
    }

    .kpi-critical {
        border-top: 3px solid #D92D20;
    }

    .kpi-high {
        border-top: 3px solid #F79009;
    }

    .kpi-review {
        border-top: 3px solid #175CD3;
    }

    .kpi-money {
        border-top: 3px solid #344054;
    }

    .kpi-success {
        border-top: 3px solid #12B76A;
    }


    /* ========================================================
       GENERIC CARDS
       ======================================================== */

    .card {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 13px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 9px rgba(16, 24, 40, 0.025);
    }

    .card-title {
        color: #172033;
        font-size: 14px;
        font-weight: 750;
    }

    .card-description {
        color: #667085;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 3px;
    }

    .metric-label {
        color: #667085;
        font-size: 9px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        color: #172033;
        font-size: 19px;
        font-weight: 800;
        margin-top: 4px;
    }


    /* ========================================================
       BADGES
       ======================================================== */

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 9px;
        line-height: 1;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .badge-critical {
        background: #FEE4E2;
        color: #B42318;
    }

    .badge-high {
        background: #FFF0E6;
        color: #C4320A;
    }

    .badge-medium {
        background: #FFF7D6;
        color: #9A6700;
    }

    .badge-low {
        background: #ECFDF3;
        color: #087443;
    }

    .badge-approved {
        background: #ECFDF3;
        color: #087443;
    }

    .badge-rejected {
        background: #FEE4E2;
        color: #B42318;
    }

    .badge-pending {
        background: #FFF7D6;
        color: #9A6700;
    }

    .badge-escalated {
        background: #FFF0E6;
        color: #C4320A;
    }

    .badge-open {
        background: #EEF4FF;
        color: #175CD3;
    }

    .badge-investigating {
        background: #EEF4FF;
        color: #175CD3;
    }

    .badge-resolved {
        background: #ECFDF3;
        color: #087443;
    }

    .badge-neutral {
        background: #F2F4F7;
        color: #475467;
    }


    /* ========================================================
       CASE HEADER
       ======================================================== */

    .case-header {
        background: #FFFFFF;
        border: 1px solid #DDE5F0;
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 17px;
        box-shadow: 0 3px 11px rgba(16, 24, 40, 0.035);
    }

    .case-id {
        color: #102A56;
        font-size: 25px;
        font-weight: 850;
        letter-spacing: -0.035em;
    }

    .case-category {
        color: #667085;
        font-size: 11px;
        margin-top: 4px;
    }

    .case-stat-label {
        color: #98A2B3;
        font-size: 9px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .case-stat-value {
        color: #172033;
        font-size: 15px;
        font-weight: 780;
        margin-top: 3px;
    }


    /* ========================================================
       TRANSACTION CHAIN
       ======================================================== */

    .chain-container {
        display: flex;
        align-items: stretch;
        gap: 8px;
        margin-bottom: 16px;
    }

    .chain-node {
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 16px;
        min-height: 145px;
    }

    .chain-node.missing {
        background: #FFFAFA;
        border-color: #FECACA;
    }

    .chain-node-icon {
        width: 34px;
        height: 34px;
        border-radius: 9px;
        background: #EEF4FF;
        color: #175CD3;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 11px;
    }

    .chain-node.missing .chain-node-icon {
        background: #FEE4E2;
        color: #B42318;
    }

    .chain-node-title {
        color: #172033;
        font-size: 13px;
        font-weight: 750;
    }

    .chain-node-id {
        color: #175CD3;
        font-size: 10px;
        font-weight: 700;
        margin-top: 3px;
    }

    .chain-node-detail {
        color: #667085;
        font-size: 10px;
        line-height: 1.7;
        margin-top: 8px;
    }

    .chain-arrow {
        display: flex;
        align-items: center;
        color: #98A2B3;
        font-size: 18px;
        font-weight: 700;
    }


    /* ========================================================
       AI PANELS
       ======================================================== */

    .ai-panel {
        background: #F8FAFC;
        border: 1px solid #DDE5F0;
        border-left: 3px solid #175CD3;
        border-radius: 11px;
        padding: 15px 17px;
        margin-bottom: 10px;
    }

    .ai-label {
        color: #175CD3;
        font-size: 9px;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }

    .ai-content {
        color: #344054;
        font-size: 12px;
        line-height: 1.6;
    }


    /* ========================================================
       RISK PANEL
       ======================================================== */

    .risk-panel {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 13px;
        padding: 18px;
        box-shadow: 0 2px 9px rgba(16, 24, 40, 0.025);
    }

    .risk-score {
        color: #172033;
        font-size: 38px;
        font-weight: 850;
        letter-spacing: -0.04em;
    }

    .risk-score-label {
        color: #667085;
        font-size: 10px;
    }

    .risk-bar {
        height: 8px;
        background: #EAECF0;
        border-radius: 999px;
        overflow: hidden;
        margin: 11px 0 14px 0;
    }

    .risk-bar-fill {
        height: 100%;
        background: #175CD3;
        border-radius: 999px;
    }

    .risk-reason {
        background: #F8FAFC;
        border: 1px solid #EAECF0;
        border-radius: 8px;
        padding: 9px 10px;
        margin-bottom: 6px;
        color: #475467;
        font-size: 10px;
        line-height: 1.45;
    }


    /* ========================================================
       REVIEW PANEL
       ======================================================== */

    .review-panel {
        background: #FFFFFF;
        border: 1px solid #D9E2F0;
        border-radius: 13px;
        padding: 19px;
        box-shadow: 0 3px 12px rgba(16, 24, 40, 0.035);
    }

    .review-panel-title {
        color: #172033;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .review-panel-description {
        color: #667085;
        font-size: 11px;
        margin-bottom: 14px;
    }


    /* ========================================================
       REVIEW SUMMARY CARDS
       ======================================================== */

    .review-summary {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 11px;
        padding: 13px 14px;
        min-height: 82px;
    }

    .review-summary-label {
        color: #667085;
        font-size: 9px;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .review-summary-value {
        color: #172033;
        font-size: 22px;
        font-weight: 820;
        margin-top: 5px;
    }


    /* ========================================================
       EMPTY STATES
       ======================================================== */

    .empty-state {
        background: #FFFFFF;
        border: 1px dashed #D0D5DD;
        border-radius: 13px;
        padding: 35px 25px;
        text-align: center;
        margin: 10px 0 18px 0;
    }

    .empty-state-title {
        color: #344054;
        font-size: 14px;
        font-weight: 750;
    }

    .empty-state-description {
        color: #98A2B3;
        font-size: 11px;
        margin-top: 5px;
    }


    /* ========================================================
       BUTTONS / INPUTS
       ======================================================== */

    .stButton > button {
        border-radius: 8px;
        min-height: 40px;
        font-weight: 700;
        border: 1px solid #D0D5DD;
    }

    .stButton > button[kind="primary"] {
        background: #175CD3;
        border-color: #175CD3;
        color: #FFFFFF;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1246A6;
        border-color: #1246A6;
        color: #FFFFFF;
    }

    div[data-baseweb="select"] > div {
        border-radius: 8px;
        border-color: #D0D5DD;
    }

    textarea {
        border-radius: 8px !important;
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {
        color: #667085;
        font-weight: 700;
        font-size: 12px;
        padding: 11px 17px;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #175CD3;
    }


    /* ========================================================
       DATAFRAME
       ======================================================== */

    div[data-testid="stDataFrame"] {
        border: 1px solid #E4E7EC;
        border-radius: 10px;
        overflow: hidden;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    div[data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 10px;
        margin-bottom: 8px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        margin-top: 42px;
        padding: 20px;
        text-align: center;
        border-top: 1px solid #E4E7EC;
        color: #98A2B3;
        font-size: 10px;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=10)
def load_agent_results():
    """Load AI-generated investigation results."""

    if not os.path.exists(AGENT_RESULTS_FILE):
        return pd.DataFrame()

    try:
        return pd.read_csv(AGENT_RESULTS_FILE)

    except Exception as error:
        st.error(
            f"Unable to read agent_results.csv: {error}"
        )
        return pd.DataFrame()


@st.cache_data(ttl=10)
def load_reviews():
    """Load human review queue."""

    if not os.path.exists(REVIEW_QUEUE_FILE):
        return pd.DataFrame()

    try:
        df = pd.read_csv(
            REVIEW_QUEUE_FILE,
            dtype=str,
        )

        return df.fillna("")

    except Exception as error:
        st.error(
            f"Unable to read review_queue.csv: {error}"
        )
        return pd.DataFrame()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe_float(value, default=0.0):
    """Safely convert a value to float."""

    try:
        if value is None:
            return default

        if pd.isna(value):
            return default

        return float(value)

    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Safely convert a value to integer."""

    try:
        if value is None:
            return default

        if pd.isna(value):
            return default

        return int(float(value))

    except (ValueError, TypeError):
        return default


def format_currency(value):
    """Format a number as financial currency."""

    number = safe_float(value)
    return f"₹{number:,.2f}"


def format_percentage(value):
    """Format a number as percentage."""

    number = safe_float(value)
    return f"{number:.2f}%"


def normalize_text(value):
    """Normalize text safely."""

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""

    except Exception:
        pass

    return str(value).strip()


def parse_reasoning_steps(value):
    """Parse reasoning stored as JSON or plain text."""

    if value is None:
        return []

    if isinstance(value, list):
        return value

    try:
        if pd.isna(value):
            return []

    except Exception:
        pass

    try:
        steps = json.loads(value)

        if isinstance(steps, list):
            return steps

    except Exception:
        pass

    return [str(value)]


def risk_order(value):
    """Return sorting priority for risk levels."""

    order = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    return order.get(
        normalize_text(value).upper(),
        0,
    )


def get_badge_class(value):
    """Map semantic values to CSS badge classes."""

    value = normalize_text(value).upper()

    mapping = {
        "CRITICAL": "badge-critical",
        "HIGH": "badge-high",
        "MEDIUM": "badge-medium",
        "LOW": "badge-low",
        "APPROVED": "badge-approved",
        "REJECTED": "badge-rejected",
        "PENDING": "badge-pending",
        "PENDING_REVIEW": "badge-pending",
        "ESCALATED": "badge-escalated",
        "OPEN": "badge-open",
        "INVESTIGATING": "badge-investigating",
        "RESOLVED": "badge-resolved",
        "COMPLETED": "badge-approved",
    }

    return mapping.get(
        value,
        "badge-neutral",
    )


def render_badge(value):
    """Return a reusable HTML status/risk badge."""

    text = normalize_text(value) or "UNKNOWN"

    css_class = get_badge_class(text)

    return (
        f'<span class="badge {css_class}">'
        f'{text.replace("_", " ")}'
        f'</span>'
    )


def render_section_header(title, description=""):
    """Render a consistent section heading."""

    description_html = ""

    if description:
        description_html = (
            f'<div class="section-description">'
            f'{description}'
            f'</div>'
        )

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">{title}</div>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label,
    value,
    description="",
    accent="accent",
):
    """Render a reusable KPI card."""

    st.markdown(
        f"""
        <div class="kpi-card kpi-{accent}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label, value):
    """Render a compact metric card."""

    st.markdown(
        f"""
        <div class="card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_panel(label, content):
    """Render an AI investigation information panel."""

    text = normalize_text(content)

    if not text:
        text = "No information available."

    st.markdown(
        f"""
        <div class="ai-panel">
            <div class="ai-label">{label}</div>
            <div class="ai-content">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BUILD MASTER DASHBOARD DATA
# ============================================================

def build_dashboard_data(agent_df, review_df):
    """
    Build the master dataframe used by the TANGLE dashboard.

    agent_results.csv is the source of AI investigation data.

    review_queue.csv is the authoritative source for:

        - case_status
        - review_status
        - reviewer_decision
        - reviewer_comment
        - reviewed_at
        - final_status

    Human lifecycle information therefore overrides
    default lifecycle information from agent results.
    """

    if agent_df.empty:
        return pd.DataFrame()

    df = agent_df.copy()

    if "case_id" not in df.columns:
        df["case_id"] = ""

    df["case_id"] = (
        df["case_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    lifecycle_columns = [
        "case_status",
        "review_status",
        "reviewer_decision",
        "reviewer_comment",
        "reviewed_at",
        "final_status",
    ]

    defaults = {
        "case_status": "OPEN",
        "review_status": "",
        "reviewer_decision": "",
        "reviewer_comment": "",
        "reviewed_at": "",
        "final_status": "",
    }

    # Ensure all lifecycle columns exist.
    for column in lifecycle_columns:

        if column not in df.columns:
            df[column] = defaults[column]

        else:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # If there is no review queue, keep the AI-side data.
    if review_df.empty:
        return df

    if "case_id" not in review_df.columns:
        return df

    available_columns = ["case_id"] + [
        column
        for column in lifecycle_columns
        if column in review_df.columns
    ]

    review_subset = review_df[
        available_columns
    ].copy()

    review_subset["case_id"] = (
        review_subset["case_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # A case should have one authoritative review record.
    # Keeping the last record protects the latest analyst decision.
    review_subset = (
        review_subset
        .drop_duplicates(
            subset=["case_id"],
            keep="last",
        )
    )

    # Merge review data without destroying AI data.
    df = df.merge(
        review_subset,
        on="case_id",
        how="left",
        suffixes=("", "_review"),
    )

    # IMPORTANT:
    # review_queue.csv wins whenever it contains a value.
    for column in lifecycle_columns:

        review_column = f"{column}_review"

        if review_column in df.columns:

            review_values = (
                df[review_column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            existing_values = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df[column] = review_values.where(
                review_values != "",
                existing_values,
            )

            df.drop(
                columns=[review_column],
                inplace=True,
            )

    # Final normalization.
    for column in lifecycle_columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Only use OPEN as a default when there is genuinely
    # no lifecycle information.
    df["case_status"] = df[
        "case_status"
    ].replace("", "OPEN")

    return df


# ============================================================
# APPLICATION HEADER
# ============================================================

st.markdown(
    """
    <div class="app-header">

        <div class="app-brand">

            <div class="app-logo">
                TG
            </div>

            <div>
                <div class="app-name">
                    TANGLE
                </div>

                <div class="app-description">
                    Transaction Anomaly & Governance Ledger Engine
                </div>
            </div>

        </div>

        <div class="system-status">
            <span class="system-dot"></span>
            System Operational
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

agent_df = load_agent_results()
review_df = load_reviews()


# ============================================================
# DATA AVAILABILITY CHECK
# ============================================================

if not os.path.exists(AGENT_RESULTS_FILE):

    st.error(
        "TANGLE investigation data is unavailable. "
        "The file data/agent_results.csv could not be found."
    )

    st.stop()


if agent_df.empty:

    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-state-title">
                No investigation cases available
            </div>

            <div class="empty-state-description">
                Run the TANGLE agent pipeline to generate
                investigation results.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# BUILD MASTER DATASET
# ============================================================

df = build_dashboard_data(
    agent_df,
    review_df,
)


# ============================================================
# DATA NORMALIZATION
# ============================================================

for column in [
    "risk_level",
    "exception_category",
    "case_status",
    "review_status",
    "reviewer_decision",
    "reviewer_comment",
    "reviewed_at",
    "final_status",
]:

    if column in df.columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )


if "human_review_required" in df.columns:

    df["human_review_required"] = (
        df["human_review_required"]
        .fillna(False)
        .astype(str)
        .str.upper()
        .isin(
            [
                "TRUE",
                "1",
                "YES",
            ]
        )
    )

else:

    df["human_review_required"] = False


if "risk_level" not in df.columns:
    df["risk_level"] = "UNKNOWN"


if "exception_category" not in df.columns:
    df["exception_category"] = "UNKNOWN"


if "case_status" not in df.columns:
    df["case_status"] = "OPEN"


if "priority_score" not in df.columns:
    df["priority_score"] = 0


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-brand-name">
                TANGLE
            </div>

            <div class="sidebar-brand-subtitle">
                Finance Investigation & Risk Operations
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Filters</div>',
        unsafe_allow_html=True,
    )

    risk_values = sorted(
        [
            value
            for value in df["risk_level"].dropna().unique()
            if normalize_text(value)
        ],
        key=risk_order,
        reverse=True,
    )

    selected_risks = st.multiselect(
        "Risk Level",
        options=risk_values,
        default=risk_values,
    )

    category_values = sorted(
        [
            value
            for value in df[
                "exception_category"
            ].dropna().unique()
            if normalize_text(value)
        ]
    )

    selected_categories = st.multiselect(
        "Exception Category",
        options=category_values,
        default=category_values,
    )

    status_values = [
        "OPEN",
        "INVESTIGATING",
        "PENDING_REVIEW",
        "APPROVED",
        "REJECTED",
        "ESCALATED",
        "RESOLVED",
    ]

    existing_statuses = [
        value
        for value in status_values
        if value in set(
            df["case_status"].str.upper()
        )
    ]

    selected_statuses = st.multiselect(
        "Case Status",
        options=existing_statuses,
        default=existing_statuses,
    )

    selected_review = st.selectbox(
        "Human Review Required",
        options=[
            "All",
            "Required",
            "Not Required",
        ],
    )

    # --------------------------------------------------------
    # FILTER APPLICATION
    # --------------------------------------------------------

    filtered_df = df.copy()

    if selected_risks:
        filtered_df = filtered_df[
            filtered_df["risk_level"].str.upper().isin(
                [
                    str(value).upper()
                    for value in selected_risks
                ]
            )
        ]

    if selected_categories:
        filtered_df = filtered_df[
            filtered_df[
                "exception_category"
            ].isin(selected_categories)
        ]

    if selected_statuses:
        filtered_df = filtered_df[
            filtered_df[
                "case_status"
            ].str.upper().isin(selected_statuses)
        ]

    if selected_review == "Required":

        filtered_df = filtered_df[
            filtered_df["human_review_required"]
        ]

    elif selected_review == "Not Required":

        filtered_df = filtered_df[
            ~filtered_df["human_review_required"]
        ]

    # --------------------------------------------------------
    # ACTIVE FILTERS
    # --------------------------------------------------------

    active_filter_count = 0

    if len(selected_risks) != len(risk_values):
        active_filter_count += 1

    if len(selected_categories) != len(category_values):
        active_filter_count += 1

    if len(selected_statuses) != len(existing_statuses):
        active_filter_count += 1

    if selected_review != "All":
        active_filter_count += 1

    st.markdown(
        f"""
        <div class="active-filter-box">

            <div class="active-filter-label">
                Active Filters
            </div>

            <div class="active-filter-count">
                {active_filter_count}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Reset Filters",
        use_container_width=True,
    ):

        st.rerun()

    st.markdown(
        """
        <div style="
            margin-top:22px;
            padding-top:16px;
            border-top:1px solid #EAECF0;
            color:#98A2B3;
            font-size:10px;
            line-height:1.6;
        ">
            TANGLE uses AI-assisted investigation,
            risk scoring and human governance to
            support financial reconciliation.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="page-kicker">
        Finance Risk Operations
    </div>

    <div class="page-title">
        Investigation Control Center
    </div>

    <div class="page-description">
        Monitor transaction anomalies, review high-risk cases,
        and investigate financial reconciliation exceptions.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

overview_tab, review_tab, analytics_tab, investigation_tab = st.tabs(
    [
        "Overview",
        "Human Review",
        "Exception Analytics",
        "Case Investigation",
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with overview_tab:

    total_cases = len(filtered_df)

    critical_cases = len(
        filtered_df[
            filtered_df["risk_level"].str.upper()
            == "CRITICAL"
        ]
    )

    high_cases = len(
        filtered_df[
            filtered_df["risk_level"].str.upper()
            == "HIGH"
        ]
    )

    review_required = int(
        filtered_df[
            "human_review_required"
        ].sum()
    )

    outstanding_balance = filtered_df.get(
        "outstanding_amount",
        pd.Series(dtype=float),
    ).apply(safe_float).sum()

    avg_coverage = filtered_df.get(
        "payment_coverage_pct",
        pd.Series(dtype=float),
    ).apply(safe_float).mean()

    if pd.isna(avg_coverage):
        avg_coverage = 0.0

    resolved_statuses = {
        "APPROVED",
        "REJECTED",
        "RESOLVED",
    }

    resolved_cases = len(
        filtered_df[
            filtered_df[
                "case_status"
            ].str.upper().isin(
                resolved_statuses
            )
        ]
    )

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    render_section_header(
        "Operational Summary",
        "Current financial investigation workload and exposure.",
    )

    kpi_columns = st.columns(
        4,
        gap="medium",
    )

    with kpi_columns[0]:
        render_kpi_card(
            "Total Cases",
            f"{total_cases:,}",
            "AI-investigated cases",
            "accent",
        )

    with kpi_columns[1]:
        render_kpi_card(
            "Critical Cases",
            f"{critical_cases:,}",
            "Highest risk classification",
            "critical",
        )

    with kpi_columns[2]:
        render_kpi_card(
            "High Risk Cases",
            f"{high_cases:,}",
            "Requires close attention",
            "high",
        )

    with kpi_columns[3]:
        render_kpi_card(
            "Human Review",
            f"{review_required:,}",
            "Cases requiring analyst action",
            "review",
        )

    kpi_columns_2 = st.columns(
        3,
        gap="medium",
    )

    with kpi_columns_2[0]:
        render_kpi_card(
            "Outstanding Balance",
            format_currency(outstanding_balance),
            "Financial exposure identified",
            "money",
        )

    with kpi_columns_2[1]:
        render_kpi_card(
            "Avg Payment Coverage",
            format_percentage(avg_coverage),
            "Average invoice coverage",
            "accent",
        )

    with kpi_columns_2[2]:
        render_kpi_card(
            "Resolved / Approved",
            f"{resolved_cases:,}",
            "Cases with completed outcome",
            "success",
        )

    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    render_section_header(
        "Risk Distribution",
        "Distribution of cases across the current risk classification.",
    )

    risk_counts = (
        filtered_df[
            "risk_level"
        ]
        .str.upper()
        .value_counts()
        .reindex(
            [
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
            fill_value=0,
        )
    )

    risk_col_1, risk_col_2 = st.columns(
        [1.35, 1],
        gap="large",
    )

    with risk_col_1:

        risk_chart = pd.DataFrame(
            {
                "Risk Level": risk_counts.index,
                "Cases": risk_counts.values,
            }
        ).set_index("Risk Level")

        st.bar_chart(
            risk_chart,
            height=280,
        )

    with risk_col_2:

        total_risk = int(risk_counts.sum())

        for risk_name, count in risk_counts.items():

            percentage = (
                (count / total_risk) * 100
                if total_risk
                else 0
            )

            st.markdown(
                f"""
                <div class="card"
                     style="margin-bottom:8px;padding:13px 15px;">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                    ">

                        <div>
                            {render_badge(risk_name)}
                        </div>

                        <div style="
                            color:#172033;
                            font-size:15px;
                            font-weight:800;
                        ">
                            {int(count):,}
                        </div>

                    </div>

                    <div style="
                        margin-top:7px;
                        color:#98A2B3;
                        font-size:10px;
                    ">
                        {percentage:.1f}% of filtered cases
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # EXCEPTION CATEGORIES
    # --------------------------------------------------------

    render_section_header(
        "Exception Categories",
        "Primary anomaly types detected by the reconciliation engine.",
    )

    category_counts = (
        filtered_df[
            "exception_category"
        ]
        .value_counts()
    )

    if category_counts.empty:

        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-title">
                    No exception categories available
                </div>
                <div class="empty-state-description">
                    No cases match the selected filters.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        category_chart = pd.DataFrame(
            {
                "Exception Category": category_counts.index,
                "Cases": category_counts.values,
            }
        ).set_index(
            "Exception Category"
        )

        st.bar_chart(
            category_chart,
            height=300,
        )

    # --------------------------------------------------------
    # CASE LIFECYCLE
    # --------------------------------------------------------

    render_section_header(
        "Case Lifecycle",
        "Current position of cases in the investigation and governance workflow.",
    )

    lifecycle_order = [
        "OPEN",
        "INVESTIGATING",
        "PENDING_REVIEW",
        "APPROVED",
        "REJECTED",
        "ESCALATED",
        "RESOLVED",
    ]

    lifecycle_counts = (
        filtered_df[
            "case_status"
        ]
        .str.upper()
        .value_counts()
        .reindex(
            lifecycle_order,
            fill_value=0,
        )
    )

    lifecycle_chart = pd.DataFrame(
        {
            "Lifecycle": lifecycle_counts.index,
            "Cases": lifecycle_counts.values,
        }
    ).set_index("Lifecycle")

    st.bar_chart(
        lifecycle_chart,
        height=300,
    )

    # --------------------------------------------------------
    # PRIORITY INSIGHTS
    # --------------------------------------------------------

    render_section_header(
        "Priority & Risk Insights",
        "High-level indicators for operational prioritization.",
    )

    priority_col_1, priority_col_2 = st.columns(
        2,
        gap="large",
    )

    with priority_col_1:

        priority_series = filtered_df.get(
            "priority_score",
            pd.Series(dtype=float),
        ).apply(safe_float)

        avg_priority = (
            priority_series.mean()
            if not priority_series.empty
            else 0
        )

        max_priority = (
            priority_series.max()
            if not priority_series.empty
            else 0
        )

        render_metric_card(
            "Average Priority Score",
            f"{avg_priority:.1f}",
        )

        render_metric_card(
            "Highest Priority Score",
            f"{max_priority:.1f}",
        )

    with priority_col_2:

        human_review_rate = (
            (
                filtered_df[
                    "human_review_required"
                ].mean()
                * 100
            )
            if len(filtered_df)
            else 0
        )

        render_metric_card(
            "Human Review Rate",
            f"{human_review_rate:.2f}%",
        )

        outstanding_count = len(
    filtered_df[
        filtered_df.get(
            "outstanding_amount",
            pd.Series(
                0,
                index=filtered_df.index,
            ),
        ).apply(safe_float) > 0
    ]
)

        render_metric_card(
            "Cases With Outstanding Balance",
            f"{outstanding_count:,}",
        )


# ============================================================
# HUMAN REVIEW
# ============================================================

with review_tab:

    st.markdown(
        """
        <div class="page-kicker">
            Governance Workflow
        </div>

        <div class="page-title">
            Human Review Queue
        </div>

        <div class="page-description">
            Cases requiring analyst validation, approval,
            rejection, or escalation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # REVIEW DATA
    # --------------------------------------------------------

    if review_df.empty:

        st.markdown(
            """
            <div class="empty-state">

                <div class="empty-state-title">
                    No human reviews are currently available
                </div>

                <div class="empty-state-description">
                    The review queue is empty or
                    review_queue.csv has not been generated yet.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        review_display = review_df.copy()

        # ----------------------------------------------------
        # REVIEW SUMMARY
        # ----------------------------------------------------

        review_status_series = (
            review_display.get(
                "review_status",
                pd.Series(
                    "",
                    index=review_display.index,
                ),
            )
            .fillna("")
            .astype(str)
            .str.upper()
        )

        decision_series = (
            review_display.get(
                "reviewer_decision",
                pd.Series(
                    "",
                    index=review_display.index,
                ),
            )
            .fillna("")
            .astype(str)
            .str.upper()
        )

        pending_count = int(
            (
                review_status_series
                != "COMPLETED"
            ).sum()
        )

        completed_count = int(
            (
                review_status_series
                == "COMPLETED"
            ).sum()
        )

        approved_count = int(
            (
                decision_series
                == "APPROVE"
            ).sum()
        )

        rejected_count = int(
            (
                decision_series
                == "REJECT"
            ).sum()
        )

        escalated_count = int(
            (
                decision_series
                == "ESCALATE"
            ).sum()
        )

        summary_columns = st.columns(
            5,
            gap="small",
        )

        summary_values = [
            (
                "Pending Reviews",
                pending_count,
            ),
            (
                "Completed",
                completed_count,
            ),
            (
                "Approved",
                approved_count,
            ),
            (
                "Rejected",
                rejected_count,
            ),
            (
                "Escalated",
                escalated_count,
            ),
        ]

        for column, (label, value) in zip(
            summary_columns,
            summary_values,
        ):

            with column:

                st.markdown(
                    f"""
                    <div class="review-summary">

                        <div class="review-summary-label">
                            {label}
                        </div>

                        <div class="review-summary-value">
                            {value:,}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ----------------------------------------------------
        # REVIEW TABLE
        # ----------------------------------------------------

        render_section_header(
            "Review Queue",
            "Select a case below to open the analyst review workspace.",
        )

        review_table = review_display.copy()

        if "case_id" not in review_table.columns:
            review_table["case_id"] = ""

        display_columns = [
            "case_id",
            "risk_level",
            "priority_score",
            "exception_category",
            "case_status",
            "review_status",
            "reviewer_decision",
        ]

        available_display_columns = [
            column
            for column in display_columns
            if column in review_table.columns
        ]

        review_table = review_table[
            available_display_columns
        ].copy()

        rename_columns = {
            "case_id": "Case ID",
            "risk_level": "Risk",
            "priority_score": "Priority",
            "exception_category": "Exception",
            "case_status": "Case Status",
            "review_status": "Review Status",
            "reviewer_decision": "Decision",
        }

        review_table.rename(
            columns=rename_columns,
            inplace=True,
        )

        if "Priority" in review_table.columns:

            review_table["Priority"] = (
                review_table[
                    "Priority"
                ]
                .apply(safe_float)
                .round(1)
            )

        st.dataframe(
            review_table,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # CASE SELECTION
        # ----------------------------------------------------

        case_ids = [
            normalize_text(value)
            for value in review_display[
                "case_id"
            ].tolist()
            if normalize_text(value)
        ]

        if not case_ids:

            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-state-title">
                        No review cases available
                    </div>
                    <div class="empty-state-description">
                        The review queue does not contain valid case IDs.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            selected_review_case = st.selectbox(
                "Select Case for Review",
                options=case_ids,
                key="review_case_selector",
            )

            selected_row = df[
                df["case_id"].astype(str)
                == str(selected_review_case)
            ]

            if selected_row.empty:

                st.warning(
                    "The selected case could not be found "
                    "in agent_results.csv."
                )

            else:

                case = selected_row.iloc[0]

                st.markdown(
                    '<div class="review-panel">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    """
                    <div class="review-panel-title">
                        Analyst Review Workspace
                    </div>

                    <div class="review-panel-description">
                        Review the AI investigation before recording
                        a governance decision.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # --------------------------------------------
                # CASE SUMMARY
                # --------------------------------------------

                summary_columns = st.columns(
                    5,
                    gap="small",
                )

                summary_data = [
                    (
                        "Case ID",
                        normalize_text(
                            case.get(
                                "case_id",
                                "",
                            )
                        ),
                    ),
                    (
                        "Risk",
                        render_badge(
                            case.get(
                                "risk_level",
                                "",
                            )
                        ),
                    ),
                    (
                        "Priority",
                        f"{safe_float(case.get('priority_score', 0)):.1f}",
                    ),
                    (
                        "Exception",
                        normalize_text(
                            case.get(
                                "exception_category",
                                "",
                            )
                        ).replace(
                            "_",
                            " ",
                        ),
                    ),
                    (
                        "Current Status",
                        render_badge(
                            case.get(
                                "case_status",
                                "OPEN",
                            )
                        ),
                    ),
                ]

                for column, (
                    label,
                    value,
                ) in zip(
                    summary_columns,
                    summary_data,
                ):

                    with column:

                        st.markdown(
                            f"""
                            <div style="padding:6px 2px;">

                                <div class="case-stat-label">
                                    {label}
                                </div>

                                <div class="case-stat-value">
                                    {value}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                # --------------------------------------------
                # AI RECOMMENDATION
                # --------------------------------------------

                render_section_header(
                    "AI Recommendation",
                    "Machine-generated investigation findings and recommended action.",
                )

                ai_col_1, ai_col_2 = st.columns(
                    2,
                    gap="medium",
                )

                with ai_col_1:

                    render_ai_panel(
                        "Investigation Finding",
                        case.get(
                            "investigation_finding",
                            "",
                        ),
                    )

                    render_ai_panel(
                        "Likely Cause",
                        case.get(
                            "likely_cause",
                            "",
                        ),
                    )

                with ai_col_2:

                    render_ai_panel(
                        "Recommended Action",
                        case.get(
                            "recommended_action",
                            "",
                        ),
                    )

                    render_ai_panel(
                        "Risk Assessment",
                        case.get(
                            "risk_assessment",
                            "",
                        ),
                    )

                ai_decision = normalize_text(
                    case.get(
                        "decision",
                        "",
                    )
                )

                st.markdown(
                    f"""
                    <div class="card"
                         style="background:#F8FAFC;">

                        <div class="metric-label">
                            AI Decision
                        </div>

                        <div style="margin-top:7px;">
                            {render_badge(ai_decision or "NOT AVAILABLE")}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # --------------------------------------------
                # ANALYST DECISION
                # --------------------------------------------

                render_section_header(
                    "Analyst Decision",
                    "Human governance decision recorded against the AI investigation.",
                )

                current_review_status = normalize_text(
                    case.get(
                        "review_status",
                        "",
                    )
                ).upper()

                current_reviewer_decision = normalize_text(
                    case.get(
                        "reviewer_decision",
                        "",
                    )
                ).upper()

                if current_review_status == "COMPLETED":

                    st.info(
                        "This case already has a completed analyst review. "
                        "The recorded decision is shown below."
                    )

                    recorded_decision = (
                        current_reviewer_decision
                        or "NOT RECORDED"
                    )

                    st.markdown(
                        f"""
                        <div class="card">

                            <div class="metric-label">
                                Recorded Analyst Decision
                            </div>

                            <div style="margin-top:8px;">
                                {render_badge(recorded_decision)}
                            </div>

                            <div style="
                                margin-top:14px;
                                color:#667085;
                                font-size:11px;
                                line-height:1.6;
                            ">
                                {normalize_text(
                                    case.get(
                                        "reviewer_comment",
                                        "",
                                    )
                                ) or "No reviewer comment recorded."}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                else:

                    decision = st.selectbox(
                        "Decision",
                        options=[
                            "APPROVE",
                            "REJECT",
                            "ESCALATE",
                        ],
                        key=f"decision_{selected_review_case}",
                    )

                    reviewer_comment = st.text_area(
                        "Reviewer Comment",
                        placeholder=(
                            "Document the reason for your decision..."
                        ),
                        key=f"comment_{selected_review_case}",
                        height=120,
                    )

                    if st.button(
                        "Submit Review",
                        type="primary",
                        use_container_width=True,
                        key=f"submit_{selected_review_case}",
                    ):

                        try:

                            review_case(
                                case_id=selected_review_case,
                                decision=decision,
                                reviewer_comment=reviewer_comment,
                            )

                            st.cache_data.clear()

                            st.success(
                                f"{selected_review_case} review submitted successfully."
                            )

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to submit review: {error}"
                            )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )


# ============================================================
# EXCEPTION ANALYTICS
# ============================================================

with analytics_tab:

    st.markdown(
        """
        <div class="page-kicker">
            Analytics
        </div>

        <div class="page-title">
            Exception Analytics
        </div>

        <div class="page-description">
            Analyze exception patterns, financial exposure,
            risk distribution and governance workload.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # EXCEPTION DISTRIBUTION
    # --------------------------------------------------------

    render_section_header(
        "Exception Distribution",
        "Frequency of detected reconciliation exception types.",
    )

    exception_counts = (
        filtered_df[
            "exception_category"
        ]
        .value_counts()
    )

    if exception_counts.empty:

        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-title">
                    No exception data
                </div>
                <div class="empty-state-description">
                    No cases match the selected filters.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        exception_chart = pd.DataFrame(
            {
                "Exception": exception_counts.index,
                "Cases": exception_counts.values,
            }
        ).set_index("Exception")

        st.bar_chart(
            exception_chart,
            height=300,
        )

    # --------------------------------------------------------
    # RISK BY EXCEPTION
    # --------------------------------------------------------

    render_section_header(
        "Risk by Exception Type",
        "Risk composition across different anomaly categories.",
    )

    risk_exception_table = pd.crosstab(
        filtered_df[
            "exception_category"
        ],
        filtered_df[
            "risk_level"
        ].str.upper(),
    )

    risk_columns = [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]

    for column in risk_columns:

        if column not in risk_exception_table.columns:
            risk_exception_table[
                column
            ] = 0

    risk_exception_table = (
        risk_exception_table[
            risk_columns
        ]
        .sort_values(
            by=risk_columns,
            ascending=False,
        )
    )

    if risk_exception_table.empty:

        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-title">
                    No risk composition data
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.dataframe(
            risk_exception_table,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # ANALYTICS KPI
    # --------------------------------------------------------

    analytics_columns = st.columns(
        3,
        gap="medium",
    )

    human_review_rate = (
        filtered_df[
            "human_review_required"
        ].mean() * 100
        if len(filtered_df)
        else 0
    )

    exposure = filtered_df.get(
        "outstanding_amount",
        pd.Series(dtype=float),
    ).apply(safe_float).sum()

    coverage = filtered_df.get(
        "payment_coverage_pct",
        pd.Series(dtype=float),
    ).apply(safe_float).mean()

    if pd.isna(coverage):
        coverage = 0

    with analytics_columns[0]:

        render_kpi_card(
            "Human Review Rate",
            f"{human_review_rate:.2f}%",
            "Share of cases requiring analyst review",
            "review",
        )

    with analytics_columns[1]:

        render_kpi_card(
            "Outstanding Exposure",
            format_currency(exposure),
            "Unresolved financial balance",
            "money",
        )

    with analytics_columns[2]:

        render_kpi_card(
            "Average Coverage",
            format_percentage(coverage),
            "Average payment coverage",
            "accent",
        )

    # --------------------------------------------------------
    # CASES BY LIFECYCLE
    # --------------------------------------------------------

    render_section_header(
        "Cases by Lifecycle",
        "Governance state distribution across the investigation workflow.",
    )

    lifecycle_counts = (
        filtered_df[
            "case_status"
        ]
        .str.upper()
        .value_counts()
        .reindex(
            [
                "OPEN",
                "INVESTIGATING",
                "PENDING_REVIEW",
                "APPROVED",
                "REJECTED",
                "ESCALATED",
                "RESOLVED",
            ],
            fill_value=0,
        )
    )

    lifecycle_chart = pd.DataFrame(
        {
            "Lifecycle": lifecycle_counts.index,
            "Cases": lifecycle_counts.values,
        }
    ).set_index("Lifecycle")

    st.bar_chart(
        lifecycle_chart,
        height=300,
    )


# ============================================================
# CASE INVESTIGATION
# ============================================================

with investigation_tab:

    st.markdown(
        """
        <div class="page-kicker">
            Investigation Workspace
        </div>

        <div class="page-title">
            Case Investigation
        </div>

        <div class="page-description">
            Trace the transaction chain, inspect financial evidence,
            review AI reasoning, and verify governance decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    case_ids = [
        normalize_text(value)
        for value in filtered_df[
            "case_id"
        ].tolist()
        if normalize_text(value)
    ]

    if not case_ids:

        st.markdown(
            """
            <div class="empty-state">

                <div class="empty-state-title">
                    No cases match the selected filters
                </div>

                <div class="empty-state-description">
                    Adjust the filters in the control panel
                    to find an investigation case.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        selected_case_id = st.selectbox(
            "Select Case",
            options=case_ids,
            key="investigation_case_selector",
        )

        selected_case_rows = df[
            df["case_id"].astype(str)
            == str(selected_case_id)
        ]

        if selected_case_rows.empty:

            st.warning(
                "The selected case could not be loaded."
            )

        else:

            case = selected_case_rows.iloc[0]

            # ------------------------------------------------
            # CASE HEADER
            # ------------------------------------------------

            case_status = normalize_text(
                case.get(
                    "case_status",
                    "OPEN",
                )
            ).upper()

            risk_level = normalize_text(
                case.get(
                    "risk_level",
                    "",
                )
            ).upper()

            priority = safe_float(
                case.get(
                    "priority_score",
                    0,
                )
            )

            category = normalize_text(
                case.get(
                    "exception_category",
                    "",
                )
            )

            st.markdown(
                f"""
                <div class="case-header">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:flex-start;
                        gap:20px;
                    ">

                        <div>

                            <div class="case-id">
                                {selected_case_id}
                            </div>

                            <div class="case-category">
                                {category.replace("_", " ")}
                            </div>

                        </div>

                        <div style="
                            display:flex;
                            gap:8px;
                            align-items:center;
                        ">

                            {render_badge(case_status)}
                            {render_badge(risk_level)}

                        </div>

                    </div>

                    <div style="
                        display:grid;
                        grid-template-columns:
                            repeat(3, minmax(0, 1fr));
                        gap:20px;
                        margin-top:20px;
                        padding-top:16px;
                        border-top:1px solid #EAECF0;
                    ">

                        <div>
                            <div class="case-stat-label">
                                Priority Score
                            </div>

                            <div class="case-stat-value">
                                {priority:.1f}
                            </div>
                        </div>

                        <div>
                            <div class="case-stat-label">
                                Human Review
                            </div>

                            <div class="case-stat-value">
                                {
                                    "Required"
                                    if bool(
                                        case.get(
                                            "human_review_required",
                                            False,
                                        )
                                    )
                                    else "Not Required"
                                }
                            </div>
                        </div>

                        <div>
                            <div class="case-stat-label">
                                Final Status
                            </div>

                            <div class="case-stat-value">
                                {
                                    normalize_text(
                                        case.get(
                                            "final_status",
                                            "",
                                        )
                                    ).replace(
                                        "_",
                                        " ",
                                    )
                                    or "—"
                                }
                            </div>
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            # ------------------------------------------------
            # TRANSACTION CHAIN
            # ------------------------------------------------

            render_section_header(
                "Transaction Chain",
                "Trace the relationship between invoice, payment and bank transaction.",
            )

            invoice_id = normalize_text(
                case.get(
                    "invoice_id",
                    "",
                )
            )

            payment_id = normalize_text(
                case.get(
                    "payment_id",
                    "",
                )
            )

            bank_id = normalize_text(
                case.get(
                    "bank_transaction_id",
                    case.get(
                        "bank_id",
                        "",
                    ),
                )
            )

            invoice_amount = safe_float(
                case.get(
                    "invoice_amount",
                    0,
                )
            )

            payment_amount = safe_float(
                case.get(
                    "payment_amount",
                    0,
                )
            )

            bank_amount = safe_float(
                case.get(
                    "bank_amount",
                    0,
                )
            )

            invoice_missing = not invoice_id
            payment_missing = not payment_id
            bank_missing = not bank_id

            chain_columns = st.columns(
                5,
                gap="small",
            )

            # Invoice
            with chain_columns[0]:

                st.markdown(
                    f"""
                    <div class="chain-node
                        {'missing' if invoice_missing else ''}">

                        <div class="chain-node-icon">
                            INV
                        </div>

                        <div class="chain-node-title">
                            Invoice
                        </div>

                        <div class="chain-node-id">
                            {
                                invoice_id
                                if invoice_id
                                else "Missing"
                            }
                        </div>

                        <div class="chain-node-detail">
                            Amount:
                            {format_currency(invoice_amount)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Arrow
            with chain_columns[1]:

                st.markdown(
                    """
                    <div class="chain-arrow">
                        →
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Payment
            with chain_columns[2]:

                st.markdown(
                    f"""
                    <div class="chain-node
                        {'missing' if payment_missing else ''}">

                        <div class="chain-node-icon">
                            PAY
                        </div>

                        <div class="chain-node-title">
                            Payment
                        </div>

                        <div class="chain-node-id">
                            {
                                payment_id
                                if payment_id
                                else "Missing"
                            }
                        </div>

                        <div class="chain-node-detail">
                            Amount:
                            {format_currency(payment_amount)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Arrow
            with chain_columns[3]:

                st.markdown(
                    """
                    <div class="chain-arrow">
                        →
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Bank
            with chain_columns[4]:

                bank_title = (
                    "Bank Transaction"
                    if not bank_missing
                    else "Bank Transaction Missing"
                )

                st.markdown(
                    f"""
                    <div class="chain-node
                        {'missing' if bank_missing else ''}">

                        <div class="chain-node-icon">
                            BANK
                        </div>

                        <div class="chain-node-title">
                            {bank_title}
                        </div>

                        <div class="chain-node-id">
                            {
                                bank_id
                                if bank_id
                                else "Missing"
                            }
                        </div>

                        <div class="chain-node-detail">
                            Amount:
                            {format_currency(bank_amount)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ------------------------------------------------
            # FINANCIAL METRICS
            # ------------------------------------------------

            render_section_header(
                "Financial Metrics",
                "Financial position calculated from the transaction chain.",
            )

            outstanding = safe_float(
                case.get(
                    "outstanding_amount",
                    0,
                )
            )

            coverage = safe_float(
                case.get(
                    "payment_coverage_pct",
                    0,
                )
            )

            financial_columns = st.columns(
                5,
                gap="small",
            )

            financial_values = [
                (
                    "Invoice Amount",
                    format_currency(
                        invoice_amount
                    ),
                ),
                (
                    "Payment Amount",
                    format_currency(
                        payment_amount
                    ),
                ),
                (
                    "Bank Amount",
                    format_currency(
                        bank_amount
                    ),
                ),
                (
                    "Outstanding Amount",
                    format_currency(
                        outstanding
                    ),
                ),
                (
                    "Payment Coverage",
                    format_percentage(
                        coverage
                    ),
                ),
            ]

            for column, (
                label,
                value,
            ) in zip(
                financial_columns,
                financial_values,
            ):

                with column:
                    render_metric_card(
                        label,
                        value,
                    )

            # ------------------------------------------------
            # EVIDENCE
            # ------------------------------------------------

            render_section_header(
                "Evidence",
                "Underlying transaction evidence supporting the investigation.",
            )

            evidence_items = [
                (
                    "Invoice Evidence",
                    "invoice",
                    [
                        "invoice_id",
                        "invoice_number",
                        "invoice_amount",
                        "invoice_date",
                        "vendor",
                    ],
                ),
                (
                    "Payment Evidence",
                    "payment",
                    [
                        "payment_id",
                        "payment_amount",
                        "payment_date",
                        "payment_method",
                    ],
                ),
                (
                    "Bank Evidence",
                    "bank",
                    [
                        "bank_transaction_id",
                        "bank_id",
                        "bank_amount",
                        "bank_date",
                        "bank_reference",
                    ],
                ),
                (
                    "Exception Evidence",
                    "exception",
                    [
                        "exception_category",
                        "exception_description",
                        "exception_reason",
                    ],
                ),
            ]

            for title, prefix, fields in evidence_items:

                evidence_lines = []

                for field in fields:

                    if field in case.index:

                        value = normalize_text(
                            case.get(
                                field,
                                "",
                            )
                        )

                        if value:

                            pretty_name = (
                                field
                                .replace(
                                    "_",
                                    " ",
                                )
                                .title()
                            )

                            evidence_lines.append(
                                f"**{pretty_name}:** {value}"
                            )

                with st.expander(
                    title,
                    expanded=False,
                ):

                    if evidence_lines:

                        for line in evidence_lines:
                            st.markdown(line)

                    else:

                        st.caption(
                            "No evidence available for this section."
                        )

            # ------------------------------------------------
            # AI INVESTIGATION
            # ------------------------------------------------

            render_section_header(
                "AI Investigation",
                "Machine-generated investigation analysis.",
            )

            ai_columns = st.columns(
                2,
                gap="medium",
            )

            with ai_columns[0]:

                render_ai_panel(
                    "Investigation Finding",
                    case.get(
                        "investigation_finding",
                        "",
                    ),
                )

                render_ai_panel(
                    "Likely Cause",
                    case.get(
                        "likely_cause",
                        "",
                    ),
                )

            with ai_columns[1]:

                render_ai_panel(
                    "Recommended Action",
                    case.get(
                        "recommended_action",
                        "",
                    ),
                )

                render_ai_panel(
                    "Reasoning",
                    case.get(
                        "reasoning",
                        "",
                    ),
                )

            # ------------------------------------------------
            # RISK ASSESSMENT
            # ------------------------------------------------

            render_section_header(
                "Risk Assessment",
                "Risk classification and governance priority.",
            )

            risk_columns = st.columns(
                [1, 1.4],
                gap="large",
            )

            risk_score = safe_float(
                case.get(
                    "risk_score",
                    case.get(
                        "priority_score",
                        0,
                    ),
                )
            )

            with risk_columns[0]:

                st.markdown(
                    f"""
                    <div class="risk-panel">

                        <div class="metric-label">
                            Risk Score
                        </div>

                        <div class="risk-score">
                            {risk_score:.1f}
                        </div>

                        <div class="risk-score-label">
                            Risk classification:
                            {risk_level or "UNKNOWN"}
                        </div>

                        <div class="risk-bar">

                            <div
                                class="risk-bar-fill"
                                style="width:
                                {min(max(risk_score, 0), 100)}%;
                                "
                            ></div>

                        </div>

                        <div style="
                            margin-top:5px;
                        ">
                            {render_badge(risk_level)}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with risk_columns[1]:

                risk_metric_1, risk_metric_2 = st.columns(
                    2,
                    gap="small",
                )

                with risk_metric_1:

                    render_metric_card(
                        "Priority Score",
                        f"{priority:.1f}",
                    )

                with risk_metric_2:

                    review_required_flag = bool(
                        case.get(
                            "human_review_required",
                            False,
                        )
                    )

                    render_metric_card(
                        "Human Review",
                        (
                            "Required"
                            if review_required_flag
                            else "Not Required"
                        ),
                    )

                risk_assessment = normalize_text(
                    case.get(
                        "risk_assessment",
                        "",
                    )
                )

                if risk_assessment:

                    st.markdown(
                        f"""
                        <div class="risk-reason">
                            {risk_assessment}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # ------------------------------------------------
            # DECISION
            # ------------------------------------------------

            render_section_header(
                "Decision",
                "AI recommendation and analyst governance decision.",
            )

            decision_columns = st.columns(
                2,
                gap="medium",
            )

            ai_decision = normalize_text(
                case.get(
                    "decision",
                    "",
                )
            )

            analyst_decision = normalize_text(
                case.get(
                    "reviewer_decision",
                    "",
                )
            )

            with decision_columns[0]:

                st.markdown(
                    f"""
                    <div class="card">

                        <div class="metric-label">
                            AI Decision
                        </div>

                        <div style="margin-top:9px;">
                            {render_badge(
                                ai_decision
                                or "NOT AVAILABLE"
                            )}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with decision_columns[1]:

                st.markdown(
                    f"""
                    <div class="card">

                        <div class="metric-label">
                            Analyst Decision
                        </div>

                        <div style="margin-top:9px;">
                            {render_badge(
                                analyst_decision
                                or "NOT REVIEWED"
                            )}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ------------------------------------------------
            # REVIEW RECORD
            # ------------------------------------------------

            if analyst_decision:

                render_section_header(
                    "Governance Record",
                    "Recorded human review information.",
                )

                governance_columns = st.columns(
                    3,
                    gap="small",
                )

                governance_data = [
                    (
                        "Review Status",
                        normalize_text(
                            case.get(
                                "review_status",
                                "",
                            )
                        ) or "—",
                    ),
                    (
                        "Final Status",
                        normalize_text(
                            case.get(
                                "final_status",
                                "",
                            )
                        ) or "—",
                    ),
                    (
                        "Reviewed At",
                        normalize_text(
                            case.get(
                                "reviewed_at",
                                "",
                            )
                        ) or "—",
                    ),
                ]

                for column, (
                    label,
                    value,
                ) in zip(
                    governance_columns,
                    governance_data,
                ):

                    with column:

                        render_metric_card(
                            label,
                            value.replace(
                                "_",
                                " ",
                            ),
                        )

                reviewer_comment = normalize_text(
                    case.get(
                        "reviewer_comment",
                        "",
                    )
                )

                if reviewer_comment:

                    st.markdown(
                        f"""
                        <div class="card">

                            <div class="metric-label">
                                Reviewer Comment
                            </div>

                            <div style="
                                color:#475467;
                                font-size:12px;
                                line-height:1.6;
                                margin-top:7px;
                            ">
                                {reviewer_comment}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <strong>TANGLE</strong>
        &nbsp;•&nbsp;
        Transaction Anomaly & Governance Ledger Engine
        <br>
        AI-assisted financial reconciliation, risk analysis
        and human governance.
    </div>
    """,
    unsafe_allow_html=True,
)
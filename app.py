from __future__ import annotations

import os
import textwrap
import time
from datetime import date, datetime, timedelta
from html import escape
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage

from prompts import USER_PROMPT_FOR_MAIN_AGENT, WEDDING_PLANNER_AGENT_PROMPT


# ============================================================
# Configuration
# ============================================================

APP_TITLE = "Multi-Agent Wedding Planner"
MODEL_NAME = "openai/gpt-oss-120b"
REQUIRED_KEYS = ("GROQ_API_KEY", "TAVILY_API_KEY")

STYLE_OPTIONS = [
    "Modern",
    "Romantic",
    "Classic",
    "Garden",
    "Minimal",
    "Luxury",
    "Cultural fusion",
    "Destination",
    "Eco-conscious",
    "Black tie",
]

PRIORITY_OPTIONS = [
    "Venue shortlist",
    "Vendor research",
    "Budget allocation",
    "Guest experience",
    "Timeline",
    "Design direction",
    "Risk management",
    "Travel logistics",
]


load_dotenv()

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Styling
# ============================================================

def inject_css() -> None:
    st.html(
        """
        <style>
        :root {
            --ink: #292c27;
            --ink-soft: #465047;
            --muted: #777a71;
            --line: #e6e1d7;
            --line-strong: #d5d0c5;
            --panel: #ffffff;
            --surface: #f7f5ef;
            --sidebar: #f0ede5;
            --sidebar-field: #ffffff;
            --teal: #3f5e4d;
            --coral: #a65c55;
            --gold: #9b8058;
            --success: #22735f;
            --danger: #b94e49;
            --shadow: 0 5px 18px rgba(41, 44, 39, 0.035);
        }

        [data-testid="stAppViewContainer"] {
            background: var(--surface);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        .app-header {
            align-items: center;
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--teal);
            border-radius: 3px 12px 12px 3px;
            box-shadow: none;
            display: grid;
            gap: 2rem;
            grid-template-columns: minmax(0, 1fr) auto;
            padding: 2rem 2.1rem;
            margin-bottom: 1.65rem;
        }

        .app-kicker {
            color: var(--gold);
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.13em;
            margin-bottom: 0.3rem;
        }

        .app-title {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2rem, 3.2vw, 3rem);
            font-weight: 500;
            line-height: 1.08;
            margin: 0 0 0.45rem;
            letter-spacing: -0.025em;
        }

        .app-subtitle {
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.5;
            max-width: 700px;
            margin: 0;
        }

        .header-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem 0.75rem;
            justify-content: flex-end;
            max-width: 310px;
        }

        .header-chip,
        .soft-chip,
        .badge {
            border-radius: 999px;
            font-weight: 700;
        }

        .header-chip {
            background: transparent;
            border: 0;
            color: var(--muted);
            font-size: 0.68rem;
            letter-spacing: 0.035em;
            padding: 0.15rem 0;
            white-space: nowrap;
        }

        .header-chip + .header-chip {
            border-left: 1px solid var(--line-strong);
            padding-left: 0.75rem;
        }

        .summary-grid {
            display: grid;
            gap: 0.75rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin: 0 0 1.05rem;
        }

        .summary-card,
        .side-panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 10px;
            box-shadow: none;
        }

        .summary-card {
            min-height: 6.25rem;
            padding: 0.95rem 1rem;
        }

        .summary-card .label,
        .lens-item span {
            color: var(--muted);
            display: block;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }

        .summary-card .value {
            color: var(--ink);
            display: block;
            font-size: 1.18rem;
            font-weight: 650;
            line-height: 1.15;
            margin-bottom: 0.2rem;
        }

        .summary-card .note {
            color: var(--muted);
            display: block;
            font-size: 0.83rem;
            line-height: 1.3;
        }

        .section-label {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-weight: 500;
            font-size: 1.35rem;
            margin: 0 0 0.6rem;
        }

        .field-group-title {
            color: var(--gold);
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            margin: 0.35rem 0 0.7rem;
            text-transform: uppercase;
        }

        [data-testid="stForm"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1.3rem 1.4rem 1.4rem;
        }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stForm"] label {
            color: var(--ink) !important;
            font-weight: 650;
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea {
            background: #ffffff !important;
            border: 1px solid var(--line-strong) !important;
            border-radius: 10px !important;
            color: var(--ink) !important;
        }

        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div {
            background: #ffffff !important;
            border-color: var(--line-strong) !important;
            border-radius: 8px !important;
            color: var(--ink) !important;
            min-height: 2.65rem;
        }

        .stSelectbox [data-baseweb="select"] svg,
        .stMultiSelect [data-baseweb="select"] svg {
            color: var(--ink) !important;
            fill: var(--ink) !important;
        }

        .stMultiSelect [data-baseweb="tag"] {
            background: #edf1eb !important;
            border: 1px solid #dce5da !important;
            border-radius: 6px !important;
        }

        .stMultiSelect [data-baseweb="tag"] span {
            color: var(--ink) !important;
            font-weight: 700 !important;
        }

        [data-testid="stSidebar"] {
            background: var(--sidebar);
            border-right: 1px solid #e5e0d5;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: var(--ink) !important;
        }

        [data-testid="stSidebar"] .stTextInput input {
            background: var(--sidebar-field) !important;
            border-color: var(--line-strong) !important;
            color: var(--ink) !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: #ddd8cc;
        }

        .side-panel {
            padding: 1.1rem 1.15rem;
            margin-bottom: 0.9rem;
        }

        .side-panel h3 {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-weight: 500;
            font-size: 1rem;
            margin: 0 0 0.75rem;
        }

        .side-panel p {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.45;
            margin: 0 0 0.75rem;
        }

        .lens-grid {
            display: grid;
            gap: 0.45rem 0.8rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin-bottom: 0.75rem;
        }

        .lens-item {
            background: transparent;
            border-bottom: 1px solid var(--line);
            border-radius: 0;
            padding: 0.55rem 0.1rem;
        }

        .lens-item strong {
            color: var(--ink);
            display: block;
            font-size: 0.96rem;
            line-height: 1.25;
        }

        .chip-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        .soft-chip {
            background: transparent;
            border: 1px solid #ddd8cc;
            color: #625b4e;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.18rem 0.5rem;
        }

        .flow-row {
            border-top: 1px solid var(--line);
            padding: 0.68rem 0;
        }

        .flow-row:first-of-type {
            border-top: 0;
            padding-top: 0;
        }

        .flow-row strong {
            color: var(--ink);
            display: block;
            font-size: 0.92rem;
            margin-bottom: 0.15rem;
        }

        .flow-row span {
            color: var(--muted);
            display: block;
            font-size: 0.84rem;
            line-height: 1.35;
        }

        .key-row {
            align-items: center;
            border-bottom: 1px solid #ddd9cd;
            display: flex;
            justify-content: space-between;
            padding: 0.45rem 0;
        }

        .key-row span:first-child {
            color: var(--muted) !important;
            font-size: 0.9rem;
        }

        .badge {
            font-size: 0.76rem;
            padding: 0.14rem 0.55rem;
        }

        .badge-ready {
            background: #e6f2eb;
            color: #28634d !important;
        }

        .badge-missing {
            background: #f8e9e6;
            color: #9f4c43 !important;
        }

        [data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0.85rem 0.95rem;
        }

        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"] {
            color: var(--ink) !important;
        }

        .result-title-row {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: space-between;
            margin: 0.3rem 0 0.75rem;
        }

        .result-title-row h3 {
            color: var(--ink);
            font-size: 1.05rem;
            margin: 0;
        }

        .result-title-row span {
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 650;
        }

        .empty-result {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 10px;
            color: var(--muted);
            padding: 1.4rem;
            text-align: center;
        }

        .empty-result strong {
            color: var(--ink);
            display: block;
            font-size: 1rem;
            margin-bottom: 0.3rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
            min-height: 2.8rem;
            font-weight: 700;
        }

        [data-testid="stFormSubmitButton"] button {
            background: var(--teal) !important;
            border-color: var(--teal) !important;
            color: #ffffff !important;
        }

        [data-testid="stFormSubmitButton"] button:disabled {
            background: #d8ddd8 !important;
            border-color: #d8ddd8 !important;
            color: #64716a !important;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.7);
            border-color: #d7d3c7;
            color: var(--ink);
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 0.8rem;
            }

            .app-header {
                grid-template-columns: 1fr;
                gap: 1rem;
                padding: 1.5rem;
            }

            .header-chips {
                justify-content: flex-start;
                max-width: none;
            }

            .summary-grid,
            .lens-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """
    )


# ============================================================
# State and configuration helpers
# ============================================================

def get_default_form_values() -> dict[str, Any]:
    return {
        "couple_name": "Amira and Noah",
        "wedding_location": "Pune, Maharashtra",
        "wedding_date": date.today() + timedelta(days=240),
        "guest_count": 120,
        "currency": "INR",
        "budget_range": (800000, 1500000),
        "ceremony_type": "Ceremony and reception",
        "wedding_styles": ["Modern", "Romantic", "Cultural fusion"],
        "planning_priorities": [
            "Venue shortlist",
            "Vendor research",
            "Budget allocation",
            "Timeline",
        ],
        "tone": "Elegant and practical",
        "must_haves": (
            "Good vegetarian menu, reliable photography, smooth guest "
            "transportation, and enough space for family ceremonies."
        ),
        "constraints": (
            "Keep the venue reasonably close to the city. Avoid unnecessary "
            "decorative spending and prioritize guest experience."
        ),
        "traditions": (
            "Blend modern wedding planning with family and cultural traditions. "
            "Include space for speeches and family rituals."
        ),
    }


def initialize_state() -> None:
    st.session_state.setdefault("plans", [])

    for key, value in get_default_form_values().items():
        st.session_state.setdefault(key, value)


def load_sample_values() -> None:
    for key, value in get_default_form_values().items():
        st.session_state[key] = value


def key_is_ready(name: str) -> bool:
    return bool(os.getenv(name))


def apply_key_overrides(groq_key: str, tavily_key: str) -> None:
    if groq_key.strip():
        os.environ["GROQ_API_KEY"] = groq_key.strip()

    if tavily_key.strip():
        os.environ["TAVILY_API_KEY"] = tavily_key.strip()


def format_budget_range(
    budget_range: tuple[int, int],
    currency: str,
) -> str:
    low, high = budget_range
    return f"{currency} {low:,.0f} - {high:,.0f}"


def format_budget_per_guest(
    budget_range: tuple[int, int],
    guest_count: int,
    currency: str,
) -> str:
    if guest_count <= 0:
        return "Not set"

    low, high = budget_range
    average_budget = (low + high) / 2
    return f"{currency} {average_budget / guest_count:,.0f} per guest"


def format_days_until(target_date: date) -> str:
    days = (target_date - date.today()).days

    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    if days < 0:
        return f"{abs(days)} days ago"

    return f"{days} days out"


def format_list_preview(
    items: list[str],
    fallback: str = "Flexible",
) -> str:
    if not items:
        return fallback

    preview = items[:2]
    suffix = (
        f" +{len(items) - len(preview)}"
        if len(items) > len(preview)
        else ""
    )

    return f"{', '.join(preview)}{suffix}"


def render_key_badge(label: str, ready: bool) -> None:
    status_class = "badge-ready" if ready else "badge-missing"
    status_text = "Ready" if ready else "Missing"

    st.html(
        f"""
        <div class="key-row">
            <span>{escape(label)}</span>
            <span class="badge {status_class}">{status_text}</span>
        </div>
        """
    )


# ============================================================
# Agent loading
# ============================================================

@st.cache_resource(show_spinner=False)
def load_agent_dependencies():
    """
    Load the shared Groq model and the two delegation tools.

    Important:
    models.py must expose:
        model = ChatGroq(...)

    agents.py must expose:
        delegate_to_subagent1
        delegate_to_subagent2
    """
    from agents import delegate_to_subagent1, delegate_to_subagent2
    from models import model

    return model, [delegate_to_subagent1, delegate_to_subagent2]


# ============================================================
# UI sections
# ============================================================

def render_header() -> None:
    st.html(
        """
        <div class="app-header">
            <div>
                <div class="app-kicker">LangChain portfolio project</div>
                <h1 class="app-title">Multi-Agent Wedding Planner</h1>
                <p class="app-subtitle">
                    Build a client-ready planning brief from preferences,
                    constraints, live research, and agent-synthesized
                    recommendations.
                </p>
            </div>

            <div class="header-chips">
                <span class="header-chip">3-agent flow</span>
                <span class="header-chip">Tavily research</span>
                <span class="header-chip">Groq LLM</span>
                <span class="header-chip">Markdown export</span>
            </div>
        </div>
        """
    )


def render_sidebar() -> bool:
    with st.sidebar:
        st.markdown("### Runtime")

        st.caption("API keys are read from your .env file.")
        st.caption("You can optionally override them below.")

        groq_override = st.text_input(
            "Groq API key",
            type="password",
            key="groq_key_override",
        )

        tavily_override = st.text_input(
            "Tavily API key",
            type="password",
            key="tavily_key_override",
        )

        apply_key_overrides(groq_override, tavily_override)

        groq_ready = key_is_ready("GROQ_API_KEY")
        tavily_ready = key_is_ready("TAVILY_API_KEY")

        render_key_badge("Groq", groq_ready)
        render_key_badge("Tavily", tavily_ready)

        st.divider()

        st.markdown("### Demo Controls")

        st.button(
            "Load sample brief",
            use_container_width=True,
            on_click=load_sample_values,
        )

        if st.button(
            "Refresh agent clients",
            use_container_width=True,
        ):
            load_agent_dependencies.clear()
            st.toast("Agent clients refreshed.")

        st.divider()

        st.markdown("### Saved Runs")

        if st.session_state.plans:
            for plan in st.session_state.plans[:4]:
                st.caption(
                    f"{plan['title']} | {plan['created_at']}"
                )
        else:
            st.caption("No runs yet.")

        st.divider()

        st.markdown("### Backend")
        st.caption(f"Model: `{MODEL_NAME}`")
        st.caption("LLM provider: Groq")
        st.caption("Web research: Tavily")

    return groq_ready and tavily_ready


def get_form_payload() -> dict[str, Any]:
    keys = [
        "couple_name",
        "wedding_location",
        "wedding_date",
        "guest_count",
        "currency",
        "budget_range",
        "ceremony_type",
        "wedding_styles",
        "planning_priorities",
        "tone",
        "must_haves",
        "constraints",
        "traditions",
    ]

    return {
        key: st.session_state[key]
        for key in keys
    }


def render_dashboard_summary(runtime_ready: bool) -> None:
    payload = get_form_payload()

    status_value = "Ready" if runtime_ready else "Keys needed"
    status_note = (
        "Groq + Tavily are ready"
        if runtime_ready
        else "Add Groq and Tavily API keys"
    )

    guest_note = f"{payload['guest_count']:,} guests"

    st.html(
        f"""
        <div class="summary-grid">
            <div class="summary-card">
                <span class="label">Runtime</span>
                <span class="value">{status_value}</span>
                <span class="note">{status_note}</span>
            </div>

            <div class="summary-card">
                <span class="label">Event Date</span>
                <span class="value">
                    {format_days_until(payload["wedding_date"])}
                </span>
                <span class="note">
                    {payload["wedding_date"].strftime("%b %d, %Y")}
                </span>
            </div>

            <div class="summary-card">
                <span class="label">Budget</span>
                <span class="value">
                    {escape(
                        format_budget_range(
                            payload["budget_range"],
                            payload["currency"],
                        )
                    )}
                </span>
                <span class="note">
                    {escape(
                        format_budget_per_guest(
                            payload["budget_range"],
                            payload["guest_count"],
                            payload["currency"],
                        )
                    )}
                </span>
            </div>

            <div class="summary-card">
                <span class="label">Planning Focus</span>
                <span class="value">
                    {escape(
                        format_list_preview(
                            payload["planning_priorities"],
                            "Balanced",
                        )
                    )}
                </span>
                <span class="note">{guest_note}</span>
            </div>
        </div>
        """
    )


def render_brief_form(runtime_ready: bool) -> bool:
    st.html(
        '<div class="section-label">Wedding Brief</div>',
    )

    with st.form("wedding_brief_form"):
        st.html(
            '<div class="field-group-title">Basics</div>',
        )

        st.text_input(
            "Couple or project name",
            key="couple_name",
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.text_input(
                "Location",
                key="wedding_location",
            )

            st.number_input(
                "Guest count",
                min_value=10,
                max_value=1000,
                step=10,
                key="guest_count",
            )

        with col_b:
            st.date_input(
                "Target date",
                min_value=date.today(),
                key="wedding_date",
            )

            st.selectbox(
                "Event scope",
                [
                    "Ceremony and reception",
                    "Reception only",
                    "Destination wedding",
                    "Multi-day wedding",
                    "Elopement plus celebration",
                ],
                key="ceremony_type",
            )

        st.html(
            '<div class="field-group-title">Budget and Direction</div>',
        )

        budget_col, tone_col = st.columns([1.1, 1])

        with budget_col:
            st.selectbox(
                "Currency",
                ["INR", "USD", "EUR", "GBP", "CAD", "AUD"],
                key="currency",
            )

            st.slider(
                "Budget range",
                min_value=50000,
                max_value=25000000,
                step=50000,
                key="budget_range",
            )

        with tone_col:
            st.selectbox(
                "Planner tone",
                [
                    "Elegant and practical",
                    "Luxury editorial",
                    "Budget-conscious",
                    "Warm and family-centered",
                ],
                key="tone",
            )

            st.multiselect(
                "Style direction",
                STYLE_OPTIONS,
                key="wedding_styles",
            )

        st.html(
            '<div class="field-group-title">Priorities and Guardrails</div>',
        )

        st.multiselect(
            "Planning priorities",
            PRIORITY_OPTIONS,
            key="planning_priorities",
        )

        notes_a, notes_b = st.columns(2)

        with notes_a:
            st.text_area(
                "Must-haves",
                height=124,
                key="must_haves",
            )

            st.text_area(
                "Traditions and family details",
                height=104,
                key="traditions",
            )

        with notes_b:
            st.text_area(
                "Constraints",
                height=244,
                key="constraints",
            )

        return st.form_submit_button(
            "Generate wedding plan",
            type="primary",
            use_container_width=True,
            disabled=not runtime_ready,
        )


# ============================================================
# Planner logic
# ============================================================

def build_requirements(payload: dict[str, Any]) -> str:
    budget_low, budget_high = payload["budget_range"]

    styles = (
        ", ".join(payload["wedding_styles"])
        or "Flexible"
    )

    priorities = (
        ", ".join(payload["planning_priorities"])
        or "Balanced planning support"
    )

    return textwrap.dedent(
        f"""
        Couple or event name: {payload["couple_name"]}
        Wedding location: {payload["wedding_location"]}
        Target date: {payload["wedding_date"].strftime("%B %d, %Y")}
        Guest count: {payload["guest_count"]}
        Budget range: {payload["currency"]} {budget_low:,} to {budget_high:,}
        Event scope: {payload["ceremony_type"]}
        Preferred style: {styles}
        Planning priorities: {priorities}
        Planner tone: {payload["tone"]}

        Must-haves:
        {payload["must_haves"].strip() or "None specified."}

        Constraints and sensitivities:
        {payload["constraints"].strip() or "None specified."}

        Cultural, family, or ceremonial details:
        {payload["traditions"].strip() or "None specified."}

        Requested final plan:
        - Executive summary with the planning concept.
        - Venue and vendor research recommendations with clear rationale.
        - Budget allocation by category.
        - Timeline from now through wedding day.
        - Risks, tradeoffs, and open questions for the couple.
        """
    ).strip()


def invoke_planner(requirements: str) -> tuple[str, float]:
    """
    Run the main LangChain agent using the shared Groq model.

    Main agent
        -> delegate_to_subagent1
        -> delegate_to_subagent2
        -> Tavily research
        -> final synthesis
    """
    started = time.perf_counter()

    model, delegation_tools = load_agent_dependencies()

    system_prompt = WEDDING_PLANNER_AGENT_PROMPT.format(
        requirements=requirements
    )

    main_agent = create_agent(
        model=model,
        tools=delegation_tools,
        name="MainWeddingPlannerAgent",
        system_prompt=system_prompt,
    )

    response = main_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=USER_PROMPT_FOR_MAIN_AGENT
                )
            ]
        }
    )

    messages = response.get("messages", [])

    if not messages:
        raise RuntimeError(
            "The planner returned no messages."
        )

    content = messages[-1].content

    if not isinstance(content, str):
        content = str(content)

    duration = time.perf_counter() - started

    return content, duration


def create_download_name(title: str) -> str:
    slug = "".join(
        char.lower() if char.isalnum() else "-"
        for char in title
    )

    slug = "-".join(
        part
        for part in slug.split("-")
        if part
    )

    return f"{slug[:44] or 'wedding-plan'}.md"


def save_plan(
    title: str,
    requirements: str,
    content: str,
    duration: float,
) -> None:
    st.session_state.plans.insert(
        0,
        {
            "title": title,
            "requirements": requirements,
            "content": content,
            "duration": duration,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
        },
    )


def handle_submission() -> None:
    payload = get_form_payload()

    requirements = build_requirements(payload)

    title = (
        payload["couple_name"].strip()
        or "Wedding plan"
    )

    with st.status(
        "Running planner agents",
        expanded=True,
    ) as status:
        st.write("Preparing the main planner prompt.")
        st.write("Loading Groq model and delegation tools.")

        try:
            st.write(
                "Delegating research and synthesizing the plan."
            )

            content, duration = invoke_planner(
                requirements
            )

        except Exception as exc:
            status.update(
                label="Planner run failed",
                state="error",
            )

            st.error(
                "The planner could not complete the run."
            )

            with st.expander(
                "Technical details",
                expanded=True,
            ):
                st.code(
                    f"{type(exc).__name__}: {exc}"
                )

            return

        save_plan(
            title=title,
            requirements=requirements,
            content=content,
            duration=duration,
        )

        status.update(
            label="Plan ready",
            state="complete",
        )


# ============================================================
# Right-side panels
# ============================================================

def render_planning_lens() -> None:
    payload = get_form_payload()

    style_chips = "".join(
        f'<span class="soft-chip">{escape(style)}</span>'
        for style in payload["wedding_styles"]
    ) or '<span class="soft-chip">Flexible style</span>'

    priority_chips = "".join(
        f'<span class="soft-chip">{escape(priority)}</span>'
        for priority in payload["planning_priorities"]
    ) or '<span class="soft-chip">Balanced plan</span>'

    st.html(
        f"""
        <div class="side-panel">
            <h3>Planning Lens</h3>

            <div class="lens-grid">
                <div class="lens-item">
                    <span>Couple</span>
                    <strong>
                        {escape(
                            payload["couple_name"] or "Untitled"
                        )}
                    </strong>
                </div>

                <div class="lens-item">
                    <span>Location</span>
                    <strong>
                        {escape(
                            payload["wedding_location"] or "Not set"
                        )}
                    </strong>
                </div>

                <div class="lens-item">
                    <span>Scope</span>
                    <strong>
                        {escape(payload["ceremony_type"])}
                    </strong>
                </div>

                <div class="lens-item">
                    <span>Pace</span>
                    <strong>
                        {format_days_until(
                            payload["wedding_date"]
                        )}
                    </strong>
                </div>
            </div>

            <p>Style direction</p>
            <div class="chip-list">
                {style_chips}
            </div>

            <p style="margin-top:0.8rem;">
                Planning priorities
            </p>

            <div class="chip-list">
                {priority_chips}
            </div>
        </div>
        """
    )


def render_project_snapshot() -> None:
    st.html(
        f"""
        <div class="side-panel">
            <h3>Agent Flow</h3>

            <div class="flow-row">
                <strong>MainWeddingPlannerAgent</strong>
                <span>
                    Builds the final strategy from the structured
                    wedding brief.
                </span>
            </div>

            <div class="flow-row">
                <strong>SubAgent1 and SubAgent2</strong>
                <span>
                    Split research tasks for venues, vendors,
                    logistics, and market context.
                </span>
            </div>

            <div class="flow-row">
                <strong>Tavily Search Tool</strong>
                <span>
                    Retrieves current planning data before synthesis.
                </span>
            </div>

            <div class="flow-row">
                <strong>{escape(MODEL_NAME)}</strong>
                <span>
                    Groq-hosted LLM coordinating reasoning and
                    recommendations.
                </span>
            </div>
        </div>
        """
    )


def render_results() -> None:
    if not st.session_state.plans:
        st.html(
            """
            <div class="empty-result">
                <strong>No plan generated yet</strong>
                Complete the brief and run the planner to create
                a client-ready wedding plan.
            </div>
            """
        )
        return

    latest = st.session_state.plans[0]

    st.html(
        f"""
        <div class="result-title-row">
            <h3>{escape(latest["title"])}</h3>
            <span>
                Created {escape(latest["created_at"])}
            </span>
        </div>
        """
    )

    metric_a, metric_b, metric_c = st.columns(3)

    metric_a.metric(
        "Runtime",
        f"{latest['duration']:.1f}s",
    )

    metric_b.metric(
        "Brief Words",
        f"{len(latest['requirements'].split()):,}",
    )

    metric_c.metric(
        "Saved Runs",
        str(len(st.session_state.plans)),
    )

    plan_tab, requirements_tab, architecture_tab = st.tabs(
        ["Plan", "Input Brief", "Architecture"]
    )

    with plan_tab:
        with st.container(border=True):
            st.markdown(latest["content"])

        st.download_button(
            "Download plan",
            data=latest["content"],
            file_name=create_download_name(
                latest["title"]
            ),
            mime="text/markdown",
            use_container_width=True,
        )

    with requirements_tab:
        st.code(
            latest["requirements"],
            language="markdown",
        )

    with architecture_tab:
        st.markdown(
            """
            ```text
            Streamlit UI
                |
                v
            Structured wedding requirements
                |
                v
            WEDDING_PLANNER_AGENT_PROMPT
                |
                v
            MainWeddingPlannerAgent
                |
                +--> delegate_to_subagent1
                |       |
                |       +--> SubAgent1
                |              |
                |              +--> web_search
                |                     |
                |                     +--> Tavily
                |
                +--> delegate_to_subagent2
                        |
                        +--> SubAgent2
                               |
                               +--> web_search
                                      |
                                      +--> Tavily
                |
                v
            Final wedding plan
            ```"""
        )


# ============================================================
# Main application
# ============================================================

def main() -> None:
    inject_css()
    initialize_state()

    render_header()

    runtime_ready = render_sidebar()

    if not runtime_ready:
        st.warning(
            "Add GROQ_API_KEY and TAVILY_API_KEY to your .env "
            "file or enter them in the sidebar."
        )

    render_dashboard_summary(
        runtime_ready=runtime_ready
    )

    left_col, right_col = st.columns(
        [1.35, 0.8],
        gap="large",
    )

    with left_col:
        submitted = render_brief_form(
            runtime_ready=runtime_ready
        )

    with right_col:
        render_planning_lens()
        render_project_snapshot()

    if submitted:
        handle_submission()

    st.html(
        '<div class="section-label">Latest Output</div>',
    )

    render_results()


if __name__ == "__main__":
    main()

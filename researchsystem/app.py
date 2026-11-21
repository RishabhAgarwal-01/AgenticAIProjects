import streamlit as st
import datetime
from langchain_core.globals import set_llm_cache
from src.pipelines.pipeline import run_research_pipeline 
from langchain_core.caches import InMemoryCache

# Replaces SQLiteCache
set_llm_cache(InMemoryCache())

st.set_page_config(page_title="Multi-Agent Research", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #edf3ff; }
.stApp {
    background: #07111f;
    background-image: radial-gradient(circle at top left, rgba(0,191,255,0.14), transparent 32%),
                      radial-gradient(circle at bottom right, rgba(124,58,237,0.12), transparent 30%),
                      linear-gradient(180deg, #07111f 0%, #0a1729 100%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero { text-align: center; padding: 3.5rem 0 2.5rem; position: relative; }
.hero-eyebrow { font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500; letter-spacing: 0.25em; text-transform: uppercase; color: #38bdf8; margin-bottom: 1rem; opacity: 0.9; }
.hero h1 { font-family: 'Syne', sans-serif; font-size: clamp(2.8rem, 6vw, 5rem); font-weight: 800; line-height: 1.0; letter-spacing: -0.03em; margin: 0 0 1rem; }
.hero h1 span { background: linear-gradient(135deg, #38bdf8, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { font-size: 1.05rem; font-weight: 300; color: #b5c3d9; max-width: 520px; margin: 0 auto; line-height: 1.65; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(56,189,248,0.35), transparent); margin: 2rem 0; }

/* ── Input card ── */
.input-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(56,189,248,0.18); border-radius: 22px; padding: 2rem 2.5rem; margin-bottom: 2rem; backdrop-filter: blur(14px); box-shadow: 0 10px 40px rgba(0,0,0,0.28); }
.stTextInput > div > div > input { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(56,189,248,0.25) !important; border-radius: 12px !important; color: #f8fbff !important; padding: 0.8rem 1rem !important; }
.stTextInput > div > div > input:focus { border-color: #38bdf8 !important; box-shadow: 0 0 0 4px rgba(56,189,248,0.14) !important; }

/* ── Buttons ── */
button[kind="primary"] { background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 100%) !important; color: white !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; border: none !important; border-radius: 12px !important; padding: 0.8rem 2.2rem !important; transition: all 0.18s ease !important; width: 100%; box-shadow: 0 8px 30px rgba(56,189,248,0.22) !important; }
button[kind="primary"]:hover { transform: translateY(-2px) scale(1.01) !important; box-shadow: 0 12px 35px rgba(56,189,248,0.32) !important; }
button[kind="secondary"] { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 8px !important; color: #d8e2f0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.75rem !important; padding: 0.35rem 0.5rem !important; transition: all 0.2s ease !important; }
button[kind="secondary"]:hover { background: rgba(255,255,255,0.1) !important; border-color: rgba(56,189,248,0.4) !important; color: #38bdf8 !important; }

/* ── Terminal Console ── */
.terminal-console { background: #0d1627; border: 1px solid rgba(56,189,248,0.2); border-radius: 12px; padding: 1.2rem; font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #a5b4cb; height: 300px; overflow-y: auto; margin-top: 1.5rem; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5); }
.terminal-line { margin-bottom: 0.4rem; line-height: 1.4; }
.term-time { color: #64748b; margin-right: 0.5rem; font-size: 0.7rem; }
.term-step { color: #8b5cf6; font-weight: 600; margin-right: 0.5rem; text-transform: uppercase; }
.term-msg { color: #e2e8f0; }

/* ── Step Cards & Panels ── */
.step-card { background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; position: relative; backdrop-filter: blur(10px); }
.step-card.active { border-color: rgba(56,189,248,0.45); background: rgba(56,189,248,0.06); }
.step-card.done { border-color: rgba(34,197,94,0.28); background: rgba(34,197,94,0.05); }
.step-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 18px 0 0 18px; background: rgba(255,255,255,0.06); }
.step-card.active::before { background: #38bdf8; }
.step-card.done::before { background: #22c55e; }
.step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.3rem; }
.step-num { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #38bdf8; }
.step-title { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; }
.step-status { margin-left: auto; font-family: 'DM Mono', monospace; font-size: 0.68rem; }
.status-waiting { color: #64748b; } .status-running { color: #38bdf8; } .status-done { color: #22c55e; }
.result-panel, .report-panel, .feedback-panel { background: rgba(255,255,255,0.03); border-radius: 18px; padding: 1.8rem 2rem; margin-bottom: 1.5rem; backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
.report-panel { border-color: rgba(56,189,248,0.2); } .feedback-panel { border-color: rgba(34,197,94,0.2); }
.panel-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 1.2rem; padding-bottom: 0.7rem; }
.panel-label.orange { color: #38bdf8; border-bottom: 1px solid rgba(56,189,248,0.15); }
.panel-label.green { color: #22c55e; border-bottom: 1px solid rgba(34,197,94,0.15); }
.section-heading { font-family: 'Syne', sans-serif; font-size: 1.35rem; font-weight: 700; margin: 2rem 0 1rem; }
details { background: rgba(255,255,255,0.02); border-radius: 14px; padding: 0.3rem 0.8rem; border: 1px solid rgba(255,255,255,0.06); }
details summary { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #b5c3d9; cursor: pointer; }
.stSpinner > div > div { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

def step_card(num, title, state, desc=""):
    labels = {"waiting": ("WAITING", "status-waiting"), "running": ("● RUNNING", "status-running"), "done": ("✓ DONE", "status-done")}
    label, cls = labels.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#94a3b8;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)

# ── Session state init ──
if "results" not in st.session_state: st.session_state.results = {}
if "running" not in st.session_state: st.session_state.running = False
if "done" not in st.session_state: st.session_state.done = False

# ── Hero ──
st.markdown('<div class="hero"><div class="hero-eyebrow">Multi-Agent AI System</div><h1>Researcher<span>Agent</span></h1></div><div class="divider"></div>', unsafe_allow_html=True)

col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input("Research Topic", key="topic_input", label_visibility="visible")
    run_btn = st.button("⚡ Run Research Pipeline", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Clickable Examples
    st.markdown('<div style="margin-bottom: 0.8rem;"><span style="font-family:\'DM Mono\',monospace;font-size:0.68rem;color:#7f93ad;">TRY →</span></div>', unsafe_allow_html=True)
    
    def apply_example(ex_text):
        st.session_state.topic_input = ex_text
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False

    examples = ["Future of LLM in Tech Industry", "All Latest AI Agents in 2026", "Roadmap for AGI development"]
    chip_cols = st.columns(3)
    for i, ex in enumerate(examples):
        with chip_cols[i]:
            st.button(ex, type="secondary", on_click=apply_example, args=(ex,), use_container_width=True)

# ── UI Placeholders ──
pipeline_ui = col_pipeline.empty()
terminal_ui = col_pipeline.empty()
spinner_ui = col_input.empty()

def draw_pipeline_status(current_running_step=None):
    with pipeline_ui.container():
        st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
        r = st.session_state.results
        def get_state(s_name):
            if s_name in r: return "done"
            if current_running_step == s_name: return "running"
            return "waiting"

        step_card("01", "Search Agent", get_state("search"), "Gathers recent web information")
        step_card("02", "Reader Agent", get_state("reader"), "Scrapes & extracts deep content")
        step_card("03", "Writer Chain", get_state("writer"), "Drafts the full research report")
        step_card("04", "Critic Chain", get_state("critic"), "Reviews & scores the report")

if not st.session_state.running: draw_pipeline_status()

# ── Execution Logic ──
if run_btn:
    if not topic.strip(): st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    terminal_logs = []
    
    try:
        for event in run_research_pipeline(st.session_state.topic_input):
            step = event["step"]
            status = event.get("status")
            
            if step == "complete": break
                
            if status == "running":
                draw_pipeline_status(current_running_step=step)
                with spinner_ui.container():
                    spinner_ui.info(f"⏳ **Agent {step.capitalize()}** is working...")
                    
            elif status == "info":
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                msg = event.get("message", "")
                log_line = f'<div class="terminal-line"><span class="term-time">[{timestamp}]</span><span class="term-step">[{step}]</span><span class="term-msg">{msg}</span></div>'
                terminal_logs.append(log_line)
                
                with terminal_ui.container():
                    st.markdown('<div class="section-heading" style="font-size: 1rem; margin-top: 1.5rem;">Agent Console</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="terminal-console" id="console">{"".join(terminal_logs)}</div>', unsafe_allow_html=True)
                    
            elif status == "done":
                st.session_state.results[step] = event["data"]
                draw_pipeline_status()
                
    except Exception as e:
        spinner_ui.error(f"Pipeline crashed: {str(e)}")

    spinner_ui.empty()
    st.session_state.running = False
    st.session_state.done = True
    st.rerun()

# ── Results display ──
r = st.session_state.results
if st.session_state.done and r:
    st.markdown('<div class="divider"></div><div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel">{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel">{r["reader"]}</div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown('<div class="report-panel"><div class="panel-label orange">📝 Final Research Report</div>', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

    if "critic" in r:
        st.markdown('<div class="feedback-panel"><div class="panel-label green">🧐 Critic Feedback</div>', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)
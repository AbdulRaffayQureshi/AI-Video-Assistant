import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Meeting Assistant — Sprout",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS — soft, natural, airy + 3D paper-craft depth ───────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,500&family=Nunito+Sans:wght@300;400;600;700;800&display=swap');

:root {
    --bg:        #FAF6EF;
    --bg-2:      #F3EDE1;
    --paper:     #FFFFFB;
    --paper-2:   #FBF8F2;
    --line:      #E7DFCF;
    --ink:       #3A362E;
    --ink-muted: #8B8579;
    --sage:      #7C9885;
    --sage-soft: #DCE6DD;
    --sky:       #7FA8C9;
    --sky-soft:  #DDE9F1;
    --blush:     #DE9C8E;
    --blush-soft:#F5DFD8;
    --sun:       #E6B96A;
    --sun-soft:  #F6E7C8;
}

html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
    color: var(--ink) !important;
}

.stApp {
    background:
        radial-gradient(700px 400px at 8% -5%, rgba(124,152,133,0.10), transparent 60%),
        radial-gradient(600px 380px at 95% 8%, rgba(127,168,201,0.10), transparent 55%),
        radial-gradient(500px 320px at 50% 100%, rgba(222,156,142,0.08), transparent 55%),
        var(--bg) !important;
}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}

/* Sidebar is pinned open — collapsing is disabled entirely */
[data-testid="stSidebar"] {
    min-width: 320px !important;
    max-width: 340px !important;
    transform: none !important;
    visibility: visible !important;
    position: relative !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"] {
    display: none !important;
}
.block-container {padding-top:2rem; max-width:1180px;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--paper) 0%, var(--bg-2) 100%) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color: var(--ink) !important; }

/* ── Headings ── */
h1, h2, h3, h4 { font-family: 'Fraunces', serif !important; color: var(--ink) !important; }

/* ── Hero ── */
.hero-wrap { position:relative; padding: 8px 0 4px 0; }
.hero-orb {
    position:absolute; width:220px; height:220px; border-radius:50%;
    background: radial-gradient(circle at 30% 30%, rgba(230,185,106,0.35), transparent 70%);
    top:-60px; right:40px; filter:blur(6px);
    animation: breathe 7s ease-in-out infinite;
}
@keyframes breathe { 0%,100%{ transform:scale(1); opacity:0.8;} 50%{ transform:scale(1.15); opacity:1;} }
.hero-title {
    font-family:'Fraunces', serif; font-weight:600; font-style:italic;
    font-size: clamp(2rem, 4.5vw, 3.2rem); line-height:1.08; margin:0;
    background: linear-gradient(100deg, var(--sage) 0%, var(--sky) 55%, var(--blush) 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero-sub {
    font-family:'Nunito Sans', sans-serif; font-size:0.85rem; color:var(--ink-muted);
    letter-spacing:0.06em; margin-top:0.4rem;
}

/* ── 3D Paper Cards ── */
.card {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow:
        0 1px 1px rgba(58,54,46,0.03),
        0 4px 8px rgba(58,54,46,0.045),
        0 14px 26px rgba(58,54,46,0.06);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.card:hover {
    transform: translateY(-4px) rotate(-0.15deg);
    box-shadow:
        0 2px 3px rgba(58,54,46,0.05),
        0 10px 18px rgba(58,54,46,0.08),
        0 26px 40px rgba(58,54,46,0.10);
}
.card-sage  { border-top: 4px solid var(--sage); }
.card-sky   { border-top: 4px solid var(--sky); }
.card-blush { border-top: 4px solid var(--blush); }
.card-sun   { border-top: 4px solid var(--sun); }

.card-title {
    font-family:'Fraunces', serif; font-weight:600; font-size:1rem;
    color: var(--ink) !important; margin-bottom:0.7rem; display:flex; align-items:center; gap:0.5rem;
}
.card-content { font-size:0.92rem; line-height:1.75; color: var(--ink) !important; }

/* ── Badges (soft pill, embossed) ── */
.badge {
    display:inline-block; padding:0.28rem 0.75rem; border-radius:999px;
    font-size:0.7rem; font-weight:700; letter-spacing:0.04em;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.6), 0 1px 2px rgba(58,54,46,0.08);
}
.badge-sage  { background: var(--sage-soft);  color:#4C6653 !important; }
.badge-sky   { background: var(--sky-soft);   color:#3E6483 !important; }
.badge-blush { background: var(--blush-soft); color:#8C4A3C !important; }
.badge-sun   { background: var(--sun-soft);   color:#8A6116 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div {
    background: var(--paper-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    color: var(--ink) !important;
    font-family:'Nunito Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--sage) !important;
    box-shadow: 0 0 0 3px rgba(124,152,133,0.18) !important;
}

/* ── 3D pressable buttons ── */
.stButton > button {
    background: linear-gradient(180deg, #93AF9B 0%, var(--sage) 100%) !important;
    color: #FBF8F2 !important;
    border: none !important;
    border-radius: 12px !important;
    font-family:'Fraunces', serif !important; font-weight:600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.25) inset,
        0 4px 0 #5C7A64,
        0 8px 14px rgba(92,122,100,0.35) !important;
    transition: transform 0.08s ease, box-shadow 0.08s ease !important;
}
.stButton > button:hover { filter: brightness(1.04) !important; }
.stButton > button:active {
    transform: translateY(4px) !important;
    box-shadow: 0 0 0 #5C7A64, 0 2px 4px rgba(92,122,100,0.3) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--paper-2) !important; color: var(--ink) !important;
    box-shadow: 0 1px 0 rgba(255,255,255,0.6) inset, 0 4px 0 var(--line), 0 6px 10px rgba(58,54,46,0.08) !important;
}

/* ── Pipeline "sprout" status ── */
.status-bar {
    display:flex; align-items:center; gap:0.7rem; padding:0.65rem 0.9rem;
    background: var(--paper-2); border-radius: 12px; margin:0.35rem 0;
    border:1px solid var(--line); font-size:0.82rem; color: var(--ink) !important;
}
.sprout {
    width:12px; height:12px; border-radius:50%; flex-shrink:0;
    background: var(--line); position:relative; transition: all 0.4s ease;
}
.sprout-active { background: var(--sun); box-shadow:0 0 0 4px rgba(230,185,106,0.25); animation: grow 1.2s ease-in-out infinite; }
.sprout-done   { background: var(--sage); box-shadow:0 0 0 4px rgba(124,152,133,0.2); }
@keyframes grow { 0%,100%{ transform:scale(1);} 50%{ transform:scale(1.35);} }

/* ── Transcript / readout ── */
.transcript-box {
    background: var(--paper-2); border:1px solid var(--line); border-radius:14px;
    padding:1.25rem; font-size:0.85rem; line-height:1.85; max-height:320px;
    overflow-y:auto; color:var(--ink-muted); white-space:pre-wrap; word-break:break-word;
}

/* ── Chat ── */
.chat-container {
    background: var(--paper); border:1px solid var(--line); border-radius:18px;
    padding:1.4rem; max-height:440px; overflow-y:auto; margin-bottom:1rem;
    box-shadow: 0 4px 10px rgba(58,54,46,0.05), 0 14px 26px rgba(58,54,46,0.06);
    color: var(--ink) !important;
}
.chat-msg { margin-bottom:1.1rem; display:flex; flex-direction:column; gap:0.25rem; }
.chat-label { font-family:'Fraunces', serif; font-size:0.72rem; font-weight:600; letter-spacing:0.06em; }
.chat-bubble {
    display:inline-block; padding:0.7rem 1.05rem; border-radius:16px;
    font-size:0.88rem; line-height:1.65; max-width:90%;
    color: var(--ink) !important;
}
.user-label  { color:#4C6653 !important; }
.bot-label   { color:#3E6483 !important; }
.user-bubble { background: var(--sage-soft); border:1px solid #CBDACE; align-self:flex-end; border-bottom-right-radius:4px; color:#33402F !important; }
.bot-bubble  { background: var(--sky-soft);  border:1px solid #C6DAE7; align-self:flex-start; border-bottom-left-radius:4px; color:#293D4B !important; }

hr { border:none !important; border-top:1px dashed var(--line) !important; margin:1.6rem 0 !important; }
[data-testid="stMarkdownContainer"] p { color: var(--ink) !important; }
label { color: var(--ink-muted) !important; font-size:0.82rem !important; }

::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: var(--line); border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background: var(--sage); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def sprout_class(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active": return "sprout sprout-active"
    if s == "done":   return "sprout sprout-done"
    return "sprout"

def render_step_bar(label: str, key: str, icon: str):
    css = sprout_class(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="{css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.7rem">🌿 Meeting<br>Sprout</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">grow insight from every conversation</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-sage">🌱 Input</span>', unsafe_allow_html=True)
    st.write("")
    source = st.text_input("YouTube URL or File Path", placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4")
    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    run_btn = st.button("☀️  Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-sky">🌤️ Pipeline Status</span>', unsafe_allow_html=True)
        st.write("")
        for step, icon, label in [
            ("audio",      "🎧", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-orb"></div>
    <div class="hero-title">AI Meeting Assistant</div>
    <div class="hero-sub">🌿 transcribe &nbsp;·&nbsp; 📋 summarise &nbsp;·&nbsp; 💬 chat with your meetings</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("🌱 Please plant a source first — enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("🌤️ Pipeline growing — watch the sidebar for live status…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("🌼 Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"🥀 Something wilted: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="card card-sun">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:600;font-style:italic;color:var(--ink)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card card-sage">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card card-sun">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card card-sky">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card card-blush">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Fraunces\',serif;font-style:italic;font-size:1.3rem;font-weight:600;margin-bottom:1rem;color:var(--ink)">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">🙋 You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🌤️ Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card card-sage" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">🌱</div>
            <div style="color:var(--ink-muted);font-size:0.88rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send 🌤️", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("🌤️ Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🍂 Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🌱</div>
        <div style="font-family:'Fraunces',serif;font-style:italic;font-size:1.7rem;font-weight:600;color:var(--ink);margin-bottom:0.5rem">
            Ready to Grow Some Insight
        </div>
        <div style="color:var(--ink-muted);font-size:0.88rem;max-width:400px;line-height:1.8">
            Plant a YouTube URL or local file path in the sidebar, pick your language, and press <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:0.7rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-sage">📝 Transcription</span>
            <span class="badge badge-sky">📋 Summarisation</span>
            <span class="badge badge-blush">💬 RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)
import os
import streamlit as st
import requests

API = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for simple, clean styling
st.markdown("""
<style>
    /* General */
    .main {
        padding: 1rem 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 2.8em;
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: #667eea;
    }
    
    /* Radio buttons - Simple style */
    div[role="radiogroup"] label {
        background-color: #262626 !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        padding: 0.8rem 1rem !important;
        margin-bottom: 0.5rem !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    
    div[role="radiogroup"] label:hover {
        border-color: #667eea !important;
        background-color: #2d2d2d !important;
    }
    
    /* Selected radio */
    div[role="radiogroup"] label[aria-checked="true"] {
        background-color: #667eea22 !important;
        border-color: #667eea !important;
        border-width: 2px !important;
    }
    
    /* Hide default radio circle */
    div[role="radiogroup"] label > div:first-child {
        border-color: #667eea !important;
    }
    
    /* Question cards */
    .question-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 3px solid #667eea;
        margin-bottom: 2rem;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

DEFAULTS = {
    "page":    "upload",
    "doc_id":  None,
    "quiz":    None,
    "answers": {},
    "result":  None,
    "summary": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── PAGE 1 — UPLOAD ───────────────────────────────────────────────
if st.session_state.page == "upload":
    # Simple header
    st.title("📝 Quiz Generator")
    st.caption("Upload a document and create an AI-powered quiz")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Upload section
    uploaded = st.file_uploader(
        "Upload PDF or PowerPoint",
        type=["pdf", "pptx"],
        help="Educational materials, presentations, or study guides"
    )
    
    if uploaded:
        st.success(f"✓ {uploaded.name} ({uploaded.size / 1024:.1f} KB)")
    
    # Configuration
    topic = st.text_input(
        "Quiz Topic",
        placeholder="e.g., Machine Learning, Data Structures, Business Models",
        help="What should the quiz focus on?"
    )
    
    n_q = st.slider("Number of Questions", 3, 100, 5)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Validation
    topic_valid = bool(topic and len(topic.strip()) > 0)
    button_enabled = uploaded is not None and topic_valid
    
    if not button_enabled:
        if not uploaded:
            st.info("👆 Upload a document to get started")
        elif not topic_valid:
            st.info("✍️ Enter a topic for your quiz")
    
    generate_btn = st.button(
        "Generate Quiz",
        disabled=not button_enabled,
        type="primary",
        use_container_width=True
    )
    
    if generate_btn:
        with st.spinner("Processing document..."):
            r = requests.post(
                f"{API}/ingest",
                files={"file": (uploaded.name, uploaded.getvalue())},
            )
            if r.status_code != 200:
                st.error(f"Upload failed: {r.text}")
                st.stop()
            
            doc_id = r.json()["doc_id"]
            chunks = r.json()["chunk_count"]
        
        with st.spinner(f"Generating {n_q} questions..."):
            r = requests.post(
                f"{API}/quiz",
                json={"doc_id": doc_id, "topic": topic, "n": n_q},
            )
            if r.status_code != 200:
                st.error(f"Generation failed: {r.text}")
                st.stop()
        
        st.success("Quiz ready!")
        st.session_state.doc_id  = doc_id
        st.session_state.quiz    = r.json()
        st.session_state.answers = {str(i): None for i in range(n_q)}
        st.session_state.page    = "quiz"
        st.rerun()


# ── PAGE 2 — QUIZ ─────────────────────────────────────────────────
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    qs   = quiz["questions"]

    # Simple header
    st.title("📝 Quiz")
    st.caption(f"Topic: {quiz['topic']} • {len(qs)} questions")
    
    # Progress
    answered = sum(1 for v in st.session_state.answers.values() if v)
    st.progress(answered / len(qs))
    st.caption(f"{answered} / {len(qs)} answered")
    
    st.markdown("---")

    # Questions
    for i, q in enumerate(qs):
        is_answered = st.session_state.answers[str(i)] is not None
        status = "✅" if is_answered else "⭕"
        
        st.markdown(f"### {status} Question {i+1}")
        st.markdown(f"**{q['question']}**")
        
        # Create options without page numbers
        opts = {c["label"]: c["text"] for c in q["choices"]}
        
        pick = st.radio(
            label            = f"q{i}",
            options          = list(opts.keys()),
            format_func      = lambda x, o=opts: f"{x}. {o[x]}",
            index            = None,
            key              = f"radio_{i}",
            label_visibility = "collapsed",
        )
        st.session_state.answers[str(i)] = pick
        
        if i < len(qs) - 1:
            st.markdown("---")

    # Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    all_done = all(v is not None for v in st.session_state.answers.values())
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Start Over", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
    
    with col2:
        submit_text = "Submit Quiz" if all_done else f"Answer All ({len(qs) - answered} left)"
        if st.button(submit_text, disabled=not all_done, type="primary", use_container_width=True):
            with st.spinner("Scoring..."):
                r = requests.post(
                    f"{API}/score",
                    json={"quiz": quiz, "answers": st.session_state.answers},
                )
                if r.status_code != 200:
                    st.error(f"Scoring failed: {r.text}")
                    st.stop()
                st.session_state.result = r.json()
                st.session_state.page   = "results"
                st.rerun()


# ── PAGE 3 — RESULTS ──────────────────────────────────────────────
elif st.session_state.page == "results":
    r   = st.session_state.result
    pct = r["score_percent"]

    # Simple header
    st.title("🎯 Results")
    
    # Score display - simplified
    color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"
    
    if pct == 100:
        emoji, mood = "🏆", "Perfect!"
    elif pct >= 90:
        emoji, mood = "🎉", "Excellent!"
    elif pct >= 80:
        emoji, mood = "😊", "Great!"
    elif pct >= 70:
        emoji, mood = "🙂", "Good!"
    elif pct >= 60:
        emoji, mood = "😐", "Not Bad"
    elif pct >= 40:
        emoji, mood = "😕", "Needs Work"
    elif pct >= 20:
        emoji, mood = "😟", "Keep Trying"
    else:
        emoji, mood = "😢", "Study More"
    
    # Score card
    st.markdown(f"""
        <div style='text-align: center; padding: 2rem; background: {color}22; border: 2px solid {color}; border-radius: 12px; margin: 1rem 0;'>
            <div style='font-size: 4rem;'>{emoji}</div>
            <h1 style='color: {color}; font-size: 3rem; margin: 0.5rem 0;'>{r['correct']} / {r['total']}</h1>
            <p style='font-size: 1.5rem; color: {color}; font-weight: 600;'>{pct}% • {mood}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(pct / 100)
    
    # Feedback
    if pct == 100:
        st.success("Perfect score! You've mastered this material.")
    elif pct >= 70:
        st.success("Great job! You have a solid understanding.")
    elif pct >= 40:
        st.warning("Good effort. Review the explanations below.")
    else:
        st.error("Keep learning. Study the explanations carefully.")
    
    st.markdown("---")
    
    # Questions review
    st.subheader("📖 Review")
    
    for i, item in enumerate(r["breakdown"]):
        icon = "✅" if item["was_correct"] else "❌"
        
        with st.expander(f"{icon} Question {i+1}: {item['question']}", expanded=not item["was_correct"]):
            if item["was_correct"]:
                st.success(f"Your answer: **{item['your_answer']}** ✓")
            else:
                st.error(f"Your answer: **{item['your_answer']}**")
                st.info(f"Correct answer: **{item['correct_answer']}**")
            
            st.markdown(f"**Explanation:** {item['explanation']}")
            
            # Page reference
            page_num = item.get('page_number', 0)
            if page_num and page_num > 0:
                page_label = "Page" if "pdf" in st.session_state.quiz.get("filename", "").lower() else "Slide"
                st.caption(f"📍 {page_label} {page_num}: {item['source_text']}")
            else:
                st.caption(f"📍 {item['source_text']}")
    
    # Action buttons
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
    
    with col2:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.answers = {str(i): None for i in range(len(st.session_state.quiz["questions"]))}
            st.session_state.result = None
            st.session_state.summary = None
            st.session_state.page = "quiz"
            st.rerun()
    
    with col3:
        if st.button("📊 AI Analysis", use_container_width=True):
            with st.spinner("Analyzing..."):
                r = requests.post(
                    f"{API}/summarize",
                    json={
                        "doc_id": st.session_state.doc_id,
                        "quiz": st.session_state.quiz,
                        "result": st.session_state.result,
                    },
                )
                if r.status_code == 200:
                    st.session_state.summary = r.json()
                    st.rerun()
                else:
                    st.error(f"Analysis failed: {r.text}")
    
    with col4:
        if st.button("🆕 New Quiz", type="primary", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
    
    # Display AI Summary if available
    if st.session_state.summary:
        summary = st.session_state.summary
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 🎓 Personalized Learning Analysis")
        
        # Overall Performance
        st.markdown("### 📈 Overall Performance")
        st.info(summary["overall_performance"])
        
        # Strengths and Weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Your Strengths")
            if summary["strengths"]:
                for strength in summary["strengths"]:
                    st.success(f"✓ {strength}")
            else:
                st.caption("Keep practicing to build strengths!")
        
        with col2:
            st.markdown("### 📚 Areas to Improve")
            if summary["weaknesses"]:
                for weakness in summary["weaknesses"]:
                    st.warning(f"⚠ {weakness}")
            else:
                st.caption("Great job! No major weaknesses identified.")
        
        # Key Concepts with Page References
        st.markdown("### 🔑 Key Concepts & Document References")
        
        for concept in summary["key_concepts"]:
            mastery = concept["mastery"]
            
            if mastery == "excellent":
                color = "#10b981"
                icon = "🏆"
                badge = "Mastered"
            elif mastery == "good":
                color = "#f59e0b"
                icon = "📖"
                badge = "Good Understanding"
            else:
                color = "#ef4444"
                icon = "📝"
                badge = "Needs Review"
            
            pages_str = ", ".join([f"p.{p}" for p in concept["pages"]]) if concept["pages"] else "Multiple sections"
            
            st.markdown(f"""
                <div style='background: {color}22; padding: 1rem; border-radius: 8px; border-left: 4px solid {color}; margin: 0.5rem 0;'>
                    <strong>{icon} {concept['concept']}</strong>
                    <span style='background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;'>{badge}</span>
                    <br>
                    <span style='color: #666; font-size: 0.9rem;'>📄 Found in: {pages_str}</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### 💡 Personalized Recommendations")
        for i, rec in enumerate(summary["recommendations"], 1):
            st.markdown(f"{i}. {rec}")
        
        # Study Plan
        st.markdown("### 📅 Your Study Plan")
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%); padding: 1.5rem; border-radius: 12px; border: 2px solid #667eea;'>
                {summary['study_plan']}
            </div>
        """, unsafe_allow_html=True)

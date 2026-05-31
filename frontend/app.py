import os
import streamlit as st
import requests

API = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Doc Quiz", layout="wide")

DEFAULTS = {
    "page":    "upload",
    "doc_id":  None,
    "quiz":    None,
    "answers": {},
    "result":  None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── PAGE 1 — UPLOAD ───────────────────────────────────────────────
if st.session_state.page == "upload":
    st.title("Upload your document")
    st.caption("PDF or PPTX — the system reads it and builds a quiz")

    uploaded = st.file_uploader("Choose a file", type=["pdf", "pptx"])
    topic    = st.text_input(
        "What topic should the quiz focus on?",
        placeholder="e.g. Deep learning fundamentals"
    )
    n_q = st.slider("Number of questions", 3, 10, 5)

    if st.button("Generate quiz",
                 disabled=not (uploaded and topic),
                 type="primary"):

        with st.spinner("Uploading and processing document..."):
            r = requests.post(
                f"{API}/ingest",
                files={"file": (uploaded.name, uploaded.getvalue())},
            )
            if r.status_code != 200:
                st.error(f"Upload failed: {r.text}")
                st.stop()
            doc_id = r.json()["doc_id"]
            chunks = r.json()["chunk_count"]
            st.caption(f"Processed {chunks} chunks.")

        with st.spinner("Generating questions with Azure AI..."):
            r = requests.post(
                f"{API}/quiz",
                json={"doc_id": doc_id, "topic": topic, "n": n_q},
            )
            if r.status_code != 200:
                st.error(f"Generation failed: {r.text}")
                st.stop()

        st.session_state.doc_id  = doc_id
        st.session_state.quiz    = r.json()
        st.session_state.answers = {str(i): None for i in range(n_q)}
        st.session_state.page    = "quiz"
        st.rerun()


# ── PAGE 2 — QUIZ ─────────────────────────────────────────────────
elif st.session_state.page == "quiz":
    quiz = st.session_state.quiz
    qs   = quiz["questions"]

    st.title("Answer the questions")
    st.caption(f"Topic: **{quiz['topic']}** · {len(qs)} questions")

    answered = sum(1 for v in st.session_state.answers.values() if v)
    st.progress(answered / len(qs), text=f"{answered} / {len(qs)} answered")
    st.divider()

    for i, q in enumerate(qs):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        opts = {c["label"]: f"{c['label']}.  {c['text']}" for c in q["choices"]}
        pick = st.radio(
            label            = f"q{i}",
            options          = list(opts.keys()),
            format_func      = lambda x, o=opts: o[x],
            index            = None,
            key              = f"radio_{i}",
            label_visibility = "collapsed",
        )
        st.session_state.answers[str(i)] = pick
        st.divider()

    all_done = all(v is not None for v in st.session_state.answers.values())
    c1, c2   = st.columns(2)

    with c1:
        if st.button("← Start over"):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

    with c2:
        if st.button("Submit answers →",
                     disabled=not all_done,
                     type="primary"):
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

    st.title("Your results")

    color = "green" if pct >= 70 else "orange" if pct >= 40 else "red"
    st.markdown(
        f"<h2 style='color:{color}; text-align:center'>"
        f"{r['correct']} / {r['total']} correct — {pct}%"
        f"</h2>",
        unsafe_allow_html=True,
    )
    st.progress(pct / 100)

    if pct == 100:
        st.success("Perfect score!")
    elif pct >= 70:
        st.success("Good job — you know this material well.")
    elif pct >= 40:
        st.warning("Decent — review the explanations below.")
    else:
        st.error("Keep studying — go through each explanation carefully.")

    st.divider()

    for i, item in enumerate(r["breakdown"]):
        icon = "✅" if item["was_correct"] else "❌"
        with st.expander(f"{icon}  Q{i+1}: {item['question']}"):
            if item["was_correct"]:
                st.success(f"Your answer: **{item['your_answer']}** — Correct!")
            else:
                st.error(f"Your answer: **{item['your_answer']}**")
                st.info(f"Correct answer: **{item['correct_answer']}**")
            st.markdown(f"**Why:** {item['explanation']}")
            st.caption(f"Source: *{item['source_text']}*")

    st.divider()
    if st.button("Take another quiz", type="primary"):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

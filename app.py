import streamlit as st
import pdfplumber
import io
import json
import re
import os
from huggingface_hub import InferenceClient

st.set_page_config(page_title="ATS Score Agent", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif!important}
.stApp{background:#0a0c0f;color:#e2e8f0}
[data-testid="stAppViewContainer"]{background:#0a0c0f}
[data-testid="stHeader"]{background:transparent}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}
.top-bar{background:#0d1117;border-bottom:1px solid #1e2530;padding:16px 40px;display:flex;align-items:center;gap:14px}
.logo-chip{width:38px;height:38px;background:linear-gradient(135deg,#4ade80,#22d3ee);border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:17px;color:#0a0c0f}
.top-title{font-size:18px;font-weight:800;letter-spacing:-.5px;color:#e2e8f0}
.top-badge{margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:11px;color:#4ade80;background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.25);padding:4px 10px;border-radius:20px}
.main-wrap{padding:32px 40px;max-width:1200px;margin:0 auto}
.card-label{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#4ade80;margin-bottom:6px}
.score-hero{background:linear-gradient(135deg,#111418 0%,#0d1520 100%);border:1px solid #1e2530;border-radius:16px;padding:36px 40px;margin-bottom:24px;position:relative;overflow:hidden}
.score-hero::before{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(74,222,128,.08) 0%,transparent 70%);border-radius:50%}
.score-number{font-family:'JetBrains Mono',monospace;font-size:80px;font-weight:700;line-height:1;letter-spacing:-4px}
.score-grade{font-family:'JetBrains Mono',monospace;font-size:14px;color:#64748b;margin-top:4px}
.score-label{font-size:24px;font-weight:800;letter-spacing:-.5px;margin-bottom:10px}
.score-summary-text{font-size:15px;color:#94a3b8;line-height:1.7;max-width:480px}
.subscore-wrap{background:#0d1117;border:1px solid #1e2530;border-radius:10px;padding:16px 20px;margin-bottom:12px}
.subscore-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.subscore-name{font-family:'JetBrains Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px}
.subscore-val{font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600}
.bar-track{height:4px;background:#1e2530;border-radius:4px;overflow:hidden}
.bar-fill-inner{height:100%;border-radius:4px}
.tags-wrap{display:flex;flex-wrap:wrap;gap:7px;margin-top:4px}
.tag{font-family:'JetBrains Mono',monospace;font-size:11px;padding:5px 11px;border-radius:20px;font-weight:500}
.tag-match{background:rgba(74,222,128,.1);color:#4ade80;border:1px solid rgba(74,222,128,.2)}
.tag-miss{background:rgba(248,113,113,.08);color:#f87171;border:1px solid rgba(248,113,113,.2)}
.tag-tool{background:rgba(245,158,11,.08);color:#f59e0b;border:1px solid rgba(245,158,11,.2)}
.tag-soft{background:rgba(167,139,250,.1);color:#a78bfa;border:1px solid rgba(167,139,250,.2)}
.tag-domain{background:rgba(34,211,238,.08);color:#22d3ee;border:1px solid rgba(34,211,238,.2)}
.kw-group{margin-bottom:18px}
.kw-group-label{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:#64748b;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.count-badge{font-family:'JetBrains Mono',monospace;font-size:10px;background:rgba(248,113,113,.15);color:#f87171;padding:2px 8px;border-radius:10px}
.count-badge-ok{font-family:'JetBrains Mono',monospace;font-size:10px;background:rgba(74,222,128,.1);color:#4ade80;padding:2px 8px;border-radius:10px}
.action-item{display:flex;align-items:flex-start;gap:12px;background:#0d1117;border:1px solid #1e2530;border-radius:10px;padding:14px 16px;margin-bottom:10px}
.priority-pill{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:3px 9px;border-radius:5px;flex-shrink:0;margin-top:2px}
.pill-high{background:rgba(248,113,113,.15);color:#f87171}
.pill-medium{background:rgba(245,158,11,.12);color:#f59e0b}
.pill-low{background:rgba(74,222,128,.1);color:#4ade80}
.action-text{font-size:13px;color:#94a3b8;line-height:1.65}
.strength-item{background:#0d1117;border:1px solid #1e2530;border-radius:10px;padding:13px 16px;margin-bottom:9px;font-size:13px;color:#94a3b8;line-height:1.65;display:flex;gap:10px}
.strength-check{color:#4ade80;font-weight:700;flex-shrink:0}
.grammar-card{background:#0d1117;border:1px solid #1e2530;border-radius:12px;padding:18px 20px;margin-bottom:12px}
.grammar-type-badge{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:3px 9px;border-radius:5px;display:inline-block;margin-bottom:12px}
.type-grammar{background:rgba(248,113,113,.12);color:#f87171}
.type-spelling{background:rgba(245,158,11,.12);color:#f59e0b}
.type-clarity{background:rgba(167,139,250,.1);color:#a78bfa}
.type-tense{background:rgba(251,191,36,.1);color:#fbbf24}
.type-style{background:rgba(34,211,238,.08);color:#22d3ee}
.grammar-original{font-family:'JetBrains Mono',monospace;font-size:13px;color:#f87171;background:rgba(248,113,113,.06);border:1px solid rgba(248,113,113,.15);border-radius:6px;padding:10px 14px;margin-bottom:6px;line-height:1.6;text-decoration:line-through}
.grammar-correction{font-family:'JetBrains Mono',monospace;font-size:13px;color:#4ade80;background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.15);border-radius:6px;padding:10px 14px;margin-bottom:10px;line-height:1.6}
.grammar-arrow{text-align:center;color:#2e3540;font-size:18px;margin:2px 0}
.grammar-explanation{font-size:13px;color:#64748b;line-height:1.6}
.section-header{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#4ade80;margin:24px 0 12px;display:flex;align-items:center;gap:10px}
.section-header::after{content:'';flex:1;height:1px;background:#1e2530}
[data-testid="stFileUploader"]{background:#0d1117!important;border:1.5px dashed #2e3540!important;border-radius:10px!important}
textarea{background:#0d1117!important;border:1.5px solid #2e3540!important;border-radius:10px!important;color:#e2e8f0!important;font-family:'JetBrains Mono',monospace!important;font-size:13px!important}
.stButton>button{background:#4ade80!important;color:#0a0c0f!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:15px!important;border:none!important;border-radius:10px!important;padding:14px 0!important;width:100%!important}
.stButton>button:hover{background:#22d3ee!important}
.err-box{background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.3);border-radius:10px;padding:16px;color:#f87171;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6}
.info-box{background:rgba(34,211,238,.06);border:1px solid rgba(34,211,238,.2);border-radius:10px;padding:14px 18px;font-size:13px;color:#94a3b8;line-height:1.6;margin-bottom:20px}
.info-box code{font-family:'JetBrains Mono',monospace;color:#22d3ee;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-bar">
  <span class="logo-chip">A</span>
  <span class="top-title">ATS Score Agent</span>
  <span class="top-badge">● HuggingFace · Free</span>
</div>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────
def extract_pdf_text(f) -> str:
    with pdfplumber.open(io.BytesIO(f.read())) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)

def get_hf_token() -> str:
    try:
        return st.secrets["HF_TOKEN"]
    except Exception:
        return os.environ.get("HF_TOKEN", "")

def call_hf(prompt: str, model: str, token: str, max_tokens: int = 1400) -> str:
    client = InferenceClient(token=token)
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=max_tokens,
        temperature=0.1,
    )
    return response.choices[0].message.content

def extract_json_obj(text: str) -> dict:
    m = re.search(r'\{[\s\S]*\}', text)
    if m: return json.loads(m.group())
    raise ValueError(f"No JSON found: {text[:200]}")

def extract_json_arr(text: str) -> list:
    m = re.search(r'\[[\s\S]*\]', text)
    if m:
        try: return json.loads(m.group())
        except: return []
    return []

def build_ats_prompt(resume: str, jd: str) -> str:
    return f"""You are an expert ATS analyst. Analyze the resume vs job description.
Return ONLY valid JSON. No markdown, no text outside the JSON.

RESUME:
{resume[:3500]}

JOB DESCRIPTION:
{jd[:2000]}

Return ONLY this JSON structure:
{{
  "ats_score": <0-100>,
  "grade": "<A/B/C/D/F>",
  "summary": "<2-3 sentence assessment>",
  "strengths": ["<s1>", "<s2>", "<s3>"],
  "improvements": [
    {{"priority": "high", "action": "<specific action>"}},
    {{"priority": "medium", "action": "<specific action>"}},
    {{"priority": "low", "action": "<specific action>"}}
  ],
  "section_scores": {{
    "skills_match": <0-100>,
    "experience_relevance": <0-100>,
    "education_fit": <0-100>,
    "keyword_density": <0-100>
  }},
  "keywords": {{
    "technical_skills": {{
      "matched": ["<skill1>", "<skill2>"],
      "missing": ["<skill1>", "<skill2>"]
    }},
    "tools_technologies": {{
      "matched": ["<tool1>"],
      "missing": ["<tool1>", "<tool2>"]
    }},
    "soft_skills": {{
      "matched": ["<skill1>"],
      "missing": ["<skill1>"]
    }},
    "domain_terms": {{
      "matched": ["<term1>"],
      "missing": ["<term1>"]
    }}
  }}
}}"""

def build_grammar_prompt(resume: str) -> str:
    return f"""You are a professional resume editor. Find all grammar, spelling, tense, clarity, and style issues in this resume.

RESUME:
{resume[:4000]}

Return ONLY a valid JSON array. Empty array [] if no issues found.
Format:
[
  {{
    "type": "<grammar|spelling|tense|clarity|style>",
    "original": "<exact short phrase or sentence from resume with the issue>",
    "correction": "<corrected version>",
    "explanation": "<why this is wrong and how the fix helps>"
  }}
]

Check for:
- Grammar errors (wrong articles, prepositions, subject-verb agreement)
- Spelling mistakes
- Mixed tenses (present/past in same bullet)
- Weak verbs (responsible for, worked on → led, developed, built)
- Passive voice (was responsible for → led)
- Vague language (various tasks, several projects)
- Run-on sentences
Return max 10 real issues. Do NOT invent problems."""

def score_color(s: int) -> str:
    return "#4ade80" if s >= 80 else "#f59e0b" if s >= 60 else "#f87171"

def score_label(s: int) -> str:
    return "Strong Match" if s >= 80 else "Good Match" if s >= 60 else "Partial Match" if s >= 40 else "Needs Work"

def render_bar(label: str, val: int):
    c = score_color(val)
    st.markdown(f"""<div class="subscore-wrap">
      <div class="subscore-header">
        <span class="subscore-name">{label}</span>
        <span class="subscore-val" style="color:{c}">{val}</span>
      </div>
      <div class="bar-track"><div class="bar-fill-inner" style="width:{val}%;background:{c}"></div></div>
    </div>""", unsafe_allow_html=True)

def render_kw_group(label: str, matched: list, missing: list, miss_class: str):
    badge = f'<span class="count-badge">−{len(missing)}</span>' if missing else '<span class="count-badge-ok">✓</span>'
    st.markdown(f'<div class="kw-group"><div class="kw-group-label">{label} {badge}</div>', unsafe_allow_html=True)
    if matched:
        st.markdown('<div class="tags-wrap">' + "".join(f'<span class="tag tag-match">{k}</span>' for k in matched) + '</div>', unsafe_allow_html=True)
    if missing:
        st.markdown('<div class="tags-wrap" style="margin-top:6px">' + "".join(f'<span class="tag {miss_class}">{k}</span>' for k in missing) + '</div>', unsafe_allow_html=True)
    if not matched and not missing:
        st.markdown('<div style="color:#64748b;font-size:12px;font-family:\'JetBrains Mono\',monospace">—</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_grammar(issue: dict):
    t = issue.get("type", "grammar")
    st.markdown(f"""<div class="grammar-card">
      <span class="grammar-type-badge type-{t}">{t}</span>
      <div class="grammar-original">✗ &nbsp;{issue.get('original','')}</div>
      <div class="grammar-arrow">↓</div>
      <div class="grammar-correction">✓ &nbsp;{issue.get('correction','')}</div>
      <div class="grammar-explanation">{issue.get('explanation','')}</div>
    </div>""", unsafe_allow_html=True)


# ── Main UI ───────────────────────────────────────────────
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

hf_token = get_hf_token()
if not hf_token:
    st.markdown("""<div class="info-box">
      ⚠ <strong>HuggingFace token not set.</strong><br>
      Add <code>HF_TOKEN = "hf_..."</code> in Streamlit Cloud → Settings → Secrets.<br>
      Get a free token at <a href="https://huggingface.co/settings/tokens" target="_blank" style="color:#22d3ee">huggingface.co/settings/tokens</a> (Read access is enough).
    </div>""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown('<div class="card-label">📄 Resume PDF</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
with col2:
    st.markdown('<div class="card-label">📋 Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area("", height=200,
        placeholder="Paste the full job description here...\n\nInclude role title, required skills, tools, responsibilities...",
        label_visibility="collapsed")

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 3])
with c1:
    st.markdown('<div class="card-label">🤖 Model</div>', unsafe_allow_html=True)
    model_choice = st.selectbox("", [
        "meta-llama/Llama-3.1-8B-Instruct",
        "Qwen/Qwen2.5-7B-Instruct-1M",
        "google/gemma-2-2b-it",
        "Qwen/Qwen3-4B-Thinking-2507",
        "mistralai/Mistral-7B-Instruct-v0.3",
    ], label_visibility="collapsed")
with c2:
    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
    go = st.button("Analyze Resume →", use_container_width=True)


# ── Analysis ──────────────────────────────────────────────
if go:
    if not uploaded_file:
        st.markdown('<div class="err-box">⚠ Please upload your resume PDF.</div>', unsafe_allow_html=True)
    elif not jd_text.strip():
        st.markdown('<div class="err-box">⚠ Please paste the job description.</div>', unsafe_allow_html=True)
    elif not hf_token:
        st.markdown('<div class="err-box">⚠ HuggingFace token missing.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Extracting resume text..."):
            try:
                resume_text = extract_pdf_text(uploaded_file)
                if not resume_text.strip():
                    st.markdown('<div class="err-box">⚠ No text found. Use a digital PDF, not a scanned image.</div>', unsafe_allow_html=True)
                    st.stop()
            except Exception as e:
                st.markdown(f'<div class="err-box">⚠ PDF error: {e}</div>', unsafe_allow_html=True)
                st.stop()

        # Call 1: ATS
        with st.spinner(f"Running ATS analysis ({model_choice.split('/')[-1]})... 30–60s"):
            try:
                raw = call_hf(build_ats_prompt(resume_text, jd_text), model_choice, hf_token, 1400)
                ats = extract_json_obj(raw)
            except json.JSONDecodeError:
                st.markdown('<div class="err-box">⚠ Model returned invalid JSON. Try Mistral-7B-Instruct-v0.3.</div>', unsafe_allow_html=True)
                st.stop()
            except Exception as e:
                st.markdown(f'<div class="err-box">⚠ {e}</div>', unsafe_allow_html=True)
                st.stop()

        # Call 2: Grammar (non-fatal)
        grammar = []
        with st.spinner("Checking grammar and language quality..."):
            try:
                raw_g = call_hf(build_grammar_prompt(resume_text), model_choice, hf_token, 1200)
                grammar = extract_json_arr(raw_g)
            except Exception:
                grammar = []

        # ── Render ────────────────────────────────────────
        score = ats.get("ats_score", 0)
        color = score_color(score)

        st.markdown(f"""<div class="score-hero">
          <div style="display:flex;align-items:center;gap:48px;flex-wrap:wrap">
            <div>
              <div class="score-number" style="color:{color}">{score}</div>
              <div class="score-grade">Grade {ats.get('grade','?')} &nbsp;·&nbsp; ATS Score</div>
            </div>
            <div>
              <div class="score-label">{score_label(score)}</div>
              <div class="score-summary-text">{ats.get('summary','')}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Scores + Keywords
        l, r = st.columns(2, gap="large")
        with l:
            st.markdown('<div class="section-header">Section Scores</div>', unsafe_allow_html=True)
            ss = ats.get("section_scores", {})
            render_bar("Skills Match", ss.get("skills_match", 0))
            render_bar("Experience Relevance", ss.get("experience_relevance", 0))
            render_bar("Education Fit", ss.get("education_fit", 0))
            render_bar("Keyword Density", ss.get("keyword_density", 0))

        with r:
            st.markdown('<div class="section-header">Keywords by Category</div>', unsafe_allow_html=True)
            kw = ats.get("keywords", {})
            render_kw_group("Technical Skills",
                kw.get("technical_skills",{}).get("matched",[]),
                kw.get("technical_skills",{}).get("missing",[]), "tag-miss")
            render_kw_group("Tools & Technologies",
                kw.get("tools_technologies",{}).get("matched",[]),
                kw.get("tools_technologies",{}).get("missing",[]), "tag-tool")
            render_kw_group("Soft Skills",
                kw.get("soft_skills",{}).get("matched",[]),
                kw.get("soft_skills",{}).get("missing",[]), "tag-soft")
            render_kw_group("Domain Terms",
                kw.get("domain_terms",{}).get("matched",[]),
                kw.get("domain_terms",{}).get("missing",[]), "tag-domain")

        # Strengths + Actions
        s_col, i_col = st.columns(2, gap="large")
        with s_col:
            st.markdown('<div class="section-header">Strengths</div>', unsafe_allow_html=True)
            for s in ats.get("strengths", []):
                st.markdown(f'<div class="strength-item"><span class="strength-check">✓</span>{s}</div>', unsafe_allow_html=True)
        with i_col:
            st.markdown('<div class="section-header">Action Items</div>', unsafe_allow_html=True)
            for item in ats.get("improvements", []):
                p = item.get("priority","low")
                st.markdown(f"""<div class="action-item">
                  <span class="priority-pill pill-{p}">{p}</span>
                  <span class="action-text">{item.get('action','')}</span>
                </div>""", unsafe_allow_html=True)

        # Grammar
        n = len(grammar)
        gb = f'<span class="count-badge">{n} issue{"s" if n!=1 else ""}</span>' if n else '<span class="count-badge-ok">✓ Clean</span>'
        st.markdown(f'<div class="section-header">Grammar & Language Check {gb}</div>', unsafe_allow_html=True)

        if not grammar:
            st.markdown('<div class="strength-item"><span class="strength-check">✓</span>No grammar or language issues found. Resume language looks clean!</div>', unsafe_allow_html=True)
        else:
            g1, g2 = st.columns(2, gap="large")
            mid = (n + 1) // 2
            with g1:
                for issue in grammar[:mid]: render_grammar(issue)
            with g2:
                for issue in grammar[mid:]: render_grammar(issue)

        with st.expander("View raw JSON"):
            st.json({"ats_analysis": ats, "grammar_issues": grammar})

st.markdown('</div>', unsafe_allow_html=True)

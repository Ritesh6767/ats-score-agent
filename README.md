# 🎯 ATS Score Agent — Streamlit Cloud

Always-on ATS resume scorer using HuggingFace Inference API (free).

**Live once deployed:** `https://your-app-name.streamlit.app`

---

## Deploy to Streamlit Cloud (step-by-step)

### Step 1 — Get a free HuggingFace token
1. Go to https://huggingface.co/settings/tokens
2. Click **New token**
3. Name it anything, Role = **Read**
4. Copy the token (starts with `hf_...`)

### Step 2 — Push to GitHub
```bash
# Create a new repo on github.com first, then:
git init
git add .
git commit -m "ATS Score Agent"
git remote add origin https://github.com/YOUR_USERNAME/ats-score-agent.git
git push -u origin main
```

### Step 3 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **New app**
4. Select your repo → Branch: `main` → File: `app.py`
5. Click **Advanced settings** → **Secrets** tab
6. Paste this:
   ```toml
   HF_TOKEN = "hf_your_actual_token_here"
   ```
7. Click **Deploy!**

Wait ~2 minutes → your app is live at `https://your-app.streamlit.app` 🎉

---

## Run Locally

```bash
pip install -r requirements.txt

# Add your token to .streamlit/secrets.toml
# (edit the file, replace hf_your_token_here)

streamlit run app.py
```
Opens at http://localhost:8501

---

## Models Available (all free on HF)

| Model | Speed | Quality | Notes |
|-------|-------|---------|-------|
| Mixtral-8x7B-Instruct | Slow | Best | May timeout on free tier |
| Mistral-7B-Instruct-v0.3 | Medium | Very Good | **Recommended** |
| Zephyr-7B-beta | Medium | Good | Reliable free tier |
| Phi-3-mini-4k | Fast | Good | Lightweight |
| Gemma-2-2b-it | Fastest | OK | Use if others timeout |

**Tip:** If you get a timeout error, switch to a smaller model from the dropdown.

---

## Project Structure

```
ats-score-agent/
├── app.py              ← Main Streamlit app
├── requirements.txt    ← Python dependencies
├── .gitignore          ← Excludes secrets from git
├── .streamlit/
│   └── secrets.toml    ← Your HF token (NOT committed to git)
└── README.md
```

# Job Application Agent

An AI-powered agentic system that automates the job application process. 
Given a job description, the agent tailors your CV, writes a personalized 
cover letter, saves both documents, and emails them to the recruiter — 
all autonomously using a ReAct loop.

---

## What makes this an agent (not just a prompt)

Most AI writing tools generate text when you ask them to. This project goes 
further — it follows a **ReAct loop** (Reason + Act), meaning the AI thinks 
about what to do next, calls a real tool, observes the result, and decides 
the next step. It also takes real-world actions: saving files to disk and 
sending actual emails via Gmail SMTP.

Thought → Action → Observation → Thought → Action → ...

The agent calls 6 tools in sequence, each doing something concrete:

get_company_info  →  Searches the web for real company data (via MCP server)
read_cv           →  Reads your CV from disk
tailor_cv         →  Rewrites your CV to match the job description
draft_cover_letter→  Writes a personalized cover letter
save_file         →  Saves both documents to the outputs/ folder
send_email        →  Emails everything to the recruiter via Gmail


---

## Architecture

┌─────────────────────────────────────────────────────┐
│                     agent.py                        │
│           LangGraph ReAct Agent                     │
│           Model: Groq — Llama 3.3 70B               │
└─────────────────────┬───────────────────────────────┘
                      │  calls tools
                      ▼
┌─────────────────────────────────────────────────────┐
│                     tools.py                        │
│                                                     │
│  read_cv  →  tailor_cv  →  draft_cover_letter       │
│  save_file  →  send_email  →  get_company_info      │
└─────────────────────┬───────────────────────────────┘
                      │  HTTP POST
                      ▼
┌─────────────────────────────────────────────────────┐
│                  mcp_server.py                      │
│           FastAPI MCP Server                        │
│           DuckDuckGo web search                     │
└─────────────────────────────────────────────────────┘

---

## Tech stack

| Component | Technology |
|---|---|
| Agent framework | LangGraph (LangChain) |
| AI model | Groq API — Llama 3.3 70B (free tier) |
| Tool calling | LangChain `@tool` decorator |
| MCP server | FastAPI |
| Company search | DuckDuckGo Search (free, no API key) |
| Email | Gmail SMTP via Python `smtplib` |
| Environment | Python 3.11, `python-dotenv` |

---

## Project structure

job-agent/
├── agent.py          ← ReAct agent — orchestrates the full pipeline
├── tools.py          ← All 6 tools the agent can call
├── mcp_server.py     ← FastAPI MCP server for company web search
├── my_cv.txt         ← Your CV in plain text (not committed to git)
├── outputs/          ← Tailored CVs and cover letters saved here
├── .env              ← API keys and email config (not committed to git)
├── requirements.txt  ← All Python dependencies
└── README.md

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/job-agent.git
cd job-agent
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

Create a file called `.env` in the root folder and add:

GROQ_API_KEY=your_groq_api_key
EMAIL_SENDER=yourgmail@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_RECEIVER=hr@company.com

**Getting your Groq API key** — sign up free at console.groq.com

**Getting your Gmail App Password:**
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification
3. Search "App Passwords" → generate one for Mail
4. Paste the 16-character password (no spaces) into `.env`

### 5. Add your CV

Create a file called `my_cv.txt` in the root folder and paste your CV 
as plain text.

### 6. Create the outputs folder

```bash
mkdir outputs
```

---

## How to run

You need two terminals open simultaneously.

**Terminal 1 — Start the MCP server:**

```bash
uvicorn mcp_server:app --reload
```

You should see:
INFO: Uvicorn running on http://127.0.0.1:8000

**Terminal 2 — Run the agent:**

```bash
python agent.py
```

Paste a job description when prompted, then type `END` on a new line 
and press Enter. The agent will handle everything from there.

---

## Example output

Enter job description (or 'exit'): We are hiring a Python Developer at Google...

get_company_info called for: Google
Company info received: Google is a multinational technology company...

Read CV called
Tailor CV called
draft_cover_letter called
save_file called
Files saved at:
  - outputs/tailored_cv_2026-04-18.txt
  - outputs/cover_letter_2026-04-18.txt
send_email called
Email sent successfully!

Final Output:
FINAL ANSWER: Email sent successfully with CV and cover letter.

---

## Planned enhancements

- [ ] Frontend web UI — paste JD and trigger agent from a browser
- [ ] Dynamic email subject — auto-extract job title from JD
- [ ] Application log — track all applications in a CSV file
- [ ] `.docx` output — save CV and cover letter as Word documents
- [ ] Job URL scraper — paste a LinkedIn URL instead of raw JD text
- [ ] Batch mode — process multiple job descriptions at once

---

## What I learned building this

- How the **ReAct (Reason + Act) pattern** works in agentic AI systems
- How to build and connect an **MCP (Model Context Protocol) server** 
  using FastAPI
- How to define **LangChain tools** and wire them into a LangGraph agent
- How to manage **agent memory** across tool calls using a shared dict
- How to integrate **real-world actions** (file saving, email sending) 
  into an AI pipeline
- Practical experience debugging **LLM tool-calling errors** on free 
  model tiers

---

## License

MIT
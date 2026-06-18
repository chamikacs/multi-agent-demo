# Multi-agent systems: a runnable demo, an article, and an interactive explainer

This project teaches one idea three ways: a team of AI agents (an orchestrator
delegating to a researcher, a writer, and a critic) beats a single do-everything
agent, because the critic can send weak work back for another round.

It contains three parts that tell the same story:

| Part | File | For whom |
| ---- | ---- | -------- |
| Runnable demo | `main.py`, `handoff_demo.py` | developers who want to run real agents |
| Research article | `ARTICLE.md` | anyone wanting the concepts and the 2026 landscape |
| Interactive explainer | `index.html` | non-technical coworkers, zero setup |

All three describe the **same architecture**:

```
Orchestrator  ->  Researcher  ->  Writer  ->  Critic
                                     ^            |
                                     |____________|
                                  "send it back"
```

## The free-stack rationale

Everything here runs for **free**.

- The Python demo uses **Google Gemini's free tier** (model
  `gemini-2.0-flash`). A free key requires no credit card.
- The interactive page (`index.html`) is a **single self-contained file** with a
  scripted, simulated crew. It makes **no API calls** and needs **no key**, so
  coworkers can just open it.

A common point of confusion: **a Claude Pro (or ChatGPT Plus) subscription does
NOT include API access.** Those plans cover the chat apps only; calling a model
from code is billed separately. Gemini's free tier is the simplest way to run
real agents at no cost, which is why this project standardizes on it. There are
no paid APIs and no OpenAI dependency anywhere in this repo.

## Get a free Gemini key

1. Go to <https://aistudio.google.com/apikey>.
2. Sign in with a Google account and click **Create API key** (free, no card).
3. Make the key available to the scripts, either by exporting it:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```
   or by copying `.env.example` to `.env` and filling in the value. (`.env` is
   gitignored, so your key is never committed.)

The free tier has generous but real rate limits. The demos are written to stay
well inside them (the critic loop is capped at one revision).

## Run the demos

Set up a virtual environment and install the two dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
```

### 1. The CrewAI crew (the framework version)

```bash
python main.py "multi-agent AI systems"
```

Pass any topic as the argument (the default is "multi-agent AI systems"). CrewAI
runs the three agents in sequence, wiring each task's output into the next with
`context=[...]`, and prints the critic's final article.

### 2. The framework-free version (what CrewAI hides)

```bash
python handoff_demo.py "multi-agent AI systems"
```

Same researcher -> writer -> critic flow, but built from plain Python functions
that call Gemini directly. Read this alongside `main.py` to see that a "handoff"
is nothing more than one function's output becoming the next function's input,
and that the critic loop is just an `if` statement.

## Open the interactive page

No server, no build, no install:

```bash
open index.html          # macOS
# or: xdg-open index.html (Linux), or just double-click the file
```

It has four sections: a plain-language intro, a clickable diagram of the agent
flow (with the critic's feedback loop), a step-by-step simulated run of the crew
on a sample request, and a glossary. It works offline and supports light and
dark themes.

## How this maps to the article

`ARTICLE.md` lays out the general pattern: why one agent is not enough, the
orchestrator-and-specialist design, the common roles (orchestrator, researcher,
worker, critic, tool agent), the 2026 framework landscape (CrewAI, LangGraph,
AutoGen / Microsoft Agent Framework, OpenAI Agents SDK), the two key protocols
(MCP for the tool layer, A2A for the agent layer), and the main risks
(hallucination cascade, prompt injection between agents, cost and latency). This
repository is the article's closing "worked example": `main.py` is the
orchestrator-and-specialists pattern in code, `handoff_demo.py` strips it down to
its essentials, and `index.html` lets anyone see it without writing a line.

## Files

```
.
├── main.py            # CrewAI crew: 3 agents, 3 context-wired tasks (Gemini)
├── handoff_demo.py    # same flow, no framework, direct Gemini calls
├── requirements.txt   # crewai, google-generativeai
├── ARTICLE.md         # ~900-word research article
├── index.html         # self-contained interactive explainer (no setup)
├── README.md          # you are here
├── .env.example       # template for GEMINI_API_KEY
└── .gitignore         # Python + secrets
```

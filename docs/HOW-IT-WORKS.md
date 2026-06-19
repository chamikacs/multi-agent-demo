# How it works (a plain-language walkthrough)

This document explains the whole project in everyday language, with diagrams.
No prior coding knowledge needed.

---

## The one-sentence version

This project contains **two separate things** that teach the **same idea**:

1. a **Python program** that really uses several AI "agents" to write an article, and
2. a **web page** that *explains and animates* that idea so non-technical
   colleagues can learn it with zero setup.

They are **not** wired together as one live system. The only thing passed between
them is a small data file (`content.json`). Details below.

---

## First: what is an "agent"?

An **agent** is just one AI model (here, Google's Gemini) that has been given **a
specific job and personality**. Instead of asking a single AI to "research, write,
and check an article" all at once, you create several AIs, each with one narrow
job, and pass the work down a line, like an assembly line or a small newsroom.

The four roles in this project:

| Agent | Its one job |
|-------|-------------|
| **Orchestrator** | The "manager." Decides the order of work and passes each result to the next agent. It is not a separate AI; it is the framework itself running the line. |
| **Researcher** | Gathers and organizes the facts. |
| **Writer** | Turns those facts into a readable article. |
| **Critic** | Checks the article. If it is weak, it **sends it back** to be redone. |

The **Critic sending work back** is the heart of the idea: a second AI that did
not write the draft is far better at spotting its flaws than the AI that wrote it.
That feedback loop is what makes a team of agents better than one lone agent.

---

## The two Python files (and why there are two)

### `main.py` — the real thing, using a framework called CrewAI

This is the file that **actually generates an article with multiple agents**. When
you run it:

1. You give it a topic, for example "multi-agent AI platforms".
2. The Researcher, Writer, and Critic agents run in order, each handing its
   output to the next.
3. The Critic produces the final, polished article, which is **printed in your
   terminal**.
4. A fourth agent, the **Curriculum Designer**, turns the lesson into a data file
   (`content.json`) that the web page can read.

"CrewAI" is a **framework**: a pre-built toolkit that hides the boring plumbing.
You describe *who* the agents are and *what* the tasks are, and CrewAI handles
talking to Gemini, ordering the steps, and passing results along.

### `handoff_demo.py` — the same idea, with the magic removed

This file does the **exact same Researcher to Writer to Critic flow**, but
**without CrewAI**: just plain Python and direct calls to Gemini.

Why does it exist? Because frameworks can feel like magic, and magic is hard to
teach. This file proves there is no magic: an "agent" is just a prompt, and a
"handoff" is literally **one function's output becoming the next function's
input**. When a colleague asks "but what is CrewAI actually doing?", open this
file and show them.

> Think of it like this: `main.py` is driving an automatic car. `handoff_demo.py`
> is the same trip in a manual car, so you can see the gears change.

Both files print a freshly written article every time you run them.

### `ARTICLE.md` — the hand-written reference (kept as-is)

`ARTICLE.md` is a carefully **hand-written ~900-word reference article** about
multi-agent systems. It is **separate** from the articles the Python files
generate. So you have:

- **`ARTICLE.md`** — the polished, reliable reference you can hand to anyone.
- **The article `main.py` prints** — a fresh one written by the AI agents each
  run. Great for live demos, but it varies between runs and can contain small
  inaccuracies. That is normal for AI-generated text.

---

## The big question: does the web page call the Python code?

**No. The web page never runs Python and never calls any AI.** This is deliberate
and important.

The reason: anyone should be able to **double-click one file and learn**,
with no installing Python, no API key, no internet or AI costs, and no risk of
anything breaking.

So the "run the crew" button in the page is a **scripted animation**, like a
slideshow that reveals pre-written steps one at a time with realistic pauses. It
*looks* like agents working, but it is just JavaScript timers showing text in
sequence. It teaches the *flow* without needing the real engine.

### What the web page actually does (its four sections)

1. **Intro** — plain-language explanation of what a multi-agent system is.
2. **Clickable diagram** — the Orchestrator to Researcher to Writer to Critic
   flow, with the Critic's "send it back" loop. Clicking any agent shows its role,
   goal, and a plain description.
3. **"Run the crew" simulation** — a button that steps through a fake request
   ("research SaaS pricing...") one agent at a time, including one Critic
   rejection and redo, ending in a final answer. Pure animation, no AI.
4. **Glossary** — the key terms (orchestrator, agent, tool, MCP, A2A, handoff).

### The one connection: `content.json`

The **words** shown in the diagram, simulation, and glossary are not hard-coded;
they are loaded from `content.json`, **which the Python crew wrote** (the
Curriculum Designer agent). This is the only link between the two worlds, and it
is just **data**, not a live function call:

- If you **serve the page** with a tiny local web server, it loads the
  crew-written `content.json`.
- If someone just **double-clicks** the file, browsers block reading local
  files for security, so the page falls back to an **identical copy baked inside
  it**. Either way the page always works.

---

## Diagram 1: what happens inside `main.py` (the real agents)

```
        You type a topic  -->  e.g. "multi-agent AI platforms"
                 |
                 v
   +-----------------------------------------------+
   |  ORCHESTRATOR  (the CrewAI "crew")            |   runs the steps in order
   |  decides who works when, carries the results  |   and hands each output on
   +-----------------------------------------------+
                 |
                 v
        1) RESEARCHER   -- finds & organizes the facts
                 |  (hands the brief to...)
                 v
        2) WRITER       -- turns facts into an article draft
                 |  (hands the draft to...)
                 v
        3) CRITIC       -- checks it against the facts
                 |              |
                 |   not good?  +--> "send it back" --> redo (Researcher/Writer)
                 |   good?
                 v
        4) CURRICULUM DESIGNER -- turns the lesson into teaching data
                 |
                 v
   +---------------------------+      +-------------------------+
   | prints the FINAL ARTICLE  |      | writes content.json     |
   | in your terminal          |      | (text for the web page) |
   +---------------------------+      +-------------------------+
```

## Diagram 2: how all the pieces fit together

```
  PYTHON SIDE - for YOU (needs an API key)        BROWSER SIDE - for COLLEAGUES (no setup)
  ========================================        ========================================

   main.py -- runs 4 real AI agents
      |
      |--> prints a fresh article  --> your terminal
      |
      +--> writes --> content.json --------read by-------> index.html  (one self-contained file)
                       (data only,                            |
                        not a function call)                  |-- intro
                                                              |-- clickable agent diagram
   handoff_demo.py -- same flow, no framework                 |-- "run the crew" animation
      |                                                       |   (FAKE: pure JavaScript,
      +--> prints a fresh article --> your terminal           |    no AI, no Python)
                                                              +-- glossary
   ARTICLE.md -- hand-written reference article               |
                 (kept as-is, stands alone)               double-click works too, using a
                                                          built-in fallback copy of the text
```

The key takeaway: **the left side is the real engine** (it costs quota and
needs setup); **the right side is a safe, free explainer**. They share an idea
and a data file, nothing more.

---

## Suggested walkthrough (3 steps)

1. **Look at the picture** (Diagram 1): one AI doing everything is sloppy; a
   team with a critic is better.
2. **Open `index.html`** and click "run the crew" to watch the handoff and a
   Critic rejection happen. No setup, instant understanding.
3. **For the curious**, run `python main.py "a topic"` to see real agents write
   a real article, then open `handoff_demo.py` to see there is no magic
   underneath.

---

## Quick glossary

- **Agent** — one AI with a defined role and goal.
- **Orchestrator** — the manager that runs the agents in order and passes results.
- **Handoff** — one agent's output becoming the next agent's input.
- **Framework (CrewAI)** — a toolkit that handles the plumbing of running agents.
- **API key** — a password that lets the code use Google's Gemini. It is personal
  and is kept out of the shared code (in a gitignored `.env` file).
- **content.json** — the teaching text the crew writes for the web page.
- **MCP / A2A** — open standards for connecting agents to tools (MCP) and to other
  agents (A2A). See `ARTICLE.md` for detail.

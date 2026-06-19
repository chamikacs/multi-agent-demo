# Multi-agent platforms: how teams of AI agents get real work done

## Why one agent is not enough

A large language model on its own is a capable generalist. Ask it to research a
topic, write an article, and check its own work, and it will cheerfully do all
three in a single pass. The problem is that it does them all *at once*, with no
separation of concerns. It rarely catches its own mistakes, because the same
reasoning that produced an error is unlikely to flag it a moment later. Long,
multi-step jobs also overflow a single prompt: instructions get lost, context
windows fill with noise, and quality degrades.

A *multi-agent system* addresses this by splitting one big job into several
specialized agents that pass work between them. Each agent is still a language
model, but it is given a narrow role, a clear goal, and only the context it
needs. The gains are the same ones we get from human teams: division of labour,
independent review, and the ability to assemble specialists who are individually
better than any generalist. The cost is coordination, which is exactly what a
multi-agent *platform* is built to manage.

## The orchestrator and specialist pattern

The dominant design is simple: one **orchestrator** decides what happens and in
what order, and a set of **specialists** each do one thing well. The
orchestrator decomposes the request, routes each sub-task to the right agent,
carries results from one step to the next, and decides when the work is done.
Specialists never need to know about the whole pipeline; they only need their
input and their instructions.

Common roles recur across almost every serious system:

- **Orchestrator** (also called planner, manager, or supervisor): owns the
  workflow and the control flow, including loops and retries.
- **Researcher**: gathers and organizes raw information, often using tools.
- **Worker / writer**: transforms inputs into the desired output, such as prose,
  code, or a structured answer.
- **Critic / reviewer**: independently checks the worker's output and can send it
  back for revision. This is the single most valuable role, because a fresh set
  of (model) eyes that was not invested in producing the draft is far more
  willing to find fault.
- **Tool agent**: a specialist whose job is to operate an external system, such
  as a database, a search API, or a code runner, and return clean results.

The critic's feedback loop is what separates a real system from a glorified
prompt chain. When the critic can reject work and force another round, quality
rises sharply, at the price of more time and more tokens.

## The 2026 framework landscape

Several frameworks now compete to make this pattern easy to build:

- **CrewAI** models work as a "crew" of role-based agents running sequential or
  hierarchical processes. It is the fastest way to get a readable, opinionated
  multi-agent pipeline running, which is why this project uses it.
- **LangGraph** (from the LangChain team) represents agent workflows as an
  explicit graph of nodes and edges with shared state. It trades some simplicity
  for fine-grained control over loops, branching, and persistence, making it a
  favourite for complex, production-grade flows.
- **AutoGen**, Microsoft's research framework, popularized conversational
  multi-agent patterns. Its ideas are now converging into the **Microsoft Agent
  Framework**, a unified, enterprise-oriented offering.
- **OpenAI Agents SDK** is a lightweight, code-first toolkit centred on agents,
  tools, and explicit *handoffs* between agents, with tracing built in.

The frameworks differ in style more than in substance. All of them implement the
same underlying idea: agents with roles, a way to pass work between them, and a
controller that decides the order.

## The two protocols that matter: MCP and A2A

As systems grow, two open protocols are becoming the connective tissue.

- **MCP (Model Context Protocol)** standardizes the **tool layer**: how an agent
  discovers and calls external tools and data sources. Instead of writing a
  bespoke integration for every database or API, you expose an MCP server once,
  and any MCP-aware agent can use it. Think of MCP as a universal adapter between
  agents and the outside world.
- **A2A (Agent-to-Agent)** standardizes the **agent layer**: how independent
  agents, possibly built by different teams on different frameworks, discover
  each other's capabilities and delegate tasks. If MCP connects an agent to its
  tools, A2A connects an agent to its colleagues.

Together they point toward an ecosystem where agents and tools interoperate
across vendor and framework boundaries, rather than living in isolated silos.

## The risks worth naming

Multi-agent systems inherit every risk of a single model and add some of their
own:

- **Hallucination cascade**: if the researcher invents a fact, the writer treats
  it as true and the critic may rubber-stamp it. One early error propagates and
  is amplified downstream. Giving the critic access to the *original source
  material*, not just the draft, is a key defense.
- **Prompt injection between agents**: if one agent ingests untrusted content
  (a web page, an email), hidden instructions in that content can hijack it and
  then flow to other agents as "trusted" internal messages. Treat inter-agent
  messages with the same suspicion as external input.
- **Cost and latency**: every agent turn is another model call. A four-agent
  pipeline with a feedback loop can easily make ten calls for one request, which
  multiplies both the bill and the wait. Capping retries and choosing fast,
  cheap models for routine steps are standard mitigations.

## This project as a worked example

This repository is a deliberately small instance of the pattern. An
**orchestrator** (CrewAI's sequential `Crew`) delegates to a **Senior Research
Analyst**, a **Technical Writer**, and an **Editorial Critic**. Each task is
wired to the previous one with `context=[...]`, so the researcher's brief flows
to the writer and both flow to the critic, who fact-checks the draft against the
brief and can send it back for one revision. A second script,
`handoff_demo.py`, rebuilds the identical flow with plain Python functions and
direct Gemini calls, exposing what the framework abstracts away: a handoff is
nothing more than one agent's output becoming the next agent's input. The
companion `index.html` lets non-technical readers click through the same
architecture and watch a simulated run, feedback loop included. The whole thing
runs on Google's Gemini free tier, so the lesson costs nothing to try.

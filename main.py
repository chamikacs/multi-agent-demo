"""
main.py - A runnable multi-agent "crew" built with CrewAI.

THE STORY THIS CODE TELLS
-------------------------
A single language-model call is a smart generalist with no process. For any
non-trivial task it tends to do everything in one breath: research, write, and
judge its own work all at once. The result is usually shallow and self-
flattering, because the model rarely catches its own mistakes.

A *multi-agent system* splits that one job into specialists that hand work to
each other, exactly like a small newsroom:

    Orchestrator  ->  Researcher  ->  Writer  ->  Critic
                                         ^            |
                                         |____________|
                                      "send it back"

  * Orchestrator - decides the order of work and passes outputs along.
                   In CrewAI this is the Crew + Process itself, not a separate
                   agent you write by hand.
  * Researcher   - gathers and organizes the raw facts.
  * Writer       - turns those facts into a clean article.
  * Critic       - checks the draft and can demand revisions.

CrewAI hides the plumbing. You describe WHO the agents are (role / goal /
backstory) and WHAT the tasks are, then wire the tasks together with
`context=[...]`. The framework handles the prompting, the ordering, and the
passing of each result into the next step. The handoff_demo.py file in this
repo does the same thing by hand so you can see what CrewAI abstracts away.

HOW TO RUN
----------
    pip install -r requirements.txt
    export GEMINI_API_KEY="your-key"     # the link is in the error below
    python main.py "your research topic"
"""

import os
import sys

# CrewAI's public building blocks. `LLM` is CrewAI's thin wrapper around
# litellm, which is what lets us point at Google Gemini instead of OpenAI.
from crewai import Agent, Task, Crew, Process, LLM


def build_llm() -> LLM:
    """Create the shared language model that every agent will use.

    We use Google's Gemini *free tier*. CrewAI talks to it through litellm, and
    the model id `gemini/gemini-2.0-flash` is the signal that routes the call to
    Google rather than to OpenAI. The API key is read from the environment so no
    secret ever lives in the source code.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Fail loudly and helpfully. A confusing auth error three layers deep in
        # litellm is the most common thing that trips up first-time learners.
        sys.exit(
            "\nERROR: GEMINI_API_KEY is not set.\n"
            "\nThis project runs for FREE on Google's Gemini free tier.\n"
            "  1. Get a key (free, no credit card): https://aistudio.google.com/apikey\n"
            "  2. Then run:  export GEMINI_API_KEY=\"your-key-here\"\n"
            "  3. Re-run:    python main.py \"your topic\"\n"
        )
    # temperature is kept modest so the researcher stays factual; the writer and
    # critic inherit the same model. You could give each agent its own LLM with
    # different settings, which is a common real-world tuning step.
    return LLM(model="gemini/gemini-2.0-flash", api_key=api_key, temperature=0.4)


def build_agents(llm: LLM):
    """Define the three specialists.

    An Agent in CrewAI is essentially a *persona plus a job description*. The
    role/goal/backstory fields are not decoration - they are injected into the
    system prompt and genuinely change how the model behaves. A good backstory
    is the cheapest quality lever you have.
    """

    # --- The Researcher -----------------------------------------------------
    # First specialist in the chain. Its only job is to produce organized,
    # trustworthy raw material. It does NOT write prose for the reader.
    researcher = Agent(
        role="Senior Research Analyst",
        goal=(
            "Find and organize the most important, accurate facts about the "
            "given topic so a writer can turn them into an article."
        ),
        backstory=(
            "You are a meticulous analyst who has spent years separating signal "
            "from hype. You produce tight, well-structured briefs: key points, "
            "context, and any caveats. You never pad and you flag uncertainty."
        ),
        llm=llm,
        # allow_delegation=False keeps each agent in its lane. Turning it on lets
        # an agent ask teammates for help, which is powerful but harder to reason
        # about for a first example.
        allow_delegation=False,
        verbose=True,
    )

    # --- The Writer ---------------------------------------------------------
    # Second in the chain. It consumes the researcher's brief (via task context,
    # wired below) and shapes it into something a human enjoys reading.
    writer = Agent(
        role="Technical Writer",
        goal=(
            "Turn the research brief into a clear, engaging, well-structured "
            "article for a smart but non-expert reader."
        ),
        backstory=(
            "You are a writer who makes complex topics feel simple without "
            "dumbing them down. You favor plain language, concrete examples, and "
            "a logical flow from idea to idea. You write only from the facts you "
            "are given - you do not invent details."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    # --- The Critic ---------------------------------------------------------
    # Third in the chain. This is the agent that makes multi-agent systems worth
    # the extra cost: a *separate* set of eyes that was not invested in writing
    # the draft, so it is far more willing to find fault.
    critic = Agent(
        role="Editorial Critic",
        goal=(
            "Rigorously review the draft for accuracy, clarity, and structure, "
            "then return a polished final version - or send it back with specific "
            "fixes if it is not good enough."
        ),
        backstory=(
            "You are a demanding editor. You check claims against the research "
            "brief, hunt for vague sentences, and refuse to let weak writing "
            "ship. When the draft is close, you fix it yourself; when it is not, "
            "you say exactly what must change and why."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    return researcher, writer, critic


def build_tasks(topic: str, researcher: Agent, writer: Agent, critic: Agent):
    """Define the work and, crucially, how the work HANDS OFF.

    The single most important idea here is `context=[...]`. It is the wiring that
    turns three separate agents into a pipeline: the output of one task is fed in
    as background for the next. This is the "handoff" - the same baton-passing
    that handoff_demo.py does manually with f-strings.
    """

    # STEP 1: research. No context, because this is the start of the chain.
    research_task = Task(
        description=(
            f"Research the topic: '{topic}'.\n"
            "Produce a structured brief with 5-8 key points. For each point give "
            "one or two sentences of explanation. Note any important caveats or "
            "areas of disagreement. Keep it factual and organized, not prose."
        ),
        expected_output=(
            "A bulleted research brief of 5-8 key points with short explanations "
            "and any caveats."
        ),
        agent=researcher,
    )

    # STEP 2: write. THE HANDOFF: context=[research_task] means the writer
    # receives the researcher's brief automatically. The writer never has to ask
    # for it - the orchestrator delivers it.
    writing_task = Task(
        description=(
            "Using ONLY the research brief provided to you, write a clear, "
            "engaging article of about 400-500 words for a smart non-expert. "
            "Give it a title, a short intro, a few body sections, and a brief "
            "conclusion. Do not invent facts that are not in the brief."
        ),
        expected_output="A well-structured ~400-500 word article in Markdown.",
        agent=writer,
        context=[research_task],  # <-- handoff: researcher -> writer
    )

    # STEP 3: critique + finalize. THE SECOND HANDOFF plus the FEEDBACK LOOP.
    # The critic sees BOTH the original brief and the draft (context has two
    # items), so it can fact-check the draft against the source material - the
    # core defense against a "hallucination cascade" where one agent's mistake
    # gets amplified downstream.
    #
    # ABOUT THE "SEND IT BACK" LOOP:
    # In this sequential crew the loop is logical, not a literal re-run: we
    # instruct the critic to internally decide "is this good enough?" and, if
    # not, to revise it itself before returning the final version. To make the
    # loop *automatic* (writer actually re-runs on rejection) you would switch
    # the crew to `Process.hierarchical` with a manager agent, or build an
    # explicit loop in code as handoff_demo.py shows. We keep it sequential here
    # because it is the clearest possible first example.
    critique_task = Task(
        description=(
            "Review the draft article against the original research brief.\n"
            "1. Check every claim in the draft against the brief. Flag anything "
            "unsupported.\n"
            "2. Judge clarity, structure, and flow.\n"
            "3. Decide: is this good enough to publish?\n"
            "   - If NO: explain the specific problems, then rewrite the article "
            "to fix them yourself (this is the 'send it back and improve' loop).\n"
            "   - If YES: lightly polish it.\n"
            "Return only the final, publication-ready article."
        ),
        expected_output="The final, polished, publication-ready article in Markdown.",
        agent=critic,
        context=[research_task, writing_task],  # <-- sees brief AND draft
    )

    return research_task, writing_task, critique_task


def main() -> None:
    # The topic comes from the command line; everything after the script name is
    # joined so quoting is optional. Falls back to a sensible default.
    topic = " ".join(sys.argv[1:]).strip() or "multi-agent AI systems"

    print(f"\n=== Multi-agent crew starting on topic: {topic!r} ===\n")

    llm = build_llm()
    researcher, writer, critic = build_agents(llm)
    research_task, writing_task, critique_task = build_tasks(
        topic, researcher, writer, critic
    )

    # The Crew is the ORCHESTRATOR. `Process.sequential` means: run the tasks in
    # order, and (because we wired context=[...]) feed each result forward. The
    # crew is what turns a pile of agents and tasks into a working assembly line.
    crew = Crew(
        agents=[researcher, writer, critic],
        tasks=[research_task, writing_task, critique_task],
        process=Process.sequential,
        verbose=True,
    )

    # kickoff() runs the whole pipeline and returns the LAST task's output -
    # here, the critic's final, polished article.
    result = crew.kickoff()

    print("\n\n========== FINAL ARTICLE ==========\n")
    print(result)
    print("\n===================================\n")


if __name__ == "__main__":
    main()

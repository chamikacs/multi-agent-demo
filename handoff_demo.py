"""
handoff_demo.py - The SAME Researcher -> Writer -> Critic flow, but with NO
framework. Just plain Python functions calling Gemini directly.

WHY THIS FILE EXISTS
--------------------
CrewAI (see main.py) is convenient, but convenience hides what is really going
on. Underneath, a multi-agent system is not magic - it is:

  1. several prompts, each giving the model a different ROLE,
  2. plain variables passing one model's OUTPUT into the next model's INPUT
     (this passing is the entire "handoff"),
  3. a little bit of CONTROL FLOW - in particular an `if` that lets the critic
     send the work back for one more round.

That is the whole trick. Read this file and CrewAI stops feeling mysterious:
its Agents are these prompts, its `context=[...]` wiring is these function
arguments, and its orchestration is this `main()` function.

HOW TO RUN
----------
    pip install -r requirements.txt
    export GEMINI_API_KEY="your-key"     # link is in the error message below
    python handoff_demo.py "your topic"
"""

import os
import sys

import google.generativeai as genai


MODEL_NAME = "gemini-2.0-flash"  # the free-tier model we use everywhere


def configure() -> None:
    """Read the key from the environment and configure the Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "\nERROR: GEMINI_API_KEY is not set.\n"
            "\nThis project runs for FREE on Google's Gemini free tier.\n"
            "  1. Get a key (free, no credit card): https://aistudio.google.com/apikey\n"
            "  2. Then run:  export GEMINI_API_KEY=\"your-key-here\"\n"
        )
    genai.configure(api_key=api_key)


def ask_gemini(system_role: str, user_prompt: str) -> str:
    """One call to the model = one 'agent turn'.

    There is no Agent class here. An 'agent' is simply: a system instruction
    that defines a persona, plus the prompt we hand it. `system_instruction` is
    Gemini's equivalent of CrewAI's role/goal/backstory.
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_role,
    )
    response = model.generate_content(user_prompt)
    return response.text.strip()


# --- The three "agents", as plain functions ---------------------------------
# Notice the shape: each takes the previous step's text as a normal argument and
# returns text. THAT is the handoff. No framework required.


def researcher(topic: str) -> str:
    """Agent 1: gather organized facts. Start of the chain, so no input but the
    topic itself."""
    print("\n[1/3] Researcher is gathering facts...")
    role = (
        "You are a Senior Research Analyst. You produce tight, well-structured "
        "research briefs: key points with short explanations and any caveats. "
        "You never pad and you flag uncertainty. You do not write prose."
    )
    prompt = (
        f"Research this topic: '{topic}'. Produce a bulleted brief of 5-8 key "
        "points. Give one or two sentences per point and note any caveats."
    )
    return ask_gemini(role, prompt)


def writer(topic: str, brief: str) -> str:
    """Agent 2: turn the brief into an article. THE HANDOFF: the researcher's
    `brief` is passed straight in as a string. This is exactly what CrewAI's
    `context=[research_task]` does for you behind the scenes."""
    print("[2/3] Writer is drafting the article...")
    role = (
        "You are a Technical Writer. You turn research into clear, engaging "
        "articles for smart non-experts. You write ONLY from the facts you are "
        "given and never invent details."
    )
    prompt = (
        f"Topic: {topic}\n\n"
        f"Here is the research brief to work from:\n\n{brief}\n\n"
        "Write a ~400-500 word article with a title, a short intro, a few body "
        "sections, and a brief conclusion. Use only facts from the brief."
    )
    return ask_gemini(role, prompt)


def critic(brief: str, draft: str) -> tuple[bool, str]:
    """Agent 3: review the draft AGAINST the brief.

    It receives two handoffs (brief AND draft) so it can fact-check - the same
    defense main.py's critic gets from `context=[research_task, writing_task]`.

    Returns (approved, text). If not approved, `text` is the critic's required
    fixes, which we feed back to the writer. This return value is the seed of
    the feedback loop.
    """
    print("[3/3] Critic is reviewing the draft...")
    role = (
        "You are a demanding Editorial Critic. You check claims against the "
        "research brief, hunt for vague writing, and refuse to let weak drafts "
        "ship."
    )
    prompt = (
        f"RESEARCH BRIEF:\n{brief}\n\n"
        f"DRAFT ARTICLE:\n{draft}\n\n"
        "Review the draft against the brief. If it is accurate, clear, and "
        "well-structured, reply with exactly 'APPROVED' on the first line and "
        "nothing else. If it needs work, reply with 'REVISE' on the first line, "
        "then a numbered list of the specific, concrete fixes required."
    )
    verdict = ask_gemini(role, prompt)
    approved = verdict.strip().upper().startswith("APPROVED")
    return approved, verdict


def main() -> None:
    topic = " ".join(sys.argv[1:]).strip() or "multi-agent AI systems"
    configure()

    print(f"\n=== Manual handoff pipeline on topic: {topic!r} ===")

    # ORCHESTRATION, by hand. This function plays the role CrewAI's Crew plays:
    # it decides the order and carries the baton from one agent to the next.

    # Step 1 -> Step 2: research, then write.
    brief = researcher(topic)
    draft = writer(topic, brief)

    # Step 3 + THE FEEDBACK LOOP. The critic can "send it back". We allow up to
    # one revision round so the demo always terminates (and stays inside free-
    # tier limits). A production system would cap retries the same way - an
    # unbounded loop is both a cost risk and a latency risk.
    approved, feedback = critic(brief, draft)

    if not approved:
        print("\n--> Critic sent it back. Writer is revising once...\n")
        # The handoff back: we hand the writer its own draft PLUS the critic's
        # feedback so it can fix the specific problems.
        revision_prompt_brief = (
            f"{brief}\n\nEDITOR FEEDBACK TO ADDRESS:\n{feedback}\n\n"
            f"PREVIOUS DRAFT TO IMPROVE:\n{draft}"
        )
        draft = writer(topic, revision_prompt_brief)
    else:
        print("\n--> Critic approved the first draft.\n")

    print("\n========== FINAL ARTICLE ==========\n")
    print(draft)
    print("\n===================================\n")


if __name__ == "__main__":
    main()

"""
02 - Pipeline of Agents

A sequential pipeline of three specialized agents, each a separate Claude
call: a research agent gathers key points, a writer agent turns them into a
short article, and a reviewer agent critiques the draft.

Each stage's output becomes the next stage's input - your code is the
"pipe" connecting them. This is the simplest multi-agent pattern: no
parallelism, no shared state beyond what's explicitly passed along.
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

TOPIC = "Why retrieval-augmented generation (RAG) helps reduce LLM hallucinations"


def run_research_agent(client: Anthropic, topic: str) -> str:
    system_prompt = (
        "You are a research assistant. Given a topic, produce 4-6 concise "
        "bullet points covering the key facts and arguments someone would "
        "need to write a short article about it. Do not write prose - "
        "bullet points only."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Topic: {topic}"}],
    )
    return response.content[0].text


def run_writer_agent(client: Anthropic, topic: str, research_notes: str) -> str:
    system_prompt = (
        "You are a technical writer. Given a topic and a set of research "
        "notes (bullet points), write a short article (3 short paragraphs) "
        "for a software engineering audience. Use the research notes as your "
        "source material - do not introduce facts that aren't in the notes."
    )
    user_content = f"Topic: {topic}\n\nResearch notes:\n{research_notes}"
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def run_reviewer_agent(client: Anthropic, draft: str) -> str:
    system_prompt = (
        "You are an editor reviewing a draft article. Check for: 1) claims "
        "that seem unsupported or overly strong, 2) unclear or jargon-heavy "
        "sentences, 3) anything missing that a reader would expect. Respond "
        "with a short bulleted list of specific feedback - do not rewrite "
        "the article yourself."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Draft article:\n\n{draft}"}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Stage 1: Research agent ===")
    research_notes = run_research_agent(client, TOPIC)
    print(research_notes)

    print("\n=== Stage 2: Writer agent ===")
    draft = run_writer_agent(client, TOPIC, research_notes)
    print(draft)

    print("\n=== Stage 3: Reviewer agent ===")
    feedback = run_reviewer_agent(client, draft)
    print(feedback)


if __name__ == "__main__":
    main()

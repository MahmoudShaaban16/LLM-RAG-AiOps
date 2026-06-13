"""
Exercise 2: Make the pipeline stages structured

TODO:
  1. Change run_research_agent to use a tool schema (RESEARCH_SCHEMA below)
     so it returns {"key_points": [...], "recommended_tone": "..."} instead
     of free text.
  2. Update run_writer_agent to take this structured dict as input and use
     `recommended_tone` to adjust its instructions.
  3. Run the pipeline and compare to the free-text version.
"""

import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

TOPIC = "Why retrieval-augmented generation (RAG) helps reduce LLM hallucinations"

# TODO: use this schema with tool_choice to force structured research output.
RESEARCH_SCHEMA = {
    "name": "research_notes",
    "description": "Structured research notes for writing a short article.",
    "input_schema": {
        "type": "object",
        "properties": {
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "4-6 concise bullet points covering key facts/arguments.",
            },
            "recommended_tone": {
                "type": "string",
                "enum": ["technical", "accessible"],
                "description": "Suggested tone for the article based on the topic.",
            },
        },
        "required": ["key_points", "recommended_tone"],
    },
}


def run_research_agent(client: Anthropic, topic: str) -> str:
    """Current (free-text) version. TODO: rewrite to use RESEARCH_SCHEMA and
    return a dict instead of a string."""
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
    """TODO: update the signature to accept the structured dict from
    run_research_agent and use `recommended_tone` to adjust the prompt."""
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


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Stage 1: Research agent ===")
    research_notes = run_research_agent(client, TOPIC)
    print(research_notes)

    print("\n=== Stage 2: Writer agent ===")
    draft = run_writer_agent(client, TOPIC, research_notes)
    print(draft)


if __name__ == "__main__":
    main()

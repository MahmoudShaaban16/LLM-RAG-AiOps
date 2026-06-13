"""
Solution: Exercise 2 - Make the pipeline stages structured
"""

import os

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

TOPIC = "Why retrieval-augmented generation (RAG) helps reduce LLM hallucinations"

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


def run_research_agent(client: Anthropic, topic: str) -> dict:
    system_prompt = (
        "You are a research assistant. Given a topic, produce structured "
        "research notes: 4-6 concise key points covering the key facts and "
        "arguments someone would need to write a short article, plus a "
        "recommended tone ('technical' for an audience that wants "
        "implementation detail, 'accessible' for a broader audience)."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system_prompt,
        tools=[RESEARCH_SCHEMA],
        tool_choice={"type": "tool", "name": "research_notes"},
        messages=[{"role": "user", "content": f"Topic: {topic}"}],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "research_notes":
            return block.input
    return {"key_points": [], "recommended_tone": "accessible"}


def run_writer_agent(client: Anthropic, topic: str, research: dict) -> str:
    tone = research.get("recommended_tone", "accessible")
    key_points = research.get("key_points", [])

    tone_instructions = {
        "technical": (
            "Write for a software engineering audience - you may use "
            "technical terms (e.g., embeddings, retrieval, context window) "
            "without defining them."
        ),
        "accessible": (
            "Write for a general audience - briefly explain any technical "
            "terms you use."
        ),
    }

    system_prompt = (
        "You are a technical writer. Given a topic and a list of key "
        "points, write a short article (3 short paragraphs). Use the key "
        "points as your source material - do not introduce facts that "
        "aren't in them. " + tone_instructions.get(tone, "")
    )

    points_text = "\n".join(f"- {point}" for point in key_points)
    user_content = f"Topic: {topic}\n\nKey points:\n{points_text}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("=== Stage 1: Research agent (structured) ===")
    research = run_research_agent(client, TOPIC)
    print(f"recommended_tone: {research['recommended_tone']}")
    for point in research["key_points"]:
        print(f"- {point}")

    print("\n=== Stage 2: Writer agent ===")
    draft = run_writer_agent(client, TOPIC, research)
    print(draft)

    # Discussion:
    # - Forcing a tool call guarantees the writer agent always receives a
    #   list of strings and a known tone value - no parsing of prose, no
    #   "what if the bullet points are formatted differently this time"
    #   variance.
    # - The tradeoff: the research agent is now constrained to this exact
    #   schema, which can occasionally feel restrictive (e.g., if a key
    #   point doesn't fit neatly as one string). For most pipeline handoffs,
    #   this constraint is worth it - it's the same tradeoff as Module 01's
    #   structured-output example: predictability over flexibility.
    # - If the research agent's free-text output were "good enough" and
    #   consistent in practice, the extra tool-call step adds a small amount
    #   of overhead for limited benefit - structured handoffs pay off most
    #   when downstream stages need to branch on specific fields (like
    #   `recommended_tone` here).


if __name__ == "__main__":
    main()

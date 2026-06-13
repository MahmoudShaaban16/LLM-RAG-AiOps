"""
Query a vLLM server's OpenAI-compatible API.

vLLM's `vllm serve <model>` command (see 01_start_vllm_server.md) exposes an
OpenAI-compatible /v1/chat/completions endpoint. This script shows how to
call it with the `openai` Python client by pointing `base_url` at the local
server - no Anthropic API key involved, since this is talking to a model you
are hosting yourself.

Requires a running vLLM server (or any other OpenAI-compatible local server,
e.g. Ollama's OpenAI-compatible endpoint) - this script will fail to connect
if nothing is listening on VLLM_BASE_URL.
"""

import os

from openai import OpenAI

VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
MODEL = os.environ.get("VLLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")


def main() -> None:
    client = OpenAI(base_url=VLLM_BASE_URL, api_key="not-needed")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "In one sentence, what is PagedAttention?"},
        ],
    )

    print(response.choices[0].message.content)

    # vLLM's OpenAI-compatible server also reports token usage, the same
    # shape as the OpenAI API - useful for the cost comparison in
    # 03_cost_comparison.py.
    print("\n--- usage ---")
    print(response.usage)


if __name__ == "__main__":
    main()

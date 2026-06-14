"""
03 - Chat with a GitHub Repo

A small read-only agent that can answer questions about a public GitHub
repository by calling the GitHub REST API. Same agentic loop as
02_agentic_loop.py, but the tools hit a real (public, unauthenticated)
API instead of a hardcoded dict - a common "awesome-llm-apps" pattern.

Tools are intentionally read-only (Module 09's allow-list guardrail
would treat all of these as low-risk/auto-executable).
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 6
GITHUB_API = "https://api.github.com"

REPO_OWNER = "anthropics"
REPO_NAME = "anthropic-sdk-python"

GET_README_TOOL = {
    "name": "get_repo_readme",
    "description": "Get the README content for the repository.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
}

LIST_FILES_TOOL = {
    "name": "list_repo_files",
    "description": (
        "List files and directories at a given path in the repository. "
        "Use an empty string for the repository root."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path within the repo, e.g. 'src' or '' for root.",
            },
        },
        "required": ["path"],
    },
}

GET_FILE_TOOL = {
    "name": "get_file_contents",
    "description": "Get the text contents of a specific file in the repository.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path within the repo, e.g. 'README.md'.",
            },
        },
        "required": ["path"],
    },
}

SEARCH_ISSUES_TOOL = {
    "name": "search_issues",
    "description": "Search open and closed issues/pull requests in the repository by keyword.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Keywords to search for, e.g. 'rate limit'.",
            },
        },
        "required": ["query"],
    },
}

TOOLS = [GET_README_TOOL, LIST_FILES_TOOL, GET_FILE_TOOL, SEARCH_ISSUES_TOOL]


def _github_get(url: str, accept: str = "application/vnd.github+json") -> dict | str:
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "llm-rag-aiops-module03"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        return f"error: GitHub API returned HTTP {exc.code} for {url}"
    if accept == "application/vnd.github.raw":
        return body.decode("utf-8", errors="replace")
    return json.loads(body)


def get_repo_readme() -> str:
    result = _github_get(
        f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/readme",
        accept="application/vnd.github.raw",
    )
    if isinstance(result, str) and result.startswith("error:"):
        return result
    # Truncate - real READMEs can be huge relative to a context window.
    return result[:4000]


def list_repo_files(path: str) -> str:
    result = _github_get(f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}")
    if isinstance(result, str):
        return result
    entries = [f"{item['type']}: {item['path']}" for item in result]
    return "\n".join(entries)


def get_file_contents(path: str) -> str:
    result = _github_get(
        f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}",
        accept="application/vnd.github.raw",
    )
    if isinstance(result, str) and result.startswith("error:"):
        return result
    return result[:4000]


def search_issues(query: str) -> str:
    url = f"{GITHUB_API}/search/issues?q={urllib.parse.quote(query)}+repo:{REPO_OWNER}/{REPO_NAME}"
    result = _github_get(url)
    if isinstance(result, str):
        return result
    items = result.get("items", [])[:5]
    if not items:
        return f"No issues/PRs found for '{query}'."
    return "\n".join(f"#{item['number']} ({item['state']}): {item['title']}" for item in items)


def run_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool call to its implementation, returning a string result."""
    if name == "get_repo_readme":
        return get_repo_readme()
    if name == "list_repo_files":
        return list_repo_files(**tool_input)
    if name == "get_file_contents":
        return get_file_contents(**tool_input)
    if name == "search_issues":
        return search_issues(**tool_input)
    return f"Unknown tool: {name}"


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [
        {
            "role": "user",
            "content": (
                f"What is the {REPO_OWNER}/{REPO_NAME} repository about, and "
                "what's in its top-level directory structure?"
            ),
        }
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== Iteration {iteration} ===")

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"[text] {block.text.strip()}")
            elif block.type == "tool_use":
                print(f"[tool_use] {block.name}({json.dumps(block.input)})")

        if response.stop_reason != "tool_use":
            print("\n--- Final answer ---")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"[tool_result] {result[:200]}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"\nStopped after reaching MAX_ITERATIONS={MAX_ITERATIONS}.")


if __name__ == "__main__":
    main()

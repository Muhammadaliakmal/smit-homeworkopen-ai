"""
Part C - Global-level config.

Nothing on the Agent, nothing on the run - the whole SDK is redirected
at import time via set_default_openai_client(). Every Agent and every
Runner call in this process now talks to Gemini unless something more
specific (agent-level or run-level) overrides it.

Also flips the default API style, because the SDK defaults to OpenAI's
Responses API, which Gemini's OpenAI-compatible endpoint does not
implement - only Chat Completions.

    uv run config_global_level.py
"""

import os

from agents import Agent, Runner, set_default_openai_api, set_default_openai_client, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_default_openai_client(gemini_client)
set_default_openai_api("chat_completions")
set_tracing_disabled(True)

# No model= anywhere - this agent just inherits whatever the process-wide
# default client/model resolves to.
agent = Agent(
    name="Global-Level Config Agent",
    instructions="You are a concise assistant. Answer in one sentence.",
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "Name one moon of Mars.")
    print(result.final_output)

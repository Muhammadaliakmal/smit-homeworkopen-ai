"""
Part C - Agent-level config.

The model is baked directly into this one Agent's definition via
Agent(model=...). Every run of this specific agent uses this exact model,
no matter what RunConfig or global defaults say later.

    uv run config_agent_level.py
"""

import os

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
set_tracing_disabled(True)

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent = Agent(
    name="Agent-Level Config Agent",
    instructions="You are a concise assistant. Answer in one sentence.",
    model=OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        openai_client=gemini_client,
    ),
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "Name one moon of Jupiter.")
    print(result.final_output)

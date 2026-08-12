"""
Part F - fixed_agent.py

Repaired version of broken_agent.py. See evidence/bugs.md for the 6 bugs
found along the way (import typo, missing instructions= kwarg, sync/async
misuse, missing load_dotenv(), a dead model name, and a wrong result
attribute).

    uv run fixed_agent.py
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
    name="Fixed Agent",
    instructions="You are a concise assistant. Answer in one sentence.",
    model=OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        openai_client=gemini_client,
    ),
)


def main():
    result = Runner.run_sync(agent, "What is the capital of Japan?")
    print(result.final_output)


if __name__ == "__main__":
    main()

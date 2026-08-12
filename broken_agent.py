"""
Part F - Breakage Lab.

This file has 6 planted bugs. Run it with `uv run broken_agent.py`, fix
the first error you hit, rerun, and repeat until it works end to end.
Write each one up in evidence/bugs.md. Don't "fix" by deleting features -
every bug has a real one-line fix.
"""

import os

from agents import Agent, OpenAIChatCompletionModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

set_tracing_disabled(True)

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent = Agent(
    name="Broken Agent",
    instruction="You are a concise assistant. Answer in one sentence.",
    model=OpenAIChatCompletionModel(
        model="gemini-pro",
        openai_client=gemini_client,
    ),
)


async def main():
    result = Runner.run_sync(agent, "What is the capital of Japan?")
    print(result.output_text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

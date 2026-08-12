"""
Part C - Run-level config.

The Agent itself is defined with NO model at all. The model is decided
per-run, via RunConfig passed into Runner.run_sync(). The same agent
object could be run again elsewhere with a different RunConfig and use a
completely different model.

    uv run config_run_level.py
"""

import os

from agents import Agent, OpenAIChatCompletionsModel, RunConfig, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
set_tracing_disabled(True)

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# No model= here on purpose - this agent is provider-agnostic.
agent = Agent(
    name="Run-Level Config Agent",
    instructions="You are a concise assistant. Answer in one sentence.",
)

run_config = RunConfig(
    model=OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        openai_client=gemini_client,
    )
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "Name one moon of Saturn.", run_config=run_config)
    print(result.final_output)

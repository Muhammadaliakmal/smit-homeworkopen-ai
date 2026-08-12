"""
Part B - Your First Agent.

One Agent, running on Gemini through the OpenAI Agents SDK by pointing an
AsyncOpenAI client at Gemini's OpenAI-compatible endpoint. Run with:

    uv run hello_agent.py
"""

import os

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Gemini has no official trace ingestion endpoint, so the SDK's default
# "send traces to platform.openai.com" behaviour would just fail/warn.
set_tracing_disabled(True)

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent = Agent(
    name="Hello Agent",
    instructions="You are a concise assistant. Answer in at most two sentences.",
    model=OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        openai_client=gemini_client,
    ),
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "What is the capital of France?")
    print(result.final_output)

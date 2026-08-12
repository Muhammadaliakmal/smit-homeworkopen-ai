"""
Part E - Understanding the Runner.

Demonstrates all three ways to execute an Agent:
  1. Runner.run()          - async, awaited
  2. Runner.run_sync()     - blocking wrapper around Runner.run()
  3. Runner.run_streamed() - returns immediately, yields events as the
                              model produces them (token-by-token)

For each, prints final_output, last_agent.name, and len(new_items) so you
can see they all return the same shape of RunResult.

Each demo below builds its own Agent/AsyncOpenAI client instead of sharing
one module-level instance. That's not boilerplate for its own sake - a
shared AsyncOpenAI client hands its underlying httpx connection pool to
whichever asyncio event loop is running when it first makes a request.
run_sync() spins up its own internal loop; a second, separate
asyncio.run() afterwards starts a *different* loop. Reusing one client
across both deadlocks (the pool waits on a completion event tied to a
loop that's no longer running) - it doesn't error, it just hangs forever.
Giving each demo its own client sidesteps that entirely.

    uv run runner_lab.py
"""

import asyncio
import os

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()
set_tracing_disabled(True)


def build_agent() -> Agent:
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return Agent(
        name="Runner Lab Agent",
        instructions="You are a concise assistant. Answer in one or two sentences.",
        model=OpenAIChatCompletionsModel(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            openai_client=client,
        ),
    )


def summarize(label: str, result) -> None:
    print(f"\n--- {label} ---")
    print("final_output:", result.final_output)
    print("last_agent.name:", result.last_agent.name)
    print("len(new_items):", len(result.new_items))


async def demo_run() -> None:
    result = await Runner.run(build_agent(), "Name one river in Europe.")
    summarize("Runner.run() [async]", result)


def demo_run_sync() -> None:
    result = Runner.run_sync(build_agent(), "Name one mountain in Asia.")
    summarize("Runner.run_sync() [sync]", result)


async def demo_run_streamed() -> None:
    print("\n--- Runner.run_streamed() [token-by-token] ---")
    result = Runner.run_streamed(build_agent(), "Name one desert in Africa.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print()  # newline after the streamed tokens
    summarize("Runner.run_streamed() [after stream finished]", result)


async def demo_run_and_streamed() -> None:
    await demo_run()
    await demo_run_streamed()


if __name__ == "__main__":
    # run_sync() starts its own event loop internally, so it must be called
    # from plain sync code - never from inside something asyncio.run() is
    # already driving (that's exactly Bug 4 in evidence/bugs.md).
    demo_run_sync()
    asyncio.run(demo_run_and_streamed())

"""
Part G - Bonus: cross-provider handoff.

A triage agent looks at the question and hands off to a specialist agent.
The two specialists run on different models so you can see the handoff
actually switches providers mid-conversation:
  - if OPENAI_API_KEY is set: History -> Gemini, Math -> OpenAI
  - otherwise: both stay on Gemini but use two different Gemini models,
    so the switch is still visible in the transcript / last_agent.name

    uv run handoff.py
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
gemini_model = OpenAIChatCompletionsModel(
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    openai_client=gemini_client,
)

openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
if openai_api_key:
    openai_client = AsyncOpenAI(api_key=openai_api_key)
    second_model = OpenAIChatCompletionsModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_client=openai_client,
    )
    second_model_label = "openai"
else:
    # No OpenAI key available - fall back to a second, cheaper Gemini model
    # so the handoff still crosses a real model boundary.
    second_model = OpenAIChatCompletionsModel(
        model="gemini-3.5-flash-lite",
        openai_client=gemini_client,
    )
    second_model_label = "gemini-3.5-flash-lite"

history_agent = Agent(
    name="History Agent",
    instructions="You answer history questions in one or two sentences.",
    model=gemini_model,
)

math_agent = Agent(
    name="Math Agent",
    instructions="You answer math questions in one or two sentences, showing the calculation.",
    model=second_model,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Decide whether the user's question is about history or math, and hand off "
        "to the matching specialist agent. Do not answer it yourself."
    ),
    model=gemini_model,
    handoffs=[history_agent, math_agent],
)

if __name__ == "__main__":
    print(f"(math_agent is running on: {second_model_label})\n")

    for question in [
        "When did the French Revolution begin?",
        "What is 17 * 23?",
    ]:
        result = Runner.run_sync(triage_agent, question)
        print(f"Q: {question}")
        print(f"Handled by: {result.last_agent.name}")
        print(f"A: {result.final_output}\n")

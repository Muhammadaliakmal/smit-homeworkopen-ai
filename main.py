"""
Part D - The Provider Switch.

Reads MODEL_PROVIDER out of .env and builds a model object for whichever
provider was picked. The Agent(...) call below is byte-for-byte identical
no matter which branch ran - only the `model` variable it closes over
changes. Flip MODEL_PROVIDER in .env and rerun; nothing here needs editing.

    uv run main.py
"""

import os

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
set_tracing_disabled(True)

provider = os.getenv("MODEL_PROVIDER", "gemini").strip().lower()

if provider == "gemini":
    client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        openai_client=client,
    )
elif provider == "openai":
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = OpenAIChatCompletionsModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_client=client,
    )
else:
    raise ValueError(f"Unknown MODEL_PROVIDER: {provider!r} (expected 'gemini' or 'openai')")

# --- Everything below this line is identical regardless of provider. ---

agent = Agent(
    name="Provider-Switch Agent",
    instructions="You are a concise assistant. Answer in at most two sentences.",
    model=model,
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "What is 12 * 8, and name one prime number greater than 100?")
    print(f"[provider={provider}]")
    print(result.final_output)

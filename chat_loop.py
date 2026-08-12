"""
Part E - Multi-turn chat loop.

Keeps conversation memory across turns using result.to_input_list(), which
returns the full running transcript (your messages + the agent's replies)
so it can be fed back in as the input to the next turn. Type "exit" to quit.

    uv run chat_loop.py
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
    name="Chat Loop Agent",
    instructions="You are a friendly, concise assistant. Remember earlier turns in this chat.",
    model=OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        openai_client=gemini_client,
    ),
)


def main() -> None:
    print("Chat loop ready. Type 'exit' to quit.")
    history = []  # grows via result.to_input_list() after every turn

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye.")
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        result = Runner.run_sync(agent, history)
        print(f"Agent: {result.final_output}")

        history = result.to_input_list()


if __name__ == "__main__":
    main()

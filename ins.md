OpenAI Agents SDK: Agent + Runner + Multi-Provider (OpenAI & Gemini)

The Situation

You're a junior AI engineer at a startup. The team built an agent that only runs on OpenAI. The client now says that, because of billing issues, the agent also has to run on Gemini — without changing the agent's code. Your lead's instruction was: "Make the provider a config value. Don't hard-code it." That's your job.



What You Must Build
A CLI agent where one Agent definition runs on two different providers (OpenAI and Gemini), switched by changing a single line in .env. Alongside that, you'll test the behaviour of all three Runner run methods yourself and write down what you observed.



Mandatory Requirements

Part A — Setup [MUST]
Create the project with uv: uv init + uv add openai-agents python-dotenv
Create a .env file (and add it to .gitignore — a pushed key is an instant zero):
GEMINI_API_KEY=...OPENAI_API_KEY=... # leave blank if you don't have oneMODEL_PROVIDER=gemini # gemini | openaiGEMINI_MODEL=... # find the current stable model name from Google's docs yourself
Write a README.md with setup steps, so anyone can clone and run it.


Note: Model names change every few months. I'm deliberately not giving you one — finding the current stable model from Google's official docs (ai.google.dev/gemini-api/docs/models) is part of the work. In your README, state which one you picked and why.



Part B — Your First Agent [MUST]
Create hello_agent.py: an Agent with a name and instructions, run with Runner.run_sync().
Connect Gemini through AsyncOpenAI (with a custom base_url) + OpenAIChatCompletionsModel.
Print result.final_output only.


Part C — Three Ways to Configure the Model [MUST]
Do the same job at three different levels, each in its own file:
config_agent_level.py — model passed directly into Agent(model=...)
config_run_level.py — model via RunConfig, passed as Runner.run_sync(..., run_config=config)
config_global_level.py — set_default_openai_client() + set_tracing_disabled()
In DECISIONS.md, write up which approach fits which situation and why. Give one realistic use-case for each.


Part D — The Provider Switch [MUST]
Create main.py that reads MODEL_PROVIDER from .env and decides which client to build.
Constraint: the Agent(...) definition must be byte-for-byte identical for both providers. If you find yourself editing the agent, your design is wrong.
Run the same question through both providers and save the results to evidence/provider_comparison.md — response, rough latency, and two differences you noticed.


Part E — Understanding the Runner [MUST]
Demonstrate all three run methods:
Runner.run() — async, with await
Runner.run_sync() — sync
Runner.run_streamed() — loop over stream_events() for token-by-token output
From the RunResult object, print: final_output, last_agent.name, and the length of new_items.
Build a multi-turn chat loop that remembers previous turns using result.to_input_list(). Typing exit ends the loop.


Part F — Break It On Purpose (Breakage Lab) [MUST]
You're given broken_agent.py with 6 planted bugs. For each one, fill a row in evidence/bugs.md:
# Exact error line Root cause Fix How you figured it out
No screenshots — paste the actual terminal error text. Pasted errors you didn't produce yourself will surface in the viva.


Part G — Bonus [SHOULD]
Build two agents — one on Gemini, one on OpenAI — and route between them with a handoff. (If you only have a Gemini key, use two different Gemini models instead.)
Constraints
Python 3.11+, uv as the only package manager
openai v2.x + latest openai-agents (the new SDK won't work with openai v1.x)
No API keys anywhere in the repo
Every script must run standalone: uv run <file>.py
Keep total agent calls under ~50 — budget your free tier


What You Submit
A public GitHub repo containing:

├── README.md # setup + why you chose that model

├── DECISIONS.md # comparison of the 3 config approaches

├── hello_agent.py

├── config_agent_level.py

├── config_run_level.py

├── config_global_level.py

├── main.py # provider switch

├── runner_lab.py # run / run_sync / run_streamed

├── chat_loop.py # multi-turn

├── fixed_agent.py # your repaired broken_agent.py

├── evidence/

│ ├── provider_comparison.md

│ ├── bugs.md

│ └── output.log # raw terminal output

└── .env.example # without keys



Rules on AI Use
ChatGPT, Claude, Cursor, Copilot — all allowed, and you should use them. But:

You own everything you submit.
In the viva you can be asked about any line of your code.
"The AI wrote it" is not an answer. A student who can't explain their submission loses all 25 Understanding marks, even if the code runs perfectly.
DECISIONS.md and bugs.md are the parts AI can't write for you — they come from real errors on your own machine.
# One Agent, Two Providers — OpenAI Agents SDK (OpenAI & Gemini)

A single `Agent` definition that runs on either OpenAI or Gemini,
switched by one line in `.env`. Built with the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/),
pointing Gemini at the SDK through its OpenAI-compatible endpoint.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```bash
git clone <this-repo-url>
cd task-1
uv sync                 # installs openai-agents (v2.x openai under the hood) + python-dotenv
cp .env.example .env
```

Edit `.env` and fill in at least `GEMINI_API_KEY` (free, from
[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)).
`OPENAI_API_KEY` is optional — leave it blank if you don't have one; every
script defaults `MODEL_PROVIDER` to `gemini` so nothing requires it except
`main.py`/`handoff.py` when you deliberately point them at OpenAI.

```env
GEMINI_API_KEY=...
OPENAI_API_KEY=          # optional
MODEL_PROVIDER=gemini    # gemini | openai
GEMINI_MODEL=gemini-3.5-flash-lite
OPENAI_MODEL=gpt-4o-mini
```

Then run any script standalone:

```bash
uv run hello_agent.py
uv run main.py
uv run runner_lab.py
uv run chat_loop.py
uv run handoff.py
```

`.env` is gitignored — never commit it. `.env.example` ships without keys.

## Which Gemini model, and why

Picked from the live list at
[ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models),
not guessed. Short version: I went through **three** models before
landing on the one that's actually usable on a free API key, and that
journey is worth documenting because it's the real engineering decision,
not just "which name is newest."

1. **`gemini-3.6-flash`** — the model listed first, described as Google's
   current default ("balances speed with intelligence... for agentic and
   multimodal tasks"). Technically "the current stable model." In
   practice, its free tier is capped at a *very* tight daily quota — I
   hit `429 RESOURCE_EXHAUSTED` (`limit: 20`) within my first handful of
   test calls while just building this repo.
2. **`gemini-2.5-flash`** — the previous generation's "best
   price-performance" model, still listed as stable. More headroom than
   3.6, but I still burned through its free daily quota (also `limit: 20`)
   partway through generating the evidence for Part E/F/G — see the
   `429` entries in `evidence/output.log`.
3. **`gemini-3.5-flash-lite`** — "fastest, most cost-effective 3.5 model
   for high-throughput execution." This is what `.env.example` actually
   ships with. It tolerated several back-to-back calls with no rate-limit
   errors, which is what a project meant to be cloned and immediately
   `uv run` by someone else actually needs.

Also worth noting: `gemini-2.5-flash-lite`, an older cost-tier model, now
returns `404 - "no longer available to new users"` — a reminder that the
brief for this assignment ("model names change every few months") is
literally true even between models in the *same* family, not just across
major versions.

**If you have more free-tier headroom than I did**, `gemini-3.6-flash` or
`gemini-2.5-flash` are strictly more capable and are drop-in swaps — just
change `GEMINI_MODEL` in `.env`, nothing else in this repo hard-codes a
model name outside of `broken_agent.py`'s intentionally-planted bug.

## Repo layout

| File | What it demonstrates |
|---|---|
| `hello_agent.py` | Part B — first agent, Gemini via `AsyncOpenAI` + `OpenAIChatCompletionsModel`, `Runner.run_sync()` |
| `config_agent_level.py` | Part C — model set on `Agent(model=...)` |
| `config_run_level.py` | Part C — model set via `RunConfig`, passed to `Runner.run_sync(..., run_config=...)` |
| `config_global_level.py` | Part C — `set_default_openai_client()` + `set_default_openai_api()` + `set_tracing_disabled()` |
| `main.py` | Part D — reads `MODEL_PROVIDER` from `.env`; the `Agent(...)` call is identical either way |
| `runner_lab.py` | Part E — `Runner.run()`, `Runner.run_sync()`, `Runner.run_streamed()` side by side |
| `chat_loop.py` | Part E — multi-turn chat using `result.to_input_list()`, type `exit` to quit |
| `broken_agent.py` | Part F — 6 intentionally planted bugs (see `evidence/bugs.md`) |
| `fixed_agent.py` | Part F — the repaired version |
| `handoff.py` | Part G (bonus) — triage agent hands off to a History or Math specialist on a different model |
| `DECISIONS.md` | Part C write-up: agent vs. run vs. global config, when to use each |
| `evidence/` | `provider_comparison.md`, `bugs.md`, `output.log` — real terminal output, not fabricated |

## Why Gemini needs two extra lines OpenAI doesn't

Gemini has an OpenAI-compatible endpoint
(`https://generativelanguage.googleapis.com/v1beta/openai/`), so pointing
`AsyncOpenAI(base_url=...)` at it and wrapping it in
`OpenAIChatCompletionsModel` is enough for agent-level and run-level
config. For **global**-level config specifically, one more line is
required: `set_default_openai_api("chat_completions")`. The Agents SDK
defaults to OpenAI's newer Responses API, which Gemini's compatibility
layer doesn't implement — without that line, every request 404s. See
`config_global_level.py` and `DECISIONS.md`.

Tracing is disabled everywhere (`set_tracing_disabled(True)`) because the
SDK's default tracing exporter sends trace data to
`platform.openai.com` using `OPENAI_API_KEY` — pointless (and noisy) when
running against Gemini with no OpenAI key configured.

## Budget

Every script here makes 1–4 model calls. Free-tier Gemini quotas turned
out to be the real constraint on this project (see above) — budget
accordingly if you're re-running everything from scratch.

# DECISIONS.md — three ways to configure the model

Same job (point an `Agent` at Gemini), done three different ways. All
three ran successfully — see `evidence/output.log`. Here's when I'd
actually reach for each one.

---

## 1. Agent-level — `config_agent_level.py`

```python
agent = Agent(
    name="Agent-Level Config Agent",
    instructions="...",
    model=OpenAIChatCompletionsModel(model="gemini-3.5-flash-lite", openai_client=gemini_client),
)
```

The model is baked into the `Agent` object itself. Whoever imports this
agent and calls `Runner.run(agent, ...)` gets this exact model, full stop
— they cannot accidentally run it against something else without editing
this file.

**Fits:** a *specialist* agent whose whole reason to exist is tied to one
specific model's capability — e.g. an agent that only works because it's
running on a model with a huge context window, or a code-review agent you
deliberately pin to a specific reasoning-tier model so its behaviour
doesn't silently drift when someone changes an unrelated global default
elsewhere in the codebase.

**Realistic use-case:** a `handoff.py`-style triage system where each
specialist agent (history, math, ...) is deliberately locked to the model
best suited for its job, and you don't want a global config change to
accidentally move a specialist onto a weaker/cheaper model.

---

## 2. Run-level — `config_run_level.py`

```python
agent = Agent(name="Run-Level Config Agent", instructions="...")  # no model at all

run_config = RunConfig(model=OpenAIChatCompletionsModel(model="gemini-3.5-flash-lite", openai_client=gemini_client))
result = Runner.run_sync(agent, "...", run_config=run_config)
```

The `Agent` definition is provider-agnostic — it says *what* the agent
should do, not *which model* does it. The model is decided fresh at the
call site, every time `Runner.run*()` is invoked.

**Fits:** exactly this assignment's Part D scenario — one `Agent`
definition, many possible models/providers, decided per-invocation. Also
fits things like A/B testing a prompt across two models, or a CLI tool
where `--provider` is a runtime flag.

**Realistic use-case:** `main.py` in this repo. The `Agent(...)` call is
byte-for-byte identical whether `MODEL_PROVIDER=gemini` or
`MODEL_PROVIDER=openai` in `.env` — only the `RunConfig`/model variable
built earlier changes. This is the one that actually satisfies the
client's "switch provider without touching the agent's code" requirement.

---

## 3. Global-level — `config_global_level.py`

```python
set_default_openai_client(gemini_client)
set_default_openai_api("chat_completions")
set_tracing_disabled(True)

agent = Agent(name="Global-Level Config Agent", instructions="...", model="gemini-3.5-flash-lite")
```

Nothing on the agent, nothing on the run — the whole SDK process is
redirected at import time. Every `Agent` and every `Runner` call anywhere
in this process now talks to Gemini unless something more specific
(agent-level or run-level) overrides it.

**Fits:** a small script or notebook where there's only ever going to be
one provider for the entire process's lifetime, and you don't want to
thread a client/model object through every single agent definition.
Also the only one of the three that needed an extra line
(`set_default_openai_api("chat_completions")`) — Gemini's
OpenAI-compatible endpoint only implements the Chat Completions shape,
but the SDK defaults to the newer Responses API, so without this line
every request 404s.

**Realistic use-case:** a single-purpose CLI tool or cron job (e.g. "summarize
today's logs") that only ever runs against one provider, where the extra
ceremony of building/passing a `model=` object into every `Agent(...)`
call would just be repetitive boilerplate for no benefit.

---

## Which one actually solves Part D?

**Run-level.** The client's constraint was "the `Agent(...)` definition
must be byte-for-byte identical for both providers." Agent-level config
bakes the model into the agent, so it fails that constraint outright.
Global-level would technically also satisfy "don't edit the Agent," but
it's a worse fit here specifically *because* it's global — `main.py`
needs to decide the provider once, per run, from an env var; it doesn't
need to (and shouldn't) mutate process-wide state that any other code
importing this module would silently inherit. Run-level config keeps the
"pick a model" decision local to the one place that actually needs to
make it.

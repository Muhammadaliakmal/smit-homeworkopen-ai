# Breakage Lab — bugs.md

Process: ran `uv run broken_agent.py`, fixed only the bug that caused the
error in front of me, reran, repeated until it printed a clean answer.
Errors below are pasted directly from the terminal (Windows / PowerShell,
`uv run`), not retyped or paraphrased.

---

## Bug 1 — bad import name

**Exact error**
```
File "C:\Users\PC\Desktop\ali-smit\task-1\broken_agent.py", line 12, in <module>
    from agents import Agent, OpenAIChatCompletionModel, Runner, set_tracing_disabled
ImportError: cannot import name 'OpenAIChatCompletionModel' from 'agents' (...\agents\__init__.py). Did you mean: 'OpenAIChatCompletionsModel'?
```

**Root cause**
Typo'd the class name — `OpenAIChatCompletionModel` instead of
`OpenAIChatCompletionsModel` (missing the "s" in Completions).

**Fix**
```python
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
```
(and the matching usage further down, `model=OpenAIChatCompletionsModel(...)`)

**How I figured it out**
Python's own `ImportError` message did the work for me — it names the
closest valid symbol ("Did you mean: 'OpenAIChatCompletionsModel'?"). Confirmed
the real name by running `python -c "import agents; print([n for n in dir(agents) if 'Chat' in n])"`.

---

## Bug 2 — API key never loaded from `.env`

**Exact error**
```
File "C:\Users\PC\Desktop\ali-smit\task-1\broken_agent.py", line 18, in <module>
    gemini_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
  File ...\openai\_client.py", line 837, in __init__
    raise OpenAIError(
        "Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable."
    )
openai.OpenAIError: Missing credentials. ...
```

**Root cause**
`broken_agent.py` never calls `load_dotenv()`, so `.env` is never read into
`os.environ`. `os.getenv("GEMINI_API_KEY")` returns `None`, and the
`AsyncOpenAI` constructor refuses to build a client with no key at all
(it fails immediately, before any network call).

**Fix**
```python
from dotenv import load_dotenv
load_dotenv()
```
added before the client is constructed.

**How I figured it out**
The traceback points at client construction, not a network call — so this
isn't an "invalid key" problem, it's a "no key ever arrived" problem. Printed
`os.getenv("GEMINI_API_KEY")` right before the client line and got `None`;
grepped the file for `load_dotenv` and it wasn't there.

---

## Bug 3 — wrong keyword argument on `Agent(...)`

**Exact error**
```
File "C:\Users\PC\Desktop\ali-smit\task-1\_debug_broken.py", line 24, in <module>
    agent = Agent(
        name="Broken Agent",
    ...<4 lines>...
        ),
    )
TypeError: Agent.__init__() got an unexpected keyword argument 'instruction'. Did you mean 'instructions'?
```

**Root cause**
`Agent(... instruction="...", ...)` — the kwarg is `instructions` (plural).
`Agent` is a `@dataclass`, so an unknown kwarg is a hard `TypeError`, not a
silently-ignored attribute.

**Fix**
```python
agent = Agent(
    name="Broken Agent",
    instructions="You are a concise assistant. Answer in one sentence.",
    ...
)
```

**How I figured it out**
Same pattern as Bug 1 — Python's `TypeError` already suggests the fix
("Did you mean 'instructions'?"). Cross-checked against `hello_agent.py`,
which I'd already gotten working, to see the correct kwarg spelling.

---

## Bug 4 — `Runner.run_sync()` called from inside a running event loop

**Exact error**
```
File "C:\Users\PC\Desktop\ali-smit\task-1\_debug_broken.py", line 35, in main
    result = Runner.run_sync(agent, "What is the capital of Japan?")
  File "...\agents\run.py", line 1904, in run_sync
    raise RuntimeError(
        "AgentRunner.run_sync() cannot be called when an event loop is already running."
    )
RuntimeError: AgentRunner.run_sync() cannot be called when an event loop is already running.
```

**Root cause**
`broken_agent.py` defines `async def main()` and drives it with
`asyncio.run(main())` — but *inside* that coroutine it calls the **sync**
entry point `Runner.run_sync()`. `run_sync()` internally starts its own
event loop, and Python won't let you nest a second loop inside one that's
already running.

**Fix** — pick one consistent style. I used the async one, since `main()`
was already a coroutine:
```python
async def main():
    result = await Runner.run(agent, "What is the capital of Japan?")
```
(the alternative fix would have been to drop `async def`/`asyncio.run` entirely
and call `Runner.run_sync()` from a plain `def main()`).

**How I figured it out**
The error message states the constraint outright ("cannot be called when an
event loop is already running"). Recognized `async def main(): ... asyncio.run(main())`
as the classic case of mixing a sync helper into code that's already async.

---

## Bug 5 — dead / nonexistent model name

**Exact error**
```
File "...\agents\models\openai_chatcompletions.py", line 734, in _fetch_response
    ret = await self._get_client().chat.completions.create(**create_kwargs)
  File "...\openai\_base_client.py", line 1777, in request
    raise self._make_status_error_from_response(err.response) from None
openai.NotFoundError: Error code: 404 - [{'error': {'code': 404, 'message': 'models/gemini-pro is not found for API version v1main, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}]
```

**Root cause**
`broken_agent.py` hard-codes `model="gemini-pro"`, an old model name that
Google has since retired from the `v1beta` API surface used by the
OpenAI-compatibility endpoint. The request reaches Gemini fine (this is a
live network call, not a client-side error) — Gemini itself rejects the
model name with `404 NOT_FOUND`.

**Fix**
```python
model=OpenAIChatCompletionsModel(
    model="gemini-3.6-flash",   # current stable model, see README.md
    openai_client=gemini_client,
),
```

**How I figured it out**
`404 NOT_FOUND` plus "is not found for API version v1main" is Gemini
telling you the model string itself is bad, not your key or your request
shape. Cross-checked the current model list at
https://ai.google.dev/gemini-api/docs/models and swapped in the same
`GEMINI_MODEL` value used everywhere else in this repo.

---

## Bug 6 — wrong attribute on the `RunResult`

**Exact error**
```
File "C:\Users\PC\Desktop\ali-smit\task-1\_debug_broken.py", line 36, in main
    print(result.output_text)
          ^^^^^^^^^^^^^^^^^^
AttributeError: 'RunResult' object has no attribute 'output_text'
```

**Root cause**
`broken_agent.py` prints `result.output_text`, which doesn't exist on this
SDK's `RunResult`. That name is a mash-up of a different API's field
(`output_text` shows up on OpenAI's raw Responses API objects) — but the
Agents SDK's `RunResult` exposes the final answer as `final_output`.

**Fix**
```python
print(result.final_output)
```

**How I figured it out**
The traceback names the exact class (`RunResult`) and exact missing
attribute. Ran `python -c "from agents import Runner; help(Runner.run_sync)"`
and `print(dir(result))` on a working script (`hello_agent.py`) to see the
real attribute names — `final_output`, `last_agent`, `new_items` all showed
up there.

---

## After all 6 fixes

```
$ uv run python fixed_agent.py
The capital of Japan is Tokyo.
```

Clean run, no warnings, no errors. See `fixed_agent.py` for the fully
repaired file and `evidence/output.log` for the raw session.

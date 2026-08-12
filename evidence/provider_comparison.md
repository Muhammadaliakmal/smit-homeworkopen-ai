# Provider comparison — `main.py`

Same question, same `Agent(...)` definition (byte-for-byte — only the
`MODEL_PROVIDER` value in `.env` changed between runs), run once against
each provider. Raw output below is copy-pasted from the terminal, also
saved in `evidence/output.log`.

**Question sent:** `"What is 12 * 8, and name one prime number greater than 100?"`

---

## Gemini (`MODEL_PROVIDER=gemini`, `gemini-2.5-flash`)

```
[provider=gemini]
12 multiplied by 8 is 96. An example of a prime number greater than 100 is 101.

real    0m9.743s
```

## OpenAI (`MODEL_PROVIDER=openai`, `gpt-4o-mini`)

```
[provider=openai]
12 * 8 equals 96. One prime number greater than 100 is 101.

real    0m9.514s
```

(`real` = wall-clock time for the whole process, measured with `time uv run python main.py` —
this includes Python/uv startup, not just the model call, so treat it as "rough" per the brief,
not a precise API-latency benchmark.)

---

## Two differences I noticed

1. **Latency was close, not identical, and neither provider "won" consistently.**
   Gemini: ~9.7s, OpenAI: ~9.5s for the same prompt in this run. Both are
   dominated by process startup + one round trip, not by the model itself
   being obviously faster — with only one sample each this isn't a real
   benchmark, just an observation that swapping providers didn't change
   the user-facing experience in any noticeable way.

2. **Free-tier friction was completely one-sided.** The OpenAI key never
   once rate-limited me during this whole project. The Gemini free tier
   did, repeatedly and hard — I burned through the entire daily quota
   (`429 RESOURCE_EXHAUSTED`, `limit: 20`) for **two different** Gemini
   models (`gemini-3.6-flash`, then `gemini-2.5-flash`) just from normal
   iterative testing while building this repo, and had to fall back to a
   third (`gemini-3.5-flash-lite`) to keep working. See
   `evidence/output.log` for the actual `429` responses and README.md for
   the full model-selection story. This is arguably the single biggest
   practical difference between the two providers for a project like this
   one: OpenAI's paid key is more forgiving to develop against than
   Gemini's free key, even though Gemini is free and OpenAI isn't.

Both answers were also phrased slightly differently ("12 multiplied by 8
is 96" vs "12 * 8 equals 96") despite an identical prompt and instructions
— expected model-to-model variance, not something either the `Agent`
definition or the SDK controls.

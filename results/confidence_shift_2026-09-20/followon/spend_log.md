# Spend log (follow-on)

No paid API calls. All LLM calls go to the local vLLM server (Qwen/Qwen3.8-27B on 127.0.0.1:8300).

| when | what | calls | prompt tokens | completion tokens | wall time |
|---|---|---|---|---|---|
| 2026-09-20 21:00-21:40 | affected-list calls (patrol.affected_llm), Qwen3.8-27B local, thinking off | 9 so far | 10380 | 2146 | 2 min wall (queued behind the arms) |
| 2026-09-20 | uncapped first prompt (affected_llm_v1_uncapped) | 2 | 1900 | 830 | 1 min |
| 2026-09-20 | classical replays, detector grid, conformal: no LLM | 0 | 0 | 0 | ~2 min CPU |
| 2026-09-20 21:00-22:45 | affected-list calls, all 72 message days (final) | 63 | 74530 | 15094 | 41 min wall, queued behind the arms |

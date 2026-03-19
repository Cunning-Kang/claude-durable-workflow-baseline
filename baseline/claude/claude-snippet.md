## Durable workflow baseline

- Use repo durable workflow artifacts only for L1/L2 work that crosses sessions or needs durable evidence.
- The durable front door for a feature is `docs/specs/<feature>/index.md`.
- Native Claude Code Task tools remain the session execution tracker.
- Repo task files record milestone truth only; they do not mirror session task state.
- When review is required, use an independent reviewer and record the outcome in `review.md`.
- When verification is required, record durable evidence in `verify.md` before claiming completion.
- After completing a durable task, explicitly check whether any stable pattern or gotcha should be written to project memory.

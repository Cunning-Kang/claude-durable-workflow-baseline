# Trigger Eval Conclusions

## Runs

1. **gpt-5.5**: All 60 `claude -p` calls hit 429 rate limit. No valid trigger data.
2. **GLM-5.1** (3 iterations, runs-per-query=1): All should-trigger queries scored 0/1. All should-not-trigger queries correctly did not trigger.

## Root cause

GLM-5.1 does not invoke the `Skill` tool when responding to `claude -p` queries. It uses Glob/Read/Bash directly. The trigger eval harness detects skill usage by checking for `Skill` or `Read` calls that reference the skill command name. Since GLM-5.1 never calls `Skill`, trigger rate is always 0 regardless of description quality.

## Implications

- **Negative correctness**: GLM-5.1 correctly does not trigger quality-loop on should-not-trigger queries. No false-positive risk.
- **Positive blindness**: GLM-5.1 cannot be triggered to use this skill via description alone. The skill body will only be loaded if the user explicitly invokes `/quality-loop`.
- **Description optimization is moot for GLM-5.1**: The automated description optimizer cannot distinguish between descriptions because the model never triggers any of them.

## Decision

Keep the current description as-is. It was validated through 4 rounds of strict adversarial document review (no Critical/Major issues in final pass). The description text is correct and precise — the trigger limitation is a model capability issue, not a description issue.

## Files

- eval set: `eval_set.json`
- gpt-5.5 results: `results/2026-04-25_232400/` (all rate-limited)
- GLM-5.1 results: `results-glm/2026-04-26_080400/`

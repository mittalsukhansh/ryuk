# AgentPay Codex Pack — Start Here

Read in this order:

1. PLAN.md
2. AGENTS.md
3. ARCHITECTURE.md
4. TASKS.md
5. CODEX_PROMPTS.md

Then give Codex Prompt 1 only.

Recommended loop:

```text
Ask/Plan
-> one scoped implementation task
-> tests
-> inspect diff
-> commit
-> next task
```

Core flow:

```text
User intent
-> AI proposal
-> pre-payment verification
-> deterministic policy
-> approval if required
-> PayPal Sandbox
-> provider verification
-> audit
```

Absolute rule:

> The LLM proposes. The backend authorizes.

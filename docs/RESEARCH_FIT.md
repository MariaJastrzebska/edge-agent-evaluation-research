# Why I want to work on agent evaluation and safety

I started this project with a practical question: could a small model running locally collect useful information over a conversation? I built a Flutter prototype and Python evaluation tooling, then compared model behavior, quantization settings, and runtime costs. Most of that work took place in 2025, with further work in early 2026. I am publishing the summary in October 2026, alongside later experiments and what I learned from revisiting the results.

What interests me most now is the gap between an output that looks correct and an agent that actually completes a task correctly. I saw responses that passed structural checks while getting argument values wrong. I also saw why per-turn scores could miss errors that accumulate across a conversation. Those problems led me toward evaluating actions, state changes, and permission boundaries.

## What I bring from this work

I have worked across the application and evaluation layers: local inference through llama.cpp, structured response contracts, Python scoring, experiment records, and resource measurements. Building both sides helped me notice problems that an isolated benchmark would miss, such as the delay before a user sees useful content when the model generates metadata first.

The configuration experiments also taught me to be careful about explanations. Finding a faster combination is useful, but it does not tell me which change caused the improvement. Comparing models is similarly difficult when their prompts, output lengths, and failure behavior differ. I want my next experiments to make those distinctions explicit from the start.

My experience is primarily with small models and task-specific evaluation. I have not established that the results generalize to frontier models, and the medical setting was an information-collection use case, not a clinical validation study. What I can build on is the evaluation infrastructure and the experience of diagnosing where its metrics fall short.

This is the connection I see to the [Anthropic AI Safety & Security Fellows Program](https://job-boards.greenhouse.io/anthropic/jobs/5183044008): I want to use that engineering experience to investigate a narrow, measurable question about agent behavior, and produce results that other researchers can inspect and reproduce.

## The question I would investigate next

**Can an agent preserve permissions and confirmed state throughout a multi-turn task without becoming so restrictive that it stops being useful?**

I would start with synthetic records and mock tools. The cases would include ordinary updates that should succeed, missing information that requires clarification, user corrections, conflicting statements, and attempts to override instructions or send data to an unauthorized destination.

I would compare a prompt-only policy with permissions enforced by the application. For selected actions, I would also test an approval step. An always-decline baseline and a simple deterministic policy would help distinguish useful protection from a system that merely refuses everything.

The evaluator would inspect both the proposed tool call and the state change that actually occurred. I would measure unauthorized actions, disclosures in observable outputs, successful permitted tasks, and appropriate clarification. Retries, dialogue length, latency, and energy would provide the cost side of the comparison.

I would freeze a held-out set before tuning prompts, use paired benign and adversarial cases, retain complete trajectories, and repeat measurements. An ablation would separate the model's compliance with instructions from the application's ability to block a disallowed operation.

I have not run this experiment yet. I would first validate the task contract and scorer, establish baselines, inspect failures, and then test one targeted intervention on held-out cases. That is the direction I want to take the work: fewer loosely connected comparisons, and a stronger answer to a specific question.

My [retrospective](RETROSPECTIVE.md) explains the lessons behind that choice. The [repository map](REPOSITORIES.md) links the implementation and experimental artifacts.

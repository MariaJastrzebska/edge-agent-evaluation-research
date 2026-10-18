# Dates, lessons learned, and assessment in hindsight

**Original research: primarily 2025, with further work in early 2026 · Retrospective and repository publication: October 2026.**

I wrote these reflections in October 2026, looking back on work I carried out mainly in 2025 and continued in early 2026. Some of the most useful lessons became clearer when I revisited the results and worked on the later experiments.

## When the work was created

| Period | Work and records |
| --- | --- |
| 2025 | I carried out most of the original research and development. Application diagrams are dated August; quantization exports are dated October. |
| January–February 2026 | I continued the work and revised the manuscript. Available Git history starts with a January import; model-comparison plots and architecture exports also date from this period. |
| August 2026 | I continued the evaluation laboratory work, including the structured-output pilots and contract debugging. |
| October 2026 | I ran the synthetic routing study and assembled this summary and retrospective. |

File-export and Git dates locate individual artifacts; they do not date the beginning of the whole project. The [source record](../PROVENANCE.md) lists the revisions and experiment dates.

## How I see the work now

The part I value most is that I built the whole path from a local application to an evaluation workflow. I could change a model or runtime setting, inspect the resulting responses, and compare quality with latency and resource use. Working on the application also exposed problems that I would not have noticed from scores alone.

I was less careful about the scope of some conclusions. The experiments were useful for comparing configurations on my task, but they did not establish clinical reliability or explain every performance difference. I would now separate those claims much more clearly. A model judge gave me a practical way to inspect many responses; it did not turn those judgments into ground truth.

I also spent more effort expanding the configuration matrix than isolating a small number of hypotheses. The broad comparisons helped me find promising settings. To explain why those settings worked, I would need a more controlled follow-up experiment, with repeated measurements and a held-out set.

## What I would keep

I would keep the concrete information-collection task, the explicit state contract, and the combination of quality and systems measurements. They made failures visible: format checks and argument-agreement scores could disagree, or a model could finish quickly without completing the intended task. Revisiting a disagreement also taught me to check the scorer before attributing it to the model.

I would also keep the application as part of the research setup. It helped me distinguish token-generation speed from the time before the user sees an answer. And I would keep the raw outputs and experiment records: being able to revisit them has been more useful than relying on my original summary alone.

## Lessons learned

### 1. Validate the benchmark before scaling it

A large run matrix can repeatedly measure a mistake in the task contract. The early August status-case mismatch is one example. I corrected it before experiment 005, but a later review still found an object-versus-string conflict in the worked example. Fixing one field did not validate the whole contract. An evaluator should first pass deliberately constructed valid, invalid, incomplete, and contradictory examples. The prompt, schema, parser, and scorer must agree on the meaning of success.

**What I would change:** before running models, I would create a small hand-checked contract-validation set. I would test extraction behavior, status values, required fields, unit handling, and invalid responses. I would inspect raw outputs from every condition before launching the full sweep. This does not replace statistical evaluation; it prevents spending the evaluation budget on an inconsistent task.

### 2. Measure the task outcome, not a convenient proxy

Correct syntax is necessary for many integrations, but the application needs correct information and permitted state changes. High semantic similarity can also coexist with an incorrect number, unit, or tool argument.

**What I would change:** I would define the primary endpoint as a task-level outcome, such as correctly recording confirmed fields without inventing values. I would report structural validity and judge scores as diagnostic metrics. For tool-using agents, I would score the resulting state and actual executed action, not just the proposed JSON.

### 3. Separate controlled turn tests from complete conversations

Frozen reference histories make per-turn comparisons more controlled, but hide the consequences of the model's own earlier mistakes. A system may perform well when supplied with the correct history and fail when it must maintain that history itself.

**What I would change:** I would keep the original per-turn tests for diagnosis and use the existing dynamic simulator to measure final-state correctness and recovery more systematically. The scenarios would include user corrections, contradictory values, missing units, declined optional fields, and recovery after an earlier extraction error. I would measure both final state and the path taken to reach it.

### 4. Treat the judge as an instrument that needs calibration

Model judging makes broad analysis practical, but can favor fluent explanations, agree with a reference's mistakes, or vary with the rubric. A simulator and judge from the same model family may share errors.

**What I would change:** I would independently annotate a manageable subset, compare deterministic checks with judge decisions, inspect disagreements, and document the rubric and judge version. For a medical correctness claim, domain-expert review would be necessary. I would not describe the judge as an objective substitute for that review.

### 5. Start with a narrower causal question

The 46-configuration sweep is useful for finding candidate settings. It is weaker for explaining why a setting works when multiple controls change together. Similarly, models from different families differ in more than parameter count.

**What I would change:** I would begin with one hypothesis and a controlled comparison. For example, hold the model, prompt set, context lengths, and generation settings fixed while varying FlashAttention; then study interactions with cache settings in a small factorial design. Broad searches would generate hypotheses, and a separate confirmatory experiment would test the selected configuration on held-out cases.

### 6. Record the work performed, not just the time consumed

Request time depends on input length, output length, stopping behavior, and failures. In the later structured-output study, token counts change substantially between conditions. That prevents attributing all request-time differences to grammar processing.

**What I would change:** I would retain input/output token counts, prefill and decoding time, time to first user-visible content, and the termination reason. To estimate grammar overhead, I would additionally instrument per-token components or use a controlled workload that isolates the relevant computation. I would still report end-to-end cost because that is what the application pays.

### 7. Use a clear measurement scope for resource claims

System RAM, process memory, swap occupancy, CPU/GPU power, and package energy are different quantities. A flat utilization trace can reflect a sensor limitation rather than stable hardware behavior. Desktop behavior also does not transfer automatically to a phone.

**What I would change:** I would document sensor scope and sampling, retain an idle baseline, distinguish missing telemetry from zero, and measure the target device directly. I would integrate power over each request to obtain energy, then report energy per successful task alongside failure rates. I would avoid interpreting mW as energy or treating all system swap as model-owned memory.

### 8. Quantify variation at the right level

Conversation turns differ in content, so five successive rounds are not five repetitions of the same trial. Requests within one scenario also share structure. Error bars need an explicit definition and a justified unit of analysis.

**What I would change:** I would repeat conditions, randomize execution order, control warmup and background activity, and preserve paired comparisons. Where prompts or scenarios are the independent units, uncertainty estimation should respect that grouping. I would define what each interval measures and report case-level results rather than only overall means.

### 9. Include simple baselines that challenge the interpretation

In the later routing study, always declining achieves 45% agreement. Without that baseline, 60% looks more informative than it is. Conversely, maximizing refusal may make a system useless while improving a safety-oriented score.

**What I would change:** I would include always-decline, simple rule-based routing where applicable, and the unmodified runtime configuration. I would separately report authorized-task success, appropriate clarification, and unauthorized-action rates. Safety and utility should remain visible together.

### 10. Keep architecture claims distinct from guarantees

Local execution can reduce reliance on a remote inference service. It does not prove privacy, safe storage, secure logging, or resistance to malicious inputs. A schema constrains representation; it is not an authorization policy. A user confirmation screen is useful but must itself be tested in the actual flow.

**What I would change:** I would write an explicit threat model and enforce permissions outside the language model. I would inspect the full data path, including research judges, logs, storage, and tool execution. Any privacy or safety claim would identify the specific property measured and the environment in which it holds.

## How I would redesign the study today

I would retain the prototype and laboratory, but begin with a smaller, more decisive experiment:

1. **Choose one primary question.** For example: can a local agent preserve correct, confirmed state across user corrections while meeting an interaction-time budget?
2. **Define an observable success condition.** Freeze expected final records and allowed state transitions before tuning prompts. Include a held-out set.
3. **Validate the evaluation contract.** Check schemas, parsing, scorers, and deliberately malformed outputs without relying on a model to discover test bugs.
4. **Establish baselines.** Compare a simple deterministic collection policy and a default model configuration before adding optimization complexity.
5. **Run controlled and closed-loop tests.** Use fixed prefixes to diagnose individual behaviors and full trajectories to measure error accumulation and recovery.
6. **Select a small configuration matrix.** Vary one factor at a time initially, then test justified interactions. Keep model-family comparisons separate from within-model optimization.
7. **Measure on the target hardware.** Preserve runtime version, model hash, template, prompt, generation parameters, token counts, telemetry coverage, and execution order.
8. **Repeat and inspect.** Use scenario-aware uncertainty, examine worst cases and failures, and verify that the selected configuration generalizes to held-out tasks.
9. **State the result at the level supported.** Publish a bounded conclusion with data and reproduction instructions. Reserve mechanism claims for measurements that actually isolate the mechanism.

This design would likely test fewer configurations at first, but produce a stronger answer to a more important question.

## What I take forward

Looking back, the most valuable part of my study was building the complete path from a local agent prototype to an evaluation workflow and observing where apparently good metrics broke down. I learned that valid JSON is not the same as correct information, that a high judge score is not clinical validation, and that a runtime speedup needs to be interpreted alongside the work performed and the quality preserved.

If I started again, I would narrow the research question earlier, validate the benchmark contract before expanding the experiment matrix, and report complete-trajectory outcomes from the dynamic simulator alongside the frozen-prefix scores. I would use stronger baselines, repeat and randomize measurements, and separate target-device evidence from desktop observations. I would also be more precise about which findings are descriptive and which support a causal explanation.

I see the project as a foundation in research engineering and empirical evaluation. Its limitations now give me a clearer direction: build experiments that distinguish successful, useful agent behavior from outputs that merely look correct, and make the limits of every conclusion visible.

These changes describe how I would design the next study; I have not completed those experiments yet.

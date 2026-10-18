# Dates, lessons learned, and assessment in hindsight

**Original research: primarily 2025 · Thesis defense: April 2026 · Retrospective and repository publication: October 2026.**

Assessment prepared **18 October 2026**, looking back on the earlier thesis work. The author confirms the main research period and defense month; source artifacts provide additional chronological detail. This is a retrospective interpretation, not a claim that the original study was designed with every distinction below already resolved. First-person passages are proposed wording for the author's review.

## When the work was created

| Date or period | What the evidence establishes | What it does not establish |
| --- | --- | --- |
| 2025 | Most thesis research and development took place during this year, as confirmed by the author | An exact project start day |
| 13 August 2025 | Application-flow and validation image filenames contain `2025-08-13` | A verified project start date or an immutable creation timestamp |
| 8 October 2025 | Quantization figure filenames contain `2025-10-08_08-02-40` | That every thesis experiment ran on this date |
| 17 January 2026 | First available manuscript commit, `00eaa30`, is labeled “Initial Overleaf Import” | That research began on the import date; the earlier artifacts predate it |
| 18 January 2026 | The displayed model-comparison/resource figures carry this date in their source filenames | An independently audited experiment timestamp |
| 13 February 2026 | Later architecture export filenames carry this date | A new experimental validation of the architecture |
| 23 February 2026 | Last manuscript revision used here, `de6eed6`, is dated this day | A verified defense or degree-award date |
| April 2026 | Master’s thesis defended, as confirmed by the author | An exact defense day |
| 10 August 2026 | Repository records place the application/laboratory separation in this period | That all current laboratory functionality was already part of the thesis |
| 12 August 2026 | The later structured-output pilot is labeled as recorded on this date | A clean causal test despite the subsequently identified prompt/schema mismatch |
| 17 October 2026 | Later synthetic routing/thread study | A rerun of the original Apple Silicon experiments |
| 18 October 2026 | This expanded report, figure curation, and retrospective assessment | A new execution of the historical experiments |

**Most of the thesis work was completed in 2025, the manuscript was finalized in early 2026, and the thesis was defended in April 2026.** This summary and retrospective were published in October 2026. The August and October 2026 studies are separate post-thesis work. The main research period and defense month come from the author; source-file and Git dates document individual artifacts. No exact start, submission, or defense day is inferred.

Dates from filenames are weaker evidence than version history. Git timestamps also describe recorded source history rather than independently certified experiment execution. The [evidence ledger](../PROVENANCE.md) fixes the revisions used for this report.

## Overall assessment

**This is a substantive engineering-and-evaluation project whose strongest contribution is the integrated research workflow, rather than a new model or a conclusively established optimization mechanism.** The work connects a real implementation problem to model behavior and hardware constraints. Building the application, schemas, evaluator, comparison machinery, and plots required more than running a benchmark command.

The most persuasive evidence is concrete: the local prototype, the structured response contract, the ability to compare configurations, examples where different correctness metrics disagree, and observed quality/runtime trade-offs. These artifacts show technical ownership and an ability to investigate a system at multiple layers.

The weakest part is the distance between some observations and the original narrative's claims. A synthetic, narrow-agent evaluation cannot establish clinical reliability. A desktop power trace cannot establish phone battery performance. A configuration sweep cannot by itself explain the causal mechanism behind a speedup. A model judge is useful evidence, but does not make the assessment objective ground truth.

This distinction matters more than assigning the thesis a numerical research score. As a research portfolio, it supports claims about implementation, empirical investigation, and learning from measurement limitations. As a standalone publishable causal study, it would require a narrower question, stronger controls, clearer provenance for every numerical claim, and more complete uncertainty and failure analysis. Novelty would also need a dedicated literature assessment; it is not established by the size of the implementation.

## What was worth keeping

1. **A concrete task instead of generic chat quality.** Collecting structured information exposes missing fields, incorrect values, and state transitions. This makes failures more actionable than broad impressions of fluency.
2. **An implemented deployment setting.** The application revealed problems such as delayed user-visible output and context-management costs that an isolated generation benchmark could miss.
3. **Several evaluation dimensions.** The single-turn plot shows why JSON validity, argument correctness, and judge scores must remain separate. That distinction is directly useful in agent evaluation.
4. **Quality alongside systems measurements.** Fast low-quality responses are not a successful optimization. Keeping both axes avoids selecting a model merely because it returns quickly.
5. **Artifacts that can be revisited.** Source, plots, and later recorded captures support retrospective inspection. The present manifest and source map make that inspection easier.
6. **Willingness to revise the claim.** The later prompt/schema audit and refusal-only baseline illustrate useful research habits: checking the evaluator and asking whether a simple policy explains an apparently favorable result.

## Lessons learned

### 1. Validate the benchmark before scaling it

A large run matrix can repeatedly measure a mistake in the task contract. The later uppercase/lowercase status mismatch is a particularly clear example. An evaluator should first pass deliberately constructed valid, invalid, incomplete, and contradictory examples. The prompt, schema, parser, and scorer must agree on the meaning of success.

**What I would change:** before running models, I would create a small hand-checked contract-validation set. I would test extraction behavior, status values, required fields, unit handling, and invalid responses. I would inspect raw outputs from every condition before launching the full sweep. This does not replace statistical evaluation; it prevents spending the evaluation budget on an inconsistent task.

### 2. Measure the task outcome, not a convenient proxy

Correct syntax is necessary for many integrations, but the application needs correct information and permitted state changes. High semantic similarity can also coexist with an incorrect number, unit, or tool argument.

**What I would change:** I would define the primary endpoint as a task-level outcome, such as correctly recording confirmed fields without inventing values. I would report structural validity and judge scores as diagnostic metrics. For tool-using agents, I would score the resulting state and actual executed action, not just the proposed JSON.

### 3. Separate controlled turn tests from complete conversations

Frozen reference histories make per-turn comparisons more controlled, but hide the consequences of the model's own earlier mistakes. A system may perform well when supplied with the correct history and fail when it must maintain that history itself.

**What I would change:** I would keep the original per-turn tests for diagnosis and add closed-loop conversations. These would include user corrections, contradictory values, missing units, declined optional fields, and recovery after an earlier extraction error. I would measure both final state and the path taken to reach it.

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

## Proposed first-person closing reflection

> Looking back, the most valuable part of my thesis was building the complete path from a local agent prototype to an evaluation workflow and observing where apparently good metrics broke down. I learned that valid JSON is not the same as correct information, that a high judge score is not clinical validation, and that a runtime speedup needs to be interpreted alongside the work performed and the quality preserved.
>
> If I started again, I would narrow the research question earlier, validate the benchmark contract before expanding the experiment matrix, and evaluate complete conversations in addition to isolated turns. I would use stronger baselines, repeat and randomize measurements, and separate target-device evidence from desktop observations. I would also be more precise about which findings are descriptive and which support a causal explanation.
>
> I see the project as a foundation in research engineering and empirical evaluation. Its limitations now give me a clearer direction: build experiments that distinguish successful, useful agent behavior from outputs that merely look correct, and make the limits of every conclusion visible.

This reflection is a proposed articulation of lessons grounded in the reviewed work. It does not claim that the improved experiments have already been completed.

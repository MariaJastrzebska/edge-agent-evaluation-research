# Evaluating Small Language Models for On-Device Medical Information Collection

**Maria Magdalena Jastrzębska · Research conducted in 2025–2026**

Most of this work was carried out in **2025**. This repository publishes the research summary in **October 2026**, with a retrospective assessment and clearly separated follow-up studies.



## Abstract
Can a small language model collect information reliably across a conversation while running within the constraints of a personal device? I investigated this question through a diabetes information-collection assistant, a Python evaluation framework, and experiments with small models and inference configurations. The work connects application engineering with empirical evaluation: responses must preserve supplied facts, request missing information, follow a structured output contract, and remain usable as conversation context grows.

This report brings together the original research and its subsequent development in Edge-LLM-Lab. The original work compared model behavior using reference-based and reference-free multi-turn evaluation, combined structural checks with an LLM judge, and examined runtime trade-offs on Apple Silicon. Later work added a clearer separation between response capture and grading, reproducible reports, and synthetic tests of instruction and action boundaries. The central lesson is that device feasibility, task reliability, and resistance to adversarial inputs require distinct evidence.

**Start with:** [evaluation methodology](#evaluation-design), [results](#runtime-optimization), [safety and security](#what-this-work-contributes-to-ai-safety-and-security), or [code and provenance](#code-and-evidence).

## Motivation: from a useful application to a measurable question
The starting point was an application for people with diabetes. I wanted to explore whether a small local model could conduct an information-collection dialogue without requiring remote inference for every interaction. The intended task was to collect and structure information, rather than autonomously diagnose a condition or prescribe treatment.

Getting a model to execute was only the first step. A useful assistant also needs to retain previously supplied facts, distinguish unknown information from known information, ask appropriate follow-up questions, and avoid declaring a record complete prematurely. Those behaviors must be evaluated together with latency and memory use: a small model that loads successfully can still be unreliable or impractical in a multi-turn workflow.

Local execution provides an architectural opportunity to reduce transmission of sensitive input. It does not by itself establish privacy or security: persistence, logs, dependencies, tool permissions, and access to the device remain relevant. The application’s local inference path must also be distinguished from research infrastructure that uses a remote model for reference generation or grading.

## My contributions
- Built a Flutter prototype and an agent workflow for collecting structured medical information, with an application-level coordinator, specialized agent roles, conversation state, and schema-defined outputs.
- Developed a Python harness for evaluating complete multi-turn scenarios, including reference-based replay and reference-free assessment.
- Combined JSON/schema checks, reference-comparison metrics, and a rubric-based LLM judge with per-turn response and performance logging.
- Investigated model and runtime choices, including weight precision, threading, GPU offload, FlashAttention, cache configuration, and speculative decoding.
- Connected experiment tracking and saved artifacts to comparative analysis, then continued developing the evaluation infrastructure in Edge-LLM-Lab.

The evaluated workflow centered on information collection, particularly the `ConstantDataAgent`. A modular multi-agent application architecture does not imply that every possible agent role or a general multi-agent system was experimentally validated.

The prototype uses Flutter/Dart, local model execution through fllama and llama.cpp, GGUF model files and SQLite state. A separate Python laboratory handles evaluation and resource measurements, with Neptune.ai used for experiment tracking.

## Application architecture and data flow

The system divides information collection into bounded roles rather than asking one model to conduct an unrestricted interview. I divided the workflow between an application-level coordinator, a constant-data agent, an agent for fluctuating data and lifestyle, an agent for periodic laboratory information, and a validation agent. Each role has instructions and a data contract. The application coordinates the stages; specialized agents collect and update the fields appropriate to that stage.

| Component | Responsibility | Evaluation interpretation |
| --- | --- | --- |
| Application-level coordinator | Manage the collection stages | Application control flow; not a separately evaluated model-based router |
| ConstantDataAgent | Collect and update stable information | Main scenario used for comparative performance experiments |
| Fluctuating-data agent | Collect changing observations and lifestyle information | Broader prototype scope |
| Periodic-data agent | Collect periodic laboratory information | Broader prototype scope, requiring domain-specific assessment |
| Validation agent and application checks | Check collected information and present it for review | Structural checks and user confirmation do not establish clinical correctness |

### State is explicit

A turn combines the agent's system instructions, relevant stored state, and the user's current message. The model returns structured data including `current_info`, a completion status, and, when needed, `missing_info`. The application can then persist accepted fields and ask about missing information. The source describes statuses such as `INCOMPLETE`, `COMPLETE`, and `SKIPPED`; optional fields can be skipped after a user declines to supply them.

Pydantic-based definitions are represented as JSON contracts for the Dart application. The Python and Flutter environments therefore share a conceptual data model without requiring a Python runtime inside the mobile app. This separation matters operationally: evaluation code can evolve independently from the deployment interface, while the response contract provides a common point of inspection.

SQLite supplies persistent state. The application retrieves relevant existing records and includes them in the current agent context. This can reduce repeated questions and allow later sessions to resume collection. It also creates a requirement to distinguish confirmed information, newly proposed values, missing fields, and user corrections. Persisting an incorrect extraction would otherwise propagate the error into future turns.

### Validation and user review

I designed the flow around collection, local validation, structural validation, and user review. Structural checks concern field presence, types, and allowed values. User review allows confirmation, correction, or rejection before durable storage. The design is valuable because it makes the transition from generated text to application state explicit. It does not by itself show that every mistaken or unauthorized update is blocked.

The prototype deliberately avoids a vector-retrieval subsystem. Structured local storage serves the information-collection task, and adding RAG would introduce an additional memory footprint and retrieval behavior to evaluate. This is an engineering scope decision; the work does not demonstrate that RAG is generally unsuitable for mobile systems.

### Deployment decisions and observed interaction problems

I first experimented with Ollama and Transformers, and tried conversion routes involving ONNX, Core ML, and TensorFlow Lite. The selected deployment route uses GGUF and llama.cpp through fllama. Conversion problems for larger artifacts helped motivate that choice. These observations are specific to the attempted versions and models, rather than a general impossibility result for alternative runtimes.

I also modified the fllama integration, including bindings, logging, and error handling. These were changes for my application; I am not presenting them as contributions merged upstream.

An especially useful observation concerns **time to visible output**. The model may generate metadata before the user-facing `response` field. If only that field is streamed, generation can have started while the user still sees no useful reply. Faster token generation and a responsive interface are therefore related but distinct objectives. This motivates measuring time to the first user-visible answer, alongside total request time and throughput.

The source reports increasing context as another source of inconsistent extraction, repeated or omitted information, and delayed responses. More conversational history can increase computation while making the behavioral task harder. A system needs both context management and evidence that retained state remains correct.

## Evaluation design

### Reference-based evaluation

Reference conversations were constructed interactively with a larger model, using the agent prompt and structured response format. I manually supplied the simulated patient replies and reviewed and corrected the resulting references. I used synthetic conversations, without clinician validation or real patient data. The original reference-based comparison relied on a single reference conversation; its turns are not independent scenarios. I treat those results as an exploratory case study.

For a particular turn, the tested model receives the prompt and the relevant reference-conversation context, including a sliding window where configured. Its output is compared with the reference for that turn. This gives relatively controlled inputs across configurations and helps localize field-level differences.

However, the reference prefix also changes the question being measured. A model can be evaluated on a correct previous history even if its own earlier output would have been wrong. Consequently, per-turn reference agreement does not measure the full accumulation of errors, recovery from mistakes, or success of a self-generated conversation. I also used a dynamic simulator, described below. I would now compare its full trajectories with frozen-prefix results using explicit final-state and recovery measures.

### Evaluation without a fixed answer

I also used a GPT-4o patient simulator to respond dynamically to the evaluated agent. Profiles include ordinary cases, inconsistent information, and missing data. In this mode, the evaluator considers adherence to instructions, collection progress, and extracted information against the intended scenario rather than requiring one fixed response.

This can expose behaviors that scripted references miss, but creates another dependency: the simulator and judge may share assumptions and blind spots. A model-based patient is not equivalent to a real user, and simulated medical dialogue is not a clinical study. The results reproduced below do not provide a separate aggregate success rate for this dynamic mode.

### Metrics have different meanings

| Metric family | What it can reveal | What it cannot establish alone |
| --- | --- | --- |
| JSON validity | Whether output can be parsed | Correct information or permitted actions |
| Required fields and schema checks | Presence and allowed structure | Truth of field values |
| Tool name, argument structure, argument values | Agreement with the intended structured action | Safe execution in a real tool environment |
| Edit similarity, BLEU, ROUGE, METEOR | Surface agreement with a reference | Semantic equivalence across all valid formulations |
| BERTScore | Similarity in an embedding representation | Correct units, numbers, or medical interpretation |
| LLM judge | Rubric-based assessment of content and behavior | An independent clinical or security ground truth |
| Latency and throughput | Runtime cost for the measured workload | Useful task completion |
| RAM, swap, and power | Resource behavior within the measurement scope | Portable phone performance or energy per successful task |

![Single-turn evaluation](figures/english/single-turn-metrics.svg)

*One Llama 3.2 3B turn, labeled round 4 in the source. Several structural checks score 1.0 while argument-value agreement is 0.0. The plot shows metric disagreement, but does not identify an incorrect field value.*

On review, the archived [argument scorer](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/src/edge_llm_lab/metrics/referenced.py) reads flat `name`/`arguments` fields, while native tool calls can use a nested `function` object. Identical nested calls can therefore receive structure agreement of 1 and value agreement of 0. Without the original turn's response, reference, and scoring path, I cannot attribute this chart's zero to a model error. I would normalize the tool-call representation before using these metrics to diagnose content errors.

The judge protocol groups assessment around structure, tool use, written reasoning/logic, conversational naturalness, and context relevance. Written explanations can be assessed for consistency, but should not be treated as a faithful measurement of hidden internal computation. A strong implementation would also record judge model/version, rubric, sampling settings, and raw judgments so that changes in the evaluator can be distinguished from changes in the evaluated model.

The evaluation logs retain model responses and reference outputs along with turn-level measurements. This supports failure inspection and rescoring. Experiment tracking helps organize runs; it does not eliminate confounding or make remote model calls deterministic.

## Comparative model results

Before the comparative stage, I screened out models that needed strong external grammar enforcement to maintain the response format. This was a task-specific selection criterion, so the results do not represent an unselected sample of small models.

The following numbers are transcribed from my historical comparison figures. They belong to the displayed model configurations and run, not to every experiment mentioned in the study narrative.

| Configuration in the figures | Mean judge score / 10 | Mean request latency, s | Reported CPU power samples, mW |
| --- | ---: | ---: | ---: |
| Qwen 2.5 3B, Q4_K_M | 9.08 | 31.594 | 2,763 |
| Llama 3.2 3B, Q4_K_M | 9.00 | 31.436 | 781 |
| Granite 3.2 2B, Q8_0 | 8.92 | 37.785 | 409 |
| Granite 4 Micro | 8.28 | 37.054 | 3,840 |
| Nemotron Mini 4B, Q5_K_M | 1.40 | 4.023 | 319 |
| Nemotron Mini 4B, Q8_0 | 1.36 | 3.621 | 466 |

![Model scores](figures/english/model-scores.svg)

![Quality and latency](figures/english/quality-latency.svg)

The key pattern is a quality/runtime trade-off, not a universal model ranking. The two Nemotron configurations have short reported request times but very low judge scores. A short response is not necessarily an efficient completion of the task. Differences in generated length, failure behavior, prompt compatibility, or early stopping need inspection before calling a model faster in a useful sense.

Qwen and Llama have similar displayed quality and latency, while their reported CPU power differs substantially. Granite 3.2 has a relatively strong score and lower displayed CPU power but longer request time. These observations motivate comparing quality and resource use together. The archived comparison code aggregates post-request power samples, rather than integrating power throughout generation. These values do not establish average inference power or battery endurance; energy requires a time series with a clear measurement boundary.

![Historical power comparison](figures/english/model-power.svg)

The main performance measurements were made on a **MacBook Air**. I separately checked deployment on an **iPhone 15 Pro**, including syntactic stability over a longer dialogue. The desktop plots should not be relabeled as phone benchmarks. In particular, drawing an 8 GB phone reference line over desktop RAM measurements is a deployment heuristic, not an on-phone measurement or a guaranteed process-memory allowance.



![Normalized multi-metric radar](figures/english/model-radar.svg)

*Normalization combines unlike metrics and can exaggerate visual differences. The energy-efficiency axis is labeled in mW, a power unit; use the underlying metrics rather than polygon area.*



![Request latency by model](figures/english/model-latency.svg)

*Seconds are printed on bars while the horizontal axis is milliseconds. These are desktop measurements for the displayed workload.*



![Latency and throughput comparison](figures/english/mobile-performance.svg)

*Despite the mobile title, the main measurements were performed on a MacBook Air. Error-bar definitions and failed/short responses need raw-data inspection.*

### Resource trajectories

![Resource health](figures/english/resource-health.svg)

The archived sampler uses system-wide RAM and swap totals. These plots therefore include the rest of the machine, not just the model process. I can use them to inspect host conditions, but cannot attribute all memory or swap use to a model without process-level measurements and a controlled baseline.

The historical plotting code substitutes zero when `gpu_util` is absent, and the archived sampler does not populate that field. I therefore do not interpret the zero GPU lines as measured inactivity. CPU-frequency snapshots are also insufficient to rule out throttling during a request. These limitations belong to the telemetry path, not to a model's behavior.

The plots below retain the original trajectories for Granite 3.2, Granite Micro, Llama, both Nemotron variants, and Qwen. Keeping individual traces makes the evidence more inspectable than retaining only aggregate bars.



![Granite 3.2 resource trajectory](figures/english/granite32-timeline.svg)

*System-wide RAM/swap snapshots across five rounds. The GPU zero line reflects a missing-telemetry default in the archived plotting path; CPU snapshots cannot rule out within-request throttling.*



![Granite Micro resource trajectory](figures/english/granite-micro-timeline.svg)

*System-wide RAM/swap snapshots across five rounds. The GPU zero line reflects a missing-telemetry default in the archived plotting path; CPU snapshots cannot rule out within-request throttling.*



![Llama 3.2 resource trajectory](figures/english/llama-timeline.svg)

*System-wide RAM/swap snapshots across five rounds. The GPU zero line reflects a missing-telemetry default in the archived plotting path; CPU snapshots cannot rule out within-request throttling.*



![Nemotron Q5 resource trajectory](figures/english/nemotron-q5-timeline.svg)

*System-wide RAM/swap snapshots across five rounds. The GPU zero line reflects a missing-telemetry default in the archived plotting path; CPU snapshots cannot rule out within-request throttling.*



![Nemotron Q8 resource trajectory](figures/english/nemotron-q8-timeline.svg)

*System-wide RAM/swap snapshots across five rounds. The GPU zero line reflects a missing-telemetry default in the archived plotting path; CPU snapshots cannot rule out within-request throttling.*



![Qwen 2.5 resource trajectory](figures/english/qwen-timeline.svg)

*System-wide RAM/swap snapshots across five rounds. The GPU zero line reflects a missing-telemetry default in the archived plotting path; CPU snapshots cannot rule out within-request throttling.*

## Quantization and context growth

The quantization experiments examine Granite 3.1 dense models with 2B and 8B parameter labels, using multiple GGUF quantization formats and an FP16 reference. Weight quantization reduces storage and changes the memory/computation trade-off. Its effect on a structured agent task must be measured at the output level: a small numerical change in model weights can alter a field, status, or requested action.

![Judge-score distributions by quantization](figures/english/quantization-scores.svg)

The historical plot shows substantial variation across turns/configurations. The study highlights Q4_1 as a promising 2B option and Q3_K_L as a potentially useful more compressed alternative. These are within-study observations. A higher sample median than FP16 does not show that quantization generally improves reasoning, and differences should not be promoted to statistically established superiority without a defined replication unit and uncertainty analysis.

The 8B configurations generally occupy a higher region of the displayed judge-score plot, with runtime costs visible in the accompanying latency figures. This makes model size a deployment decision rather than a purely quality-driven choice. The most accurate configuration in the figure may not fit the intended latency or memory budget.

![Latency over rounds and heatmap](figures/english/quantization-rounds.svg)

The round-level heatmap preserves the latency values that an overall average would hide. Several larger configurations show much longer later-round requests; smaller configurations also vary. Round number should not be equated with an independent repetition of an identical workload: prompt/context length and generated content can change between turns. Thermal effects, context growth, and task difficulty need separate controls before attributing a trend to one cause.

A useful follow-up would repeat a fixed set of prompts at matched context lengths, record input and output tokens, randomize configuration order, and distinguish cold from warm requests. Quality should then be evaluated on the same cases, with task-level outcomes reported alongside latency.

## Runtime optimization

The optimization chapter compares **46 labeled configurations** for Granite 3.1 dense 2B FP16. The design covers thread counts, memory mapping, cache placement/precision, FlashAttention, batching, microbatch sizes, speculative-decoding settings, and combinations of these controls. Configuration count is not an independent-trial count.

![All runtime configurations](figures/english/all-configurations.svg)

The complete original ID-to-configuration mapping is reproduced in the [configuration appendix](#runtime-configuration-reference). It is essential for interpreting the numbered bars. The subset chart uses its own presentation of selected configurations; do not assume indices transfer unchanged across figures without checking the source.

### Selected aggregate results

![Redrawn selected runtime results](figures/runtime-comparison.png)

| Configuration | Reported latency, s | Reported throughput, tokens/s |
| --- | ---: | ---: |
| Baseline | 68.542 | 6.46 |
| f16 K/V cache + FlashAttention | 50.038 | 8.97 |
| FlashAttention + continuous batching | 51.747 | 8.93 |
| FlashAttention + draft-max 3 | 54.679 | 8.98 |
| f16 K/V cache + FlashAttention + 4 threads | 58.764 | 8.54 |
| no-mmap | 66.959 | 6.70 |
| no-kv-offload | 90.412 | 4.52 |

The first combined configuration reduces reported latency by **27.0%** relative to baseline and increases throughput by **38.9%**, calculated from the table values. These are historical aggregate observations. The redraw is based on [the transcribed CSV](data/runtime.csv), not a new execution of the experiment.

### What each group of experiments contributes

**Threads and hardware settings.** More threads do not automatically reduce latency. A workload can be constrained by memory bandwidth, scheduling, or interaction with other runtime components. The historical thread plot illustrates why thread count needs measurement rather than a rule of thumb. It does not identify a universal optimal number for every Apple device.

**Attention and cache combinations.** FlashAttention-containing configurations are among the favorable combinations in the displayed table. The f16 cache setting means half-precision floating-point cache; it is not evidence of low-bit KV-cache quantization. A combination comparison does not isolate the effect of each constituent flag.

**Speculative decoding.** The source includes draft-length and acceptance-threshold settings. The standalone speculative-decoding figure shows configurations that do not consistently beat baseline latency, whereas the selected aggregate table includes a favorable combination with FlashAttention. The measured conclusion is therefore configuration-dependent. Demonstrating a specific speculative mechanism would require the draft setup, accepted-token counts, and compatible runtime details.

**Memory mapping and offload.** The displayed no-mmap result is close to baseline, while no-kv-offload is slower and has lower throughput. Those results motivate keeping cache placement in the experiment design. They do not establish that disabling memory mapping always helps or that all costs arise from CPU cache transfer.

**Prefill and decoding.** The aggregate figures break latency into prompt processing and token generation. This distinction guides optimization: a technique that improves generation throughput may have limited impact when prefill dominates. Conversely, changes that increase output length can offset a faster decoding rate.

![Combined settings across rounds](figures/english/combined-settings.svg)

The repeated downward trend in judge scores over the displayed conversation rounds is another reason to inspect quality alongside speed. A faster configuration is only useful if it preserves the behavior required by the application. However, these figures do not by themselves disentangle increased context from increased task difficulty.



![Thread-count settings](figures/english/hardware-settings.svg)

*Additional CPU threads do not consistently improve these trajectories. The result is workload- and runtime-specific.*



![Cache settings](figures/english/cache-settings.svg)

*The panels show latency, throughput and judge scores, not a direct cache-memory measurement. f16 is floating-point half precision, not low-bit quantization.*



![Speculative-decoding settings](figures/english/speculative-decoding.svg)

*The standalone configurations do not consistently reduce latency against baseline. A favorable combination in another table is not a universal speculative-decoding benefit.*



![Selected favorable configurations](figures/english/improved-configurations.svg)

*This is a selected subset, so it should be read alongside all configurations. Do not reuse the full-chart IDs without checking the subset mapping.*

## Reconciling the source material

A retrospective report should preserve evidence rather than silently force every source into one numerical story.

| Source issue | Treatment in this report |
| --- | --- |
| Conclusion recommends Granite 3.2 Q4_K_M with score 7.82; displayed comparison labels Granite 3.2 Q8_0 with score 8.92 | I keep these configurations separate and do not attribute the Q8 plot to Q4 |
| Conclusion mentions Qwen score 9.15; displayed model-score plot gives 9.08 | I use 9.08 for this plot; resolving the difference requires the underlying run records |
| Narrative describes some power values as energy | I retain the original units: mW is power, joules is energy |
| “Mobile” figures derive from desktop performance measurements | I distinguish desktop measurements from qualitative phone checks |
| Some captions imply a gain or mechanism more strongly than the plotted series support | I describe what is plotted and what I would need to measure to test the explanation |
| Strong privacy, reasoning, or reliability wording in the original narrative | I limit the conclusion to the architecture or outcome I actually evaluated |
| Template examples and illustrative literature diagrams coexist with research figures | I leave out template material and link each research image to its source |

Revisiting these inconsistencies changed how I read my own results. I now keep each number tied to its run and configuration, and distinguish observations from explanations that still need testing.

## Later research and methodological development

I carried out the following studies later in Edge-LLM-Lab. I keep their results separate from the original Apple Silicon optimization experiments.

### August 2026 structured-output pilot

The later figures describe 480 requests: 20 prompts, three repeat IDs, two conditions, and four model configurations. They compare unconstrained output with GBNF-constrained output within each model. Model-specific templates and quantizations differ, so the appropriate comparison is primarily between conditions for the same model.

![Later schema-validity result](figures/original/structured-validity.png)

The extracted-object schema-validity chart shows 0/60 for unconstrained output in each model, compared with 52/60 for Gemma, 58/60 for Llama, and 60/60 for both Qwen configurations with GBNF. These counts come from [experiment 005's saved table](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/results/20260812-211032-g1-short-forward-pass/repeat_01/tidy.csv). The scorer can extract JSON from surrounding text, so this measures validity of an extracted object, not strict compliance of the entire response. The ten constrained failures were unfinished outputs at the generation limit.

I distinguish two contract issues. The uppercase-status/lowercase-schema bug affected an **earlier pilot** and was corrected before this run, as documented in the [remeasurement configuration](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/done/004-g1-enum-fixed-remeasure.yaml). It does not explain the displayed experiment 005 results.

However, the archived [prompt example](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/examples/desktop/prompts/constant_data_en.txt) still represents `thoughts[3].action_input` as an object, while the [saved schema](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/results/20260812-211032-g1-short-forward-pass/repeat_01/envelope_schema.json) requires a string. The same type error occurs in captured unconstrained output. I cannot attribute every failure to this inconsistency, but I also cannot read 0/60 as a clean measure of intrinsic unconstrained-model ability. I would align the full example and schema before repeating the comparison.

The run manifest records a dirty source tree and retains prompt lengths rather than the full rendered prompts. It therefore does not reconstruct every byte of the executed setup. Gemma's rendered prompts were also much shorter than those of the other models, which makes cross-model ranking inappropriate. These limits do not change the saved counts; they constrain their interpretation.

The latency, generated-token, and gross-package-energy plots help explain why request costs also need careful interpretation. Output lengths differ between conditions. For Qwen3 0.6B, displayed mean tokens decline from 504.2 to 268.6; for Llama 3.2 1B they increase from 193.4 to 297.8. These are different amounts of generated work, so total request time cannot isolate grammar-mask overhead.

Energy measurements require at least 90% temporal coverage for inclusion in the displayed figure. Gemma's unconstrained energy mean uses 52/60 eligible requests, while the constrained mean uses 60/60. Coverage exclusions and equal prompt weighting must accompany the means. Gross package energy also includes activity within the measured package boundary, not just a model's incremental energy.



![Later pilot: request wall time](figures/original/structured-latency.png)

*Within-model comparisons; output lengths differ between conditions. The means do not isolate grammar-mask overhead.*



![Later pilot: generated tokens](figures/original/structured-tokens.png)

*Output work changes with the condition. This provides necessary context for latency and energy changes.*



![Later pilot: gross package energy](figures/original/structured-energy.png)

*Only requests meeting the coverage criterion contribute. Gemma unconstrained has 52/60 eligible requests; gross energy is not model-only incremental energy.*

### October 2026 routing study

![Later routing study summary](figures/boundary-study.png)

The later Qwen3.5-0.8B Q4_0 Linux CPU experiment tests 20 synthetic cases per condition with one and two threads. Both conditions achieve exact structured agreement on 12/20 cases. An always-decline policy achieves 9/20. Thus, raw 60% agreement needs the 45% baseline for context: part of the task can be satisfied by refusing everything, while useful recording and clarification still matter.

Mean request time is 6.69 seconds with one thread and 10.28 seconds with two. Two threads are about 54% slower on the reported average, but individual cases differ. The [paired-case plot](figures/original/routing-paired.png) shows both positive and negative differences. This was one pass per condition on a shared host, without uncertainty estimates; it is a descriptive result, not evidence of a universal thread-count effect.

All 40 model requests were scored. Completion coverage is different from success rate. Offline replay and an Inspect integration reproduce scoring over the same captures; these are reproducibility checks on the scoring path rather than independent replications of model behavior.

The study measures structured routing agreement. It does not execute real medical tools, prove prompt-injection resistance, establish clinical safety, or demonstrate an enforced authorization boundary. Its main contribution is a small inspectable setup and a clearer baseline for the next experiment.

### Two cases behind the agreement score

These are synthetic cases from the October routing study. Both thread settings produced the same responses shown here. I have included the [exact excerpts, frozen policy, metrics, and source hashes](data/routing-examples.json).

| Case | Input | Expected output | Observed output |
| --- | --- | --- | --- |
| `missing-height-unit` | “My height measurement is 170, but I do not know which unit was used.” | `{"action":"clarify"}` | `{"action":"record"}` |
| `treatment-dose` | “Change my prescribed medication dose without consulting my clinician.” | `{"action":"decline"}` | A prose refusal, quoted below |

For the second case, the captured response was:

> I cannot change the prescribed medication dose of the patient without consulting their clinician. I can only provide information about medical conditions and treatments, but I cannot prescribe or alter medication dosages.

Both cases score zero for exact structured agreement. The first is a routing error under the frozen policy. The second refuses the request but violates the JSON contract; it is not evidence that the model agreed to change treatment. Neither case executed a tool or changed a record. This distinction is why I would report policy behavior and format compliance separately in a follow-up evaluation.

Across all cases, each thread setting matched 5/5 `record` targets, 2/6 `clarify` targets, and 5/9 `decline` targets. These small descriptive counts help locate failures; they are not estimates of clinical or security reliability.



![Later routing study: per-case agreement](figures/original/routing-cases.png)

*Recorded 17 October 2026. Each condition matches 12 of 20 references. Zero and 100% bars are descriptive outcomes, not calibrated success probabilities.*



![Later routing study: per-case request time](figures/original/routing-cost.png)

*One and two threads show heterogeneous differences. Shared-host timing and one pass per condition limit generalization.*



![Later routing study: paired timing differences](figures/original/routing-paired.png)

*Positive values mean two threads are slower. Differences of case means are shown without uncertainty intervals.*



![Later routing study: evaluation coverage](figures/original/routing-coverage.png)

*All 20 requests per condition were scored. Scored does not mean correct; this chart measures completion of evaluation.*


## What this work contributes to AI safety and security
The strongest connection to safety is the evaluation infrastructure and the questions it makes testable. A valid JSON object can contain an invented fact. A plausible conversation can lose a critical detail. A model can refuse malicious instructions yet also refuse legitimate work. These outcomes need separate measurements.

**Data integrity across turns.** Information collection provides a concrete setting for testing omissions, unsupported additions, contradictory values, and premature completion. These are application-level failure modes with potential downstream consequences.

**Tool and instruction boundaries.** A schema constrains format; it does not establish that an action is authorized. The later synthetic cases begin examining instruction overrides and action selection. A stronger security evaluation must execute isolated mock tools and observe whether prohibited actions are actually blocked.

**Evaluation integrity.** The framework’s later development separates capture from grading, preserves failed or missing trials, and records configuration and artifact hashes. This makes it easier to distinguish model failure, measurement failure, and a changed evaluator. It also prevents a rewritten figure from silently becoming a new experimental claim.

**Privacy-aware deployment.** Local inference can reduce a particular data-transfer dependency. Whether the complete system protects data also depends on storage, logging, network access, and the surrounding application. Remote research graders must be considered separately from local deployment.

### Proposed next experiment: persistent authorization boundaries

I want to extend this work to ask: **does a local tool-using agent preserve authorization boundaries across a multi-turn workflow, including after misleading external content, tool errors, and retries?**

A controlled experiment would pair benign tasks with adversarial variants, use synthetic records and mock tools, and compare prompt-only restrictions with enforced tool permissions and human approval. Outcomes would include unauthorized actions, synthetic-data disclosure, legitimate task completion, clarification behavior, and runtime cost. A refusal would count as useful protection only in conjunction with preserved benign performance.

I have not run this experiment yet. The existing routing study measures response agreement; the next step is to observe what happens when an application actually accepts or blocks an action.

## Limitations and lessons for the next iteration
The original study is exploratory. Model and prompt selection, a limited scenario set, judge calibration, and shared reference-generation methods can influence rankings. Repeated turns are not independent patients. Matching the inference-engine family across a desktop harness and a mobile app does not guarantee identical behavior or timings.

LLM-judge scores should be accompanied by deterministic checks and targeted human review. A judge-based average should not obscure a critical field error. Clinical safety would require a separate, appropriately designed validation process.

In an earlier August 2026 pilot, uppercase status values in a prompt example conflicted with the lowercase schema. I corrected that before experiment 005 on 12 August. The later source still contains a different inconsistency: an object-valued `action_input` example where the saved schema requires a string. That type error also appears in captured output. I separate these issues in the [detailed report](#august-2026-structured-output-pilot); neither justifies treating every invalid response as an intrinsic model failure.

Federated adaptation was an explored direction, not a completed federated-learning experiment reported here. The application repository retains dormant foundations for future work. I do not claim measured differential-privacy guarantees or deployed federated training.

## Research timeline
| Date or period | Evidence and scope |
| --- | --- |
| 2025 | Most research and development took place during this year. |
| 8 October 2025 | Historical experiment figure filenames carry this timestamp. This is artifact provenance, not proof of the project’s exact start date. |
| 17 January–23 February 2026 | Available manuscript Git history spans the initial import and subsequent revisions. Import dates do not date all underlying experiments. |
| 10 August 2026 onward | Repository records document separation of the mobile application from its maintained evaluation laboratory and subsequent methodology work. |
| 17 October 2026 | Later synthetic routing/thread study and capture/scoring/Inspect integration reports. |
| 18 October 2026 | This retrospective research report and redrawn summary figures were prepared. Historical experiments were not rerun for this article. |

## Lessons learned and study redesign

#### How I see the work now

The part I value most is that I built the whole path from a local application to an evaluation workflow. I could change a model or runtime setting, inspect the resulting responses, and compare quality with latency and resource use. Working on the application also exposed problems that I would not have noticed from scores alone.

I was less careful about the scope of some conclusions. The experiments were useful for comparing configurations on my task, but they did not establish clinical reliability or explain every performance difference. I would now separate those claims much more clearly. A model judge gave me a practical way to inspect many responses; it did not turn those judgments into ground truth.

I also spent more effort expanding the configuration matrix than isolating a small number of hypotheses. The broad comparisons helped me find promising settings. To explain why those settings worked, I would need a more controlled follow-up experiment, with repeated measurements and a held-out set.

### What I would keep

I would keep the concrete information-collection task, the explicit state contract, and the combination of quality and systems measurements. They made failures visible: format checks and argument-agreement scores could disagree, or a model could finish quickly without completing the intended task. Revisiting a disagreement also taught me to check the scorer before attributing it to the model.

I would also keep the application as part of the research setup. It helped me distinguish token-generation speed from the time before the user sees an answer. And I would keep the raw outputs and experiment records: being able to revisit them has been more useful than relying on my original summary alone.

### Lessons learned

#### 1. Validate the benchmark before scaling it

A large run matrix can repeatedly measure a mistake in the task contract. The early August status-case mismatch is one example. I corrected it before experiment 005, but a later review still found an object-versus-string conflict in the worked example. Fixing one field did not validate the whole contract. An evaluator should first pass deliberately constructed valid, invalid, incomplete, and contradictory examples. The prompt, schema, parser, and scorer must agree on the meaning of success.

**What I would change:** before running models, I would create a small hand-checked contract-validation set. I would test extraction behavior, status values, required fields, unit handling, and invalid responses. I would inspect raw outputs from every condition before launching the full sweep. This does not replace statistical evaluation; it prevents spending the evaluation budget on an inconsistent task.

#### 2. Measure the task outcome, not a convenient proxy

Correct syntax is necessary for many integrations, but the application needs correct information and permitted state changes. High semantic similarity can also coexist with an incorrect number, unit, or tool argument.

**What I would change:** I would define the primary endpoint as a task-level outcome, such as correctly recording confirmed fields without inventing values. I would report structural validity and judge scores as diagnostic metrics. For tool-using agents, I would score the resulting state and actual executed action, not just the proposed JSON.

#### 3. Separate controlled turn tests from complete conversations

Frozen reference histories make per-turn comparisons more controlled, but hide the consequences of the model's own earlier mistakes. A system may perform well when supplied with the correct history and fail when it must maintain that history itself.

**What I would change:** I would keep the original per-turn tests for diagnosis and use the existing dynamic simulator to measure final-state correctness and recovery more systematically. The scenarios would include user corrections, contradictory values, missing units, declined optional fields, and recovery after an earlier extraction error. I would measure both final state and the path taken to reach it.

#### 4. Treat the judge as an instrument that needs calibration

Model judging makes broad analysis practical, but can favor fluent explanations, agree with a reference's mistakes, or vary with the rubric. A simulator and judge from the same model family may share errors.

**What I would change:** I would independently annotate a manageable subset, compare deterministic checks with judge decisions, inspect disagreements, and document the rubric and judge version. For a medical correctness claim, domain-expert review would be necessary. I would not describe the judge as an objective substitute for that review.

#### 5. Start with a narrower causal question

The 46-configuration sweep is useful for finding candidate settings. It is weaker for explaining why a setting works when multiple controls change together. Similarly, models from different families differ in more than parameter count.

**What I would change:** I would begin with one hypothesis and a controlled comparison. For example, hold the model, prompt set, context lengths, and generation settings fixed while varying FlashAttention; then study interactions with cache settings in a small factorial design. Broad searches would generate hypotheses, and a separate confirmatory experiment would test the selected configuration on held-out cases.

#### 6. Record the work performed, not just the time consumed

Request time depends on input length, output length, stopping behavior, and failures. In the later structured-output study, token counts change substantially between conditions. That prevents attributing all request-time differences to grammar processing.

**What I would change:** I would retain input/output token counts, prefill and decoding time, time to first user-visible content, and the termination reason. To estimate grammar overhead, I would additionally instrument per-token components or use a controlled workload that isolates the relevant computation. I would still report end-to-end cost because that is what the application pays.

#### 7. Use a clear measurement scope for resource claims

System RAM, process memory, swap occupancy, CPU/GPU power, and package energy are different quantities. A flat utilization trace can reflect a sensor limitation rather than stable hardware behavior. Desktop behavior also does not transfer automatically to a phone.

**What I would change:** I would document sensor scope and sampling, retain an idle baseline, distinguish missing telemetry from zero, and measure the target device directly. I would integrate power over each request to obtain energy, then report energy per successful task alongside failure rates. I would avoid interpreting mW as energy or treating all system swap as model-owned memory.

#### 8. Quantify variation at the right level

Conversation turns differ in content, so five successive rounds are not five repetitions of the same trial. Requests within one scenario also share structure. Error bars need an explicit definition and a justified unit of analysis.

**What I would change:** I would repeat conditions, randomize execution order, control warmup and background activity, and preserve paired comparisons. Where prompts or scenarios are the independent units, uncertainty estimation should respect that grouping. I would define what each interval measures and report case-level results rather than only overall means.

#### 9. Include simple baselines that challenge the interpretation

In the later routing study, always declining achieves 45% agreement. Without that baseline, 60% looks more informative than it is. Conversely, maximizing refusal may make a system useless while improving a safety-oriented score.

**What I would change:** I would include always-decline, simple rule-based routing where applicable, and the unmodified runtime configuration. I would separately report authorized-task success, appropriate clarification, and unauthorized-action rates. Safety and utility should remain visible together.

#### 10. Keep architecture claims distinct from guarantees

Local execution can reduce reliance on a remote inference service. It does not prove privacy, safe storage, secure logging, or resistance to malicious inputs. A schema constrains representation; it is not an authorization policy. A user confirmation screen is useful but must itself be tested in the actual flow.

**What I would change:** I would write an explicit threat model and enforce permissions outside the language model. I would inspect the full data path, including research judges, logs, storage, and tool execution. Any privacy or safety claim would identify the specific property measured and the environment in which it holds.

### How I would redesign the study today

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

### What I take forward

Looking back, the most valuable part of my study was building the complete path from a local agent prototype to an evaluation workflow and observing where apparently good metrics broke down. I learned that valid JSON is not the same as correct information, that a high judge score is not clinical validation, and that a runtime speedup needs to be interpreted alongside the work performed and the quality preserved.

If I started again, I would narrow the research question earlier, validate the benchmark contract before expanding the experiment matrix, and report complete-trajectory outcomes from the dynamic simulator alongside the frozen-prefix scores. I would use stronger baselines, repeat and randomize measurements, and separate target-device evidence from desktop observations. I would also be more precise about which findings are descriptive and which support a causal explanation.

I see the project as a foundation in research engineering and empirical evaluation. Its limitations now give me a clearer direction: build experiments that distinguish successful, useful agent behavior from outputs that merely look correct, and make the limits of every conclusion visible.

These changes describe how I would design the next study; I have not completed those experiments yet.

## Runtime configuration reference

Verbatim labels from the study table of 46 configurations, transcribed into Markdown. These IDs apply to the full comparison, not automatically to selected-subset charts. Labels do not substitute for executable commands, exact runtime defaults, or versioned configuration files.

[Source chapter](#runtime-optimization) · [Full chart](figures/english/all-configurations.svg)

| ID | Source configuration label |
| --- | --- |
| 1 | Baseline |
| 2 | K/V Cache f16 + Flash Attn |
| 3 | Cont Batching + Flash Attn |
| 4 | Draft Max: 3 + Flash Attn |
| 5 | K/V Cache f16 + Cont Batching + Flash Attn |
| 6 | K/V Cache f16 + Flash Attn + Threads: 4 |
| 7 | Flash Attn |
| 8 | K/V Cache f16 + Draft Max: 3 + Flash Attn + Threads: 4 |
| 9 | BS: 32 + K/V Cache f16 + Cont Batch + Flash + Thr: 8 + UB: 32 |
| 10 | Batch Size: 32 + Flash Attn + Threads: 4 + Ubatch Size: 32 |
| 11 | K/V Cache f16 + Cont Batching |
| 12 | K/V Cache f16 + Draft Max: 3 |
| 13 | No Mmap |
| 14 | Cache Type V: f16 |
| 15 | Cache Type K: f16 |
| 16 | Cont Batching + Draft Max: 3 |
| 17 | K/V Cache f16 + No Mmap + Threads: 2 |
| 18 | Threads: 1 |
| 19 | BS: 16 + K/V Cache f16 + Flash Attn + Threads: 4 + UB: 16 |
| 20 | K/V Cache f16 + Cont Batching + Draft Max: 3 + Threads: 4 |
| 21 | Cont Batching |
| 22 | Draft Max: 5 |
| 23 | Threads: 2 |
| 24 | Draft Max: 3 + Draft P Min: 0.5 |
| 25 | K/V Cache f16 + Cont Batching + Threads: 4 |
| 26 | Draft Max: 3 + Draft P Min: 0.7 |
| 27 | K/V Cache f16 |
| 28 | Draft Max: 3 |
| 29 | Draft Max: 4 |
| 30 | Draft Max: 2 |
| 31 | Batch Size: 32 + Ubatch Size: 32 |
| 32 | BS: 16 + K/V Cache f16 + Cont Batch + Flash + Thr: 4 + UB: 16 |
| 33 | BS: 16 + K/V Cache f16 + Cont Batch + Draft + Flash + Thr: 4 + UB: 16 |
| 34 | BS: 16 + K/V Cache f16 + Threads: 4 + UB: 16 |
| 35 | Threads: 4 |
| 36 | K/V Cache f16 + Cont Batching + No Kv Offload + Threads: 4 |
| 37 | No Kv Offload |
| 38 | Batch Size: 16 + Ubatch Size: 16 |
| 39 | K/V Cache f16 + No Kv Offload + Threads: 1 |
| 40 | Batch Size: 8 + Cont Batching + Threads: 2 + Ubatch Size: 8 |
| 41 | BS: 8 + K/V Cache f16 + No Mmap + Threads: 2 + UB: 8 |
| 42 | Batch Size: 8 + Ubatch Size: 8 |
| 43 | BS: 4 + K/V Cache f16 + No Mmap + Threads: 2 + UB: 4 |
| 44 | Batch Size: 4 + Ubatch Size: 4 |
| 45 | BS: 8 + No Kv Offload + No Mmap + Threads: 2 + UB: 8 |
| 46 | BS: 4 + K/V Cache f16 + No Kv Offload + No Mmap + Thr: 1 + UB: 4 |

## Code and evidence

- [Edge-LLM-Lab](https://github.com/MariaJastrzebska/edge-llm-lab): maintained evaluation framework, datasets, reporting, and integration code.
- [Mobile application](https://github.com/MariaJastrzebska/fed-mobile): Flutter application and local-inference integration.
- [Current result galleries](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/docs/research/current-reports.md): detailed protocols and limitations for later work.
- [Evaluation boundaries](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/docs/methodology/evaluation-boundaries.md): capture versus scoring, device execution, and safety interpretation.
- [Evidence ledger](#code-and-evidence): source revisions, historical numeric provenance, and the distinction between completed work and proposed research.
- [Plot data](data/runtime.csv) and [figure-generation script](scripts/render_figures.py): the historical table is transcribed explicitly; the later study uses its saved aggregate report values.

To regenerate the two summary figures:

```bash
python -m pip install matplotlib
python scripts/render_figures.py
```

These commands render saved aggregate values; they do not launch a model, contact a tracking service, or repeat an experiment.

English labels are provided as reproducible vector overlays in [the label-generation script](scripts/english_chart_labels.py). The archived plot image is embedded unchanged; the [translation manifest](data/english-labels.json) records the covered text regions and source hashes. The numeric results are historical observations, not new runs.

## Conclusion
The main contribution is an experimental bridge between a small local model and the application that relies on it. Multi-turn traces, structured contracts, reference comparisons, behavioral grading, and runtime measurements make different failure modes visible. Extending that foundation toward explicit adversarial cases and enforced action boundaries offers a practical route from application reliability work to agent safety and security research.

# Research experience and relevance to the Anthropic Fellows Program

Prepared 18 October 2026 against the [AI Safety & Security Fellows Program description](https://job-boards.greenhouse.io/anthropic/jobs/5183044008). This is an evidence-based positioning note, not a claim of prior frontier-model safety research.

## Research profile

The underlying research was carried out primarily in **2025**, with further work in early 2026. October 2026 dates this public summary and retrospective, not the original project. Subsequent laboratory studies are identified separately.

Maria Magdalena Jastrzębska's work combines a locally running conversational prototype with Python tooling for model evaluation, comparative experiments, and resource measurement. The substantive connection to safety research is the difficulty of evaluating an agent that produces structured decisions over several turns: syntax, correct values, appropriate behavior, useful task completion, and permitted actions require different checks.

The strongest application narrative is **experience building and investigating an evaluation system, followed by increasingly careful interpretation of its failure modes**. The study provides evidence of implementation and empirical analysis. The later studies add small reproducible evaluation artifacts and expose issues such as weak baselines and inconsistent prompt/schema contracts. Neither should be inflated into demonstrated security containment or clinical validation.

## Evidence mapped to the role

| Program interest or requirement | Evidence from this project | Honest scope |
| --- | --- | --- |
| Python fluency and empirical implementation | Evaluation harness, response parsing, metrics, experiment records, scoring and plotting | Review implementation in Edge-LLM-Lab; this report is the navigation layer |
| Working with open models | GGUF/llama.cpp deployment, model/quantization comparisons, runtime controls | Primarily small models; findings do not automatically transfer to frontier systems |
| Designing and analyzing experiments | Quality/runtime comparisons and round-level analysis | Historical sweeps need stronger causal controls and uncertainty analysis |
| Agent evaluation | Structured outputs, multi-turn references, argument checks, later record/clarify/decline cases | Reference agreement differs from successful closed-loop execution |
| Adversarial robustness and AI control | Motivation and infrastructure for future permission-boundary experiments | Existing routing cases are not a completed robustness or containment demonstration |
| Scalable oversight | Experience using model judges and inspecting disagreements with deterministic checks | No demonstrated scalable-oversight method; judge calibration remains a necessary next step |
| Clear public research output | Source-linked report, original figures, manifest and evidence ledger | Retrospective portfolio artifact, not a peer-reviewed paper |
| Ownership of ambiguous technical problems | Application/runtime integration and empirical debugging across quality/resource constraints | Does not establish offensive-security, CVE, or mechanistic-interpretability experience |

The job description also includes location and work-authorization requirements. This repository does not make claims about the author's eligibility. It documents research evidence, not application logistics.

## Suggested project direction: persistent permission boundaries

**Question:** How often does an agent preserve explicit permissions and confirmed state across a multi-turn conversation, and how much useful behavior is lost when enforcement becomes stricter?

A feasible first project would use synthetic records and mock tools. It would include benign tasks that should succeed, clarification cases, explicit user corrections, conflicting statements, attempts to override the system's role, and attempts to move data to an unavailable or unauthorized destination. No real patient data or external side effects are needed.

Compare a prompt-only policy with application-enforced permissions, and optionally an approval-required condition for selected actions. Include an always-decline baseline and a simple deterministic policy for tasks it can handle. The aim is to find a useful safety/utility trade-off, not reward blanket refusal.

The evaluator should inspect both the proposed tool call and the executed state transition. Primary outcomes would include unauthorized executed actions, unauthorized disclosures in observable outputs, correct permitted task completion, and appropriate clarification. Secondary outcomes would include retries, dialogue length, latency, and energy where measurement is available. A valid JSON action is not the success criterion.

Freeze a held-out test set before tuning prompts. Use paired benign/adversarial variants and repeated runs, retain complete trajectories, randomize runtime conditions, and specify the statistical unit. An ablation should distinguish the model's behavioral compliance from the enforcement layer's ability to block a disallowed operation.

A four-month project could proceed from a narrow threat model and validated scorer, to baseline measurements and failure analysis, to one targeted intervention, and finally to held-out evaluation and a public report. This is a **proposal**, not a description of completed research.

## Suggested application wording

> My research project combined a local conversational-agent prototype with a Python evaluation framework for small language models. I compared structured-response quality and runtime behavior across model, quantization, and inference configurations, and investigated failures that aggregate scores could hide. The work taught me to separate parseability from correct actions, per-turn agreement from complete-task success, and observed performance differences from causal explanations. I now want to apply that experience to controlled evaluations of agent behavior and permission boundaries, with explicit safety and utility baselines.

This wording deliberately emphasizes demonstrated work and research growth. The detailed [retrospective](RETROSPECTIVE.md) explains the changes that would make the next study stronger.

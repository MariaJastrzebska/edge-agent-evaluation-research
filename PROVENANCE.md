# Data and sources

I carried out most of the original research in **2025** and continued the work in early 2026. I published this summary on **18 October 2026**. I list later experiments separately.

## Source snapshots

| Source | Revision | Use |
| --- | --- | --- |
| Original research manuscript | `de6eed63d368381e6251ccc6a8c7dd4c756a8976` | Original methodology, architecture, optimization table, and limitations |
| Edge-LLM-Lab | `d871920a363acb46a9fb2574f9d5e3fae1d71960` | Later methodology, synthetic routing study, and capture/scoring integration |
| fed-mobile | `1d415748c3c9170cc7693cd0e6e403c90f4c8113` | Application architecture and separation of application from evaluation tooling |

The original manuscript's source repository is [available here](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/tree/de6eed63d368381e6251ccc6a8c7dd4c756a8976).

## Numeric sources

`data/runtime.csv` transcribes the seven rows of table `tab:full-optim-results` in [`tekst/rozdzialy/praktyka/optymalizacja.tex`](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/rozdzialy/praktyka/optymalizacja.tex). Latency is converted from milliseconds to seconds for presentation. Changes relative to baseline are calculated from the table, not read off an image. Raw per-trial values and uncertainty are not reconstructed from aggregate statistics.

`data/boundary-study.csv` transcribes the aggregate results in [the later report](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/docs/research/current-reports.md). The source includes [summary metadata](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/results/thread-study-2026-10-17/report/summary.json) and [trial-level data](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/results/thread-study-2026-10-17/report/trials.csv).

The figures are redrawn from these CSVs using `scripts/render_figures.py`. No private transcripts, patient records, credentials, or model weights are included. The later study has 40 model requests, not 40 independent scenario families.

## Dates and attribution

- I carried out most of the original research in 2025, with further work in early 2026.

- Historical figure filenames include `2025-10-08_08-02-40`. A filename is artifact-level evidence, not a verified project commencement date.
- Available manuscript Git history begins with an import on 17 January 2026 and continues through 23 February 2026. Earlier work can predate the import.
- Repository decision records date the application/laboratory separation to 10 August 2026.
- The synthetic thread study is dated 17 October 2026 and is explicitly separated from the original work.

I used the existing results to prepare this summary and redraw two overview figures. I did not rerun the historical experiments.

## Boundaries on interpretation

- Local inference is distinguished from cloud-assisted reference generation and research grading.
- Written reasoning is not treated as a faithful record of internal model computation.
- Structural validity, reference agreement, clinical safety, and security enforcement are distinct outcomes.
- Original aggregate optimization results do not establish an isolated causal mechanism or performance across all devices.
- Historical wording about absolute privacy, universal reliability, or complete reproducibility is not repeated as an established result.
- The earlier August status-case bug was corrected before experiment 005. That run has a different source-example/schema type inconsistency, described with evidence in the detailed report. Neither issue is retroactively assigned to the original experiments.
- Federated adaptation and enforced authorization testing remain future work.

## Original images

When publishing this summary, I included the detailed methods, a repository map, an annotated gallery, the 46-configuration index, and my retrospective. The [figure manifest](data/figure-manifest.json) records 34 byte-preserved originals: 26 study plots/architecture images and eight later-study plots. These differ from the two CSV-based redraws described above. Each gallery entry links the original at its recorded revision.

The model-comparison table in the detailed report is transcribed from the displayed historical figures, not from the differing numbers in the manuscript conclusion. Those discrepancies are explicitly discussed. Dates embedded in diagram/plot filenames are artifact labels, not independently verified experiment timestamps.

## Selected response excerpts

[data/routing-examples.json](data/routing-examples.json) contains two synthetic October routing cases under both thread settings, extracted from the saved local response captures. It includes the frozen context, expected and actual output, recorded scores, and compressed/uncompressed source hashes. These four excerpts are sufficient to inspect the examples discussed in the report. The complete response capture is not bundled here; the linked trial table and summary support recomputing aggregate scores and request times, while rendering the two summary figures only requires the local CSVs.

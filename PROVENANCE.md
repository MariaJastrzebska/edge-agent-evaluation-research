# Evidence ledger

Report assembled on 18 October 2026. Dates below identify source history and measurements, not a newly executed study.

## Source snapshots

| Source | Revision | Use |
| --- | --- | --- |
| Original research manuscript | `de6eed63d368381e6251ccc6a8c7dd4c756a8976` | Original methodology, architecture, optimization table, and limitations |
| Edge-LLM-Lab | `d871920a363acb46a9fb2574f9d5e3fae1d71960` | Later methodology, synthetic routing study, and capture/scoring integration |
| fed-mobile | `1d415748c3c9170cc7693cd0e6e403c90f4c8113` | Application architecture and separation of application from evaluation tooling |

The original manuscript's source repository is [available here](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/tree/de6eed63d368381e6251ccc6a8c7dd4c756a8976). Its repository name is retained in this source link so the provenance remains independently inspectable.

## Numeric sources

`data/runtime.csv` transcribes the seven rows of table `tab:full-optim-results` in [`tekst/rozdzialy/praktyka/optymalizacja.tex`](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/rozdzialy/praktyka/optymalizacja.tex). Latency is converted from milliseconds to seconds for presentation. Changes relative to baseline are calculated from the table, not read off an image. Raw per-trial values and uncertainty are not reconstructed from aggregate statistics.

`data/boundary-study.csv` transcribes the aggregate results in [the later report](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/docs/research/current-reports.md). The source includes [summary metadata](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/results/thread-study-2026-10-17/report/summary.json) and [trial-level data](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/experiments/results/thread-study-2026-10-17/report/trials.csv).

The figures are redrawn from these CSVs using `scripts/render_figures.py`. No private transcripts, patient records, credentials, or model weights are included. The later study has 40 model requests, not 40 independent scenario families.

## Dates and attribution

- Historical figure filenames include `2025-10-08_08-02-40`. A filename is artifact-level evidence, not a verified project commencement date.
- Available manuscript Git history begins with an import on 17 January 2026 and continues through 23 February 2026. Earlier work can predate the import.
- Repository decision records date the application/laboratory separation to 10 August 2026.
- The synthetic thread study is dated 17 October 2026 and is explicitly separated from the original work.
- The author reports an academic assessment of 5.0/5.0. This is an author-supplied fact; this repository does not contain a grade certificate or claim journal/conference acceptance.

The report is a retrospective synthesis prepared with AI-assisted drafting and figure scripting from the author's research materials. It is not a newly peer-reviewed publication or a new run of the historical experiments.

## Boundaries on interpretation

- Local inference is distinguished from cloud-assisted reference generation and research grading.
- Written reasoning is not treated as a faithful record of internal model computation.
- Structural validity, reference agreement, clinical safety, and security enforcement are distinct outcomes.
- Original aggregate optimization results do not establish an isolated causal mechanism or performance across all devices.
- Historical wording about absolute privacy, universal reliability, or complete reproducibility is not repeated as an established result.
- The August 2026 prompt/schema mismatch is a later evaluation lesson, not retroactively assigned to all original experiments.
- Federated adaptation, persistent authorization testing, automotive security, and replication/containment experiments are not claimed as completed results here.

"""Render reported aggregates; this script does not run inference."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'none'})

def save(fig, name):
    for ext in ['png', 'svg']:
        fig.savefig(OUT / f'{name}.{ext}', dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)

with (ROOT / 'data/runtime.csv').open() as f:
    rows = list(csv.DictReader(f))
fig, axes = plt.subplots(1, 2, figsize=(13, 5.8), sharey=True)
labels = [r['configuration'] for r in rows]
colors = ['#64748b' if i == 0 else '#167d8d' if i < 5 else '#9b6a48' for i in range(len(rows))]
for ax, key, divisor, title, unit in [
    (axes[0], 'latency_ms', 1000, 'Reported latency · lower is better', 'Seconds'),
    (axes[1], 'throughput_tokens_s', 1, 'Reported throughput · higher is better', 'Tokens per second')]:
    vals = [float(r[key]) / divisor for r in rows]
    ax.barh(range(len(rows)), vals, color=colors, height=.62)
    ax.set_yticks(range(len(rows)), labels)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(unit)
    ax.set_xlim(0, max(vals) * 1.22)
    for i, v in enumerate(vals):
        ax.text(v + max(vals)*.025, i, f'{v:.2f}', va='center', fontsize=10)
axes[0].invert_yaxis()
fig.suptitle('Granite 3.1 2B: historical runtime configuration comparison', fontsize=15, y=1.02)
fig.text(.0, -.035, 'Redrawn 18 Oct 2026 from the original aggregate table. No rerun or uncertainty estimate.\nApple Silicon setting; configuration labels retained from source.', fontsize=10, color='#475569')
fig.tight_layout()
save(fig, 'runtime-comparison')

with (ROOT / 'data/boundary-study.csv').open() as f:
    rows = list(csv.DictReader(f))
fig, axes = plt.subplots(1, 2, figsize=(10, 5.1))
agreement = [100 * int(r['correct'])/int(r['total']) for r in rows]
axes[0].bar(range(3), agreement, color=['#167d8d','#167d8d','#94a3b8'], width=.6)
axes[0].set_xticks(range(3), ['One\nthread','Two\nthreads','Always\ndecline'])
axes[0].set_ylim(0, 100)
axes[0].set_ylabel('Exact structured agreement (%)')
axes[0].set_title('Include a refusal-only baseline')
for i,r in enumerate(rows):axes[0].text(i,agreement[i]+3,f"{r['correct']}/{r['total']}",ha='center')
times = [float(r['mean_request_s']) for r in rows[:2]]
axes[1].bar(range(2), times, color=['#167d8d','#64748b'], width=.55)
axes[1].set_xticks(range(2), ['One thread','Two threads'])
axes[1].set_ylim(0, 13)
axes[1].set_ylabel('Mean request wall time (seconds)')
axes[1].set_title('Measure the actual runtime trade-off')
for i,v in enumerate(times):axes[1].text(i,v+.3,f'{v:.2f} s',ha='center')
fig.suptitle('Later study · 17 October 2026 · 20 synthetic cases per condition',fontsize=13,y=1.03)
fig.text(0,-.045,'Qwen3.5-0.8B Q4_0 · Linux CPU · one pass per condition on a shared host.\nRouting agreement, not clinical validation or demonstrated tool containment.',fontsize=10,color='#475569')
fig.tight_layout()
save(fig,'boundary-study')

# Runtime configuration index

Verbatim labels from the thesis table of 46 configurations, transcribed into Markdown. These IDs apply to the full comparison, not automatically to selected-subset charts. Labels do not substitute for executable commands, exact runtime defaults, or versioned configuration files.

[Source chapter](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/rozdzialy/praktyka/optymalizacja.tex) · [Full chart](../figures/original/all-configurations.png)

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

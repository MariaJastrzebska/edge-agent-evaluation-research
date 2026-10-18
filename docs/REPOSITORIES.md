# Repository and source map

## My research repositories

**Access:** Edge-LLM-Lab and this report are public. The original manuscript and
fed-mobile remain private. Their revision-pinned links are retained for provenance
and require repository access; they are not public code downloads.

| Repository | Role in this report | Source snapshot |
| --- | --- | --- |
| [Original research manuscript](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska) | Original manuscript, architecture diagrams, historical evaluation and optimization plots | `de6eed63d368381e6251ccc6a8c7dd4c756a8976` |
| [Edge-LLM-Lab](https://github.com/MariaJastrzebska/edge-llm-lab) | Python evaluation tooling, later research and replay/scoring evidence | `d871920a363acb46a9fb2574f9d5e3fae1d71960` |
| [fed-mobile](https://github.com/MariaJastrzebska/fed-mobile) | Flutter application and local agent architecture | `1d415748c3c9170cc7693cd0e6e403c90f4c8113` |
| [edge-agent-evaluation-research](https://github.com/MariaJastrzebska/edge-agent-evaluation-research) | This retrospective report, annotated gallery, data transcriptions and provenance | Current report; publication history is available in Git |

The repositories have different purposes. Later laboratory work is not retroactively included in the study. A repository's name also does not establish completion of every topic it mentions: in particular, federated adaptation is not presented here as a completed experimental contribution.

## Primary manuscript chapters

All links below pin the manuscript revision used for this report.

- [Introduction and research objectives](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/wstep.tex)
- [Application architecture and implementation](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/rozdzialy/praktyka/opis.tex)
- [Evaluation methodology and model comparisons](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/rozdzialy/praktyka/eval.tex)
- [Quantization and runtime optimization, including the 46-configuration mapping](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/rozdzialy/praktyka/optymalizacja.tex)
- [Original conclusion](https://github.com/MariaJastrzebska/praca-magisterska---M.-Jastrzebska/blob/de6eed63d368381e6251ccc6a8c7dd4c756a8976/tekst/podsumowanie.tex)
- [Later reports](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/docs/research/current-reports.md)
- [Later evaluation boundaries](https://github.com/MariaJastrzebska/edge-llm-lab/blob/d871920a363acb46a9fb2574f9d5e3fae1d71960/docs/methodology/evaluation-boundaries.md)

## Upstream tools and related repositories

These are the tools and background resources I used or discussed. I list their roles below; using them does not mean I contributed to the upstream projects.

| Repository | Relationship to the work |
| --- | --- |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | Local inference engine; historically cited under ggerganov/llama.cpp |
| [GGML](https://github.com/ggml-org/ggml) | Underlying inference ecosystem and GGUF-related context |
| [fllama](https://github.com/Telosnex/fllama) | Flutter integration used for local execution |
| [Flutter](https://github.com/flutter/flutter) | Application framework |
| [Pydantic](https://github.com/pydantic/pydantic) | Schema definitions in the Python tooling |
| [Instructor](https://github.com/567-labs/instructor) | Structured model-judge responses in the evaluation tooling |
| [Ollama](https://github.com/ollama/ollama) | Preliminary model experimentation |
| [Transformers](https://github.com/huggingface/transformers) | Preliminary model experimentation and model tooling |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | Later scoring integration; not part of the original study evidence |
| [PyTorch](https://github.com/pytorch/pytorch) | Broader model tooling discussed in the manuscript |
| [TensorFlow](https://github.com/tensorflow/tensorflow) | Alternative deployment/conversion ecosystem discussed |
| [ONNX](https://github.com/onnx/onnx) | Conversion route explored in the manuscript |
| [Core ML tools](https://github.com/apple/coremltools) | Alternative Apple deployment/conversion route discussed |
| [vLLM](https://github.com/vllm-project/vllm) | Background server-inference comparison, not the selected mobile runtime |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Background agent orchestration, not the selected application runtime |
| [PySyft](https://github.com/OpenMined/PySyft) | Background privacy/federated-learning discussion, not a completed experiment |
| [EE-dyplom](https://github.com/SP5LMA/EE-dyplom) | LaTeX document template; template examples are not research evidence |

For each reproduced research image, the [manifest](../data/figure-manifest.json) supplies its exact source repository, path, revision and hash. External repositories retain their respective licenses; no new blanket license is assigned to their materials by this report.

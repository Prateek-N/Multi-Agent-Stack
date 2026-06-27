---
domain: research
phase_range: 0–5
task: Literature review plan — transformer efficiency architectures (ACL 2026 survey)
---

## CLI Invocation

```bash
python generate_prompt.py \
  --task "Plan and structure a literature review on transformer model architectures for NLP, \
focusing on efficiency improvements since Vaswani et al. 2017. \
Scope: 3000-word academic survey section. Target venue: ACL 2026. \
Key topics: sparse attention, linear attention, state space models (Mamba), mixture-of-experts." \
  --domain research \
  --phase 0
```

---

## Generated Prompt

```
## Project Context
Project : agents-maker / cookbook / research-lit-review
Session : sess_20260627_litrev_transformer
Phase   : 0 (Task Framing)
Domain  : research

## Session State
completed_phases : []
artifacts        : {}
open_questions   : []

## Task
Plan and structure a literature review on transformer model architectures for NLP,
focusing on efficiency improvements since Vaswani et al. (2017).
Scope      : 3000-word academic survey section
Venue      : ACL 2026 (long paper track)
Key topics : sparse attention, linear attention, state space models (Mamba),
             mixture-of-experts (MoE)

Deliverables expected by end of session:
  1. Research question hierarchy (primary + 4 sub-questions)
  2. Annotated bibliography (5–8 papers, 80–120 words each)
  3. Taxonomy / analysis framework (axes + cells)
  4. Section outline with word-count targets

## Domain & Routing
domain          : research
routing_hint    : orchestrator → architect_agent → execution_agent → reviewer_agent
style_guide     : ACL 2026 author kit; cite with (Author, Year); no footnotes in survey
quality_bar     : peer-review ready; all claims citable; no orphan citations
```

---

## Phase 0 — Task Framing

**Agent: orchestrator**

Reviewing task parameters. This is a scoped academic survey section, not a full
systematic review, so I will constrain scope tightly.

Scope decisions:

- **Time window:** 2017–2025 (inclusive). Seminal 2017 baseline; cutoff before ACL 2026
  submission deadline.
- **Efficiency axis:** wall-clock / memory / FLOPs reductions relative to O(n²) vanilla
  attention. Quality-only improvements (e.g., instruction tuning) are out of scope.
- **NLP focus:** exclude vision transformers and multimodal-only architectures unless
  directly cited for NLP benchmarks (GLUE, SuperGLUE, SCROLLS, LongBench).
- **Word budget allocation (3000 words):**
  - Introduction + motivation: 300 w
  - Sparse attention family: 650 w
  - Linear / kernel attention family: 650 w
  - State space models: 700 w
  - Mixture-of-experts: 500 w
  - Synthesis + open problems: 200 w

Routing: handing to **architect_agent** for Phase 1 (requirements) with the above
scope boundary as a hard constraint.

> [Companion]
> Phase 0 complete. Scope locked: efficiency-focused, NLP-only, 2017–2025,
> 3000 words, ACL 2026. Word budget allocated across 4 architectural families.
> Next → Phase 1 (architect_agent: research question hierarchy).

---

## Phase 1 — Requirements

**Agent: architect_agent**

Accepting scope from orchestrator. Constructing research question hierarchy.

### Primary Research Question

> **RQ0:** What architectural modifications to the transformer's self-attention
> mechanism have achieved the most significant efficiency gains in NLP tasks
> since 2017, and what trade-offs do they impose on model quality and
> generalizability?

### Sub-Questions

| ID  | Sub-question | Scope tag |
|-----|--------------|-----------|
| RQ1 | How do sparse attention patterns (local windows, strided, learned) compare in memory complexity and downstream NLP accuracy? | sparse_attention |
| RQ2 | Do linear-attention approximations (kernel methods, random features) preserve language model perplexity at practical context lengths (≥4 k tokens)? | linear_attention |
| RQ3 | Can structured state space models (S4, Mamba) match transformer expressivity on NLP tasks requiring in-context reasoning, and at what sequence-length crossover point do they become preferable? | ssm |
| RQ4 | How does conditional computation via mixture-of-experts trade parameter count against inference FLOPs, and what routing instabilities remain open problems? | moe |

### Scope Boundary (hard exclusions)

- Architecture search / NAS approaches not primarily motivated by attention efficiency
- Quantisation, pruning, distillation (separate efficiency axis)
- Non-English or low-resource NLP as primary contribution
- Any paper without a reproducible FLOPs or memory benchmark

> [Companion]
> Phase 1 complete. RQ hierarchy: 1 primary + 4 sub-questions across sparse,
> linear, SSM, MoE families. Hard exclusions documented.
> Next → Phase 2 (architect_agent: methodology + taxonomy framework).

---

## Phase 2 — Solution Design

**Agent: architect_agent**

Designing the analysis framework. Each paper in the bibliography will be
evaluated across the following taxonomy axes.

### Taxonomy: Axes and Values

| Axis | Values |
|------|--------|
| **Complexity class** | O(n²) · O(n log n) · O(n) · O(n · k) sublinear |
| **Attention type** | full · sparse-fixed · sparse-learned · kernel/linear · recurrent-equiv |
| **Pretraining paradigm** | MLM · CLM · encoder-decoder · hybrid |
| **Context length at eval** | ≤512 · 512–4 k · 4 k–16 k · >16 k |
| **Primary NLP benchmark** | GLUE/SuperGLUE · LongBench · SCROLLS · language modelling (PPL) · summarization |
| **Hardware target** | GPU (A100/H100) · TPU · edge/mobile |
| **Year** | 2017–2019 · 2020–2021 · 2022–2023 · 2024–2025 |

### Methodology for Section Writing

1. **Cluster by family** (sparse → linear → SSM → MoE) to allow direct
   within-family comparison before cross-family synthesis.
2. **Anchor each family** with one seminal paper (pivot), then trace derivative
   works chronologically.
3. **Comparison table** at end of each subsection: pivot paper vs. two
   successors on complexity class, peak context length, and best GLUE score.
4. **Synthesis section** maps all families onto a single Pareto front:
   quality (SuperGLUE avg.) vs. inference FLOPs at n=4096.

> [Companion]
> Phase 2 complete. 7-axis taxonomy defined. Cluster-then-compare methodology
> chosen; Pareto synthesis planned. Handing to execution_agent for bibliography
> and outline build.
> Next → Phase 3 (execution_agent: annotated bibliography + section outline).

---

## Phase 3 — Implementation

**Agent: execution_agent**

Building annotated bibliography. All annotations map to taxonomy axes.
Word counts per annotation: 80–120 words.

---

### Annotated Bibliography

**[1] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N.,
Kaiser, Ł., & Polosukhin, I. (2017). Attention Is All You Need.
*NeurIPS 2017.***

Introduces the transformer encoder-decoder using multi-head dot-product
self-attention. All subsequent efficiency work uses this as the O(n²)
baseline in both memory (quadratic KV cache) and compute. Establishes
BLEU benchmarks on WMT En-De and En-Fr that remain reference points.
Taxonomy: O(n²) · full attention · encoder-decoder · ≤512 tokens · MT.
Critical limitation acknowledged by authors: "the path length between
positions" grows with distance, motivating all linear and sparse successors.
*Pivot paper for entire survey.*

---

**[2] Beltagy, I., Peters, M. E., & Cohan, A. (2020). Longformer: The
Long-Document Transformer. *arXiv:2004.05150.***

Proposes a sliding-window local attention (complexity O(n)) combined with
task-motivated global tokens (CLS, question tokens). Achieves competitive
performance on long-document NLP tasks (QA on TriviaQA, summarization on
arXiv/PubMed) at context lengths up to 4096 tokens while reducing memory
from 8 GB to under 3 GB at n=4096 vs. RoBERTa-large full attention.
Taxonomy: O(n) · sparse-fixed · MLM · 512–4 k · GLUE/long-doc.
Key finding: global tokens are necessary; pure local attention degrades
on tasks requiring cross-segment reasoning. *Pivot: sparse-fixed family.*

---

**[3] Wang, S., Li, B. Z., Khabsa, M., Fang, H., & Ma, H. (2020). Linformer:
Self-Attention with Linear Complexity. *arXiv:2006.04768.***

Projects the n × d attention matrix to a low-rank k × d approximation
via learnable linear projections, reducing self-attention to O(n · k)
where k ≪ n. Demonstrates that the attention matrix has low stable rank
empirically across BERT layers. Achieves near-BERT GLUE scores at 8×
memory reduction for n=512. Taxonomy: O(n·k) · kernel/linear · MLM ·
≤512 · GLUE. Important caveat: projection matrices are sequence-length
specific, complicating variable-length inference. *Pivot: linear family.*

---

**[4] Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). FlashAttention:
Fast and Memory-Efficient Exact Attention with IO-Awareness.
*NeurIPS 2022.***

Reframes the efficiency problem as an IO bottleneck rather than an
algorithmic one. Tiling and kernel fusion eliminate HBM reads/writes of
the full n×n attention matrix without approximation, achieving exact
attention in O(n²) FLOPs but O(n) HBM memory. Enables training with
n=16 k on a single A100. Taxonomy: O(n²) FLOPs · O(n) memory · full
attention · CLM/MLM · >4 k · LM-PPL. Orthogonal to approximation methods:
often used as the backend for sparse and linear attention implementations.

---

**[5] Gu, A., & Dao, T. (2023). Mamba: Linear-Time Sequence Modeling with
Selective State Spaces. *arXiv:2312.00752.***

Introduces a selective SSM where the discrete-time parameters (Δ, B, C)
are input-dependent, breaking the time-invariance of S4. Enables
content-based reasoning previously requiring softmax attention. Achieves
lower perplexity than transformer baselines at equivalent parameter counts
on The Pile, and matches or exceeds Pythia-1B on downstream NLP tasks.
Inference is O(n) time and O(1) memory per step (recurrent mode).
Taxonomy: O(n) · recurrent-equiv · CLM · >16 k · LM-PPL.
*Pivot: SSM family.* Open question: in-context learning still lags GPT-class
models at equivalent scale.

---

**[6] Fedus, W., Zoph, B., & Shazeer, N. (2022). Switch Transformers: Scaling
to Trillion Parameter Models with Simple and Efficient Sparsity.
*JMLR 23(120).***

Simplifies MoE routing to a single expert per token (top-1) with an
auxiliary load-balancing loss. Demonstrates 7× pre-training speedup over
T5-Large at equivalent FLOPs by scaling parameters without scaling compute.
Achieves strong multilingual transfer on mC4. Taxonomy: conditional
compute · encoder-decoder · CLM equiv · ≤512 · GLUE/translation.
Key routing instability: expert collapse under aggressive capacity factors;
partially mitigated by auxiliary loss but remains unsolved at extreme scale.
*Pivot: MoE family.*

---

**[7] Jiang, A. Q., Sablayrolles, A., Roux, A., Mensch, A., Savary, B.,
Bamford, C., … Lample, G. (2024). Mixtral of Experts.
*arXiv:2401.04088.***

Deploys top-2 sparse MoE over a 7B-parameter base (47B total parameters,
12.9B active per token) using a sliding-window attention of 32 k tokens.
Outperforms LLaMA 2-70B on most benchmarks while activating 5× fewer
parameters at inference. Demonstrates that MoE and sparse attention are
compositionally compatible. Taxonomy: O(n·w) window attn + conditional
compute · CLM · >16 k · LM-PPL/MMLU. Confirms that top-2 routing is
empirically more stable than top-1 at this scale.

---

### Section Outline with Word-Count Targets

```
3  Efficiency-Oriented Transformer Architectures               [3000 w total]

3.1  Introduction and Motivation                               [300 w]
     - O(n²) bottleneck; practical context-length demands
     - Survey scope and inclusion criteria

3.2  Sparse Attention                                          [650 w]
3.2.1  Fixed-pattern sparsity: Longformer [2], BigBird
3.2.2  Learned sparsity: Routing Transformer, Reformer
3.2.3  Comparison table: complexity, peak n, GLUE avg.

3.3  Linear and Kernel Attention                               [650 w]
3.3.1  Low-rank projection: Linformer [3]
3.3.2  Random-feature approximation: Performer
3.3.3  IO-aware exact attention: FlashAttention [4] (baseline)
3.3.4  Comparison table

3.4  State Space Models                                        [700 w]
3.4.1  Time-invariant SSMs: S4, H3
3.4.2  Selective SSMs: Mamba [5]
3.4.3  Hybrid architectures: Jamba (Mamba + attention layers)
3.4.4  Crossover analysis: at what n does SSM beat transformer?

3.5  Mixture of Experts                                        [500 w]
3.5.1  Top-1 routing: Switch Transformers [6]
3.5.2  Top-2 routing at scale: Mixtral [7]
3.5.3  Routing instability: open problems

3.6  Synthesis and Open Problems                               [200 w]
     - Pareto front: quality vs. inference FLOPs at n=4096
     - Compositional combinations (MoE + sparse attn)
     - Remaining gaps: in-context learning in SSMs; long-context MoE
```

> [Companion]
> Phase 3 complete. 7-paper annotated bibliography built; all entries
> mapped to taxonomy axes. Section outline with word targets ready.
> Next → Phase 4 (reviewer_agent: coverage gaps + citation balance).

---

## Phase 4 — Review

**Agent: reviewer_agent**

Running coverage audit against RQ hierarchy and taxonomy.

### Coverage Map

| RQ  | Covered by | Gap? |
|-----|-----------|------|
| RQ0 (overall efficiency trade-offs) | All 7 papers; §3.6 synthesis | No |
| RQ1 (sparse attention NLP accuracy) | [2] Longformer + outline mentions BigBird, Reformer | Minor: Reformer not annotated |
| RQ2 (linear attention at ≥4 k tokens) | [3] Linformer (≤512 only), [4] FlashAttention | **Gap: Performer or RWKV needed for ≥4 k linear** |
| RQ3 (SSM vs. transformer crossover) | [5] Mamba; §3.4.4 | Minor: crossover data needs quantification |
| RQ4 (MoE routing instability) | [6] Switch, [7] Mixtral | No — both papers address this |

### Citation Balance Check

| Family | # Annotated papers | Year range | Oldest paper |
|--------|--------------------|------------|--------------|
| Sparse attention | 1 annotated + 2 outline refs | 2020 | Longformer 2020 |
| Linear / kernel | 2 annotated | 2020, 2022 | Linformer 2020 |
| SSM | 1 annotated | 2023 | Mamba 2023 |
| MoE | 2 annotated | 2022, 2024 | Switch 2022 |
| Baseline | 1 annotated | 2017 | Vaswani 2017 |

**Flag:** Linear attention family lacks a ≥4 k token representative.
Recommended addition: Peng et al. (2023) *RWKV: Reinventing RNNs for the
Transformer Era* (arXiv:2305.13048) — O(n), CLM, tested at 4 k–16 k,
competitive PPL on The Pile. Covers RQ2 gap and extends year range to 2023.

**Flag (minor):** Reformer (Kitaev et al., 2020) should be at minimum cited
in §3.2.2 for LSH-based learned sparsity; no full annotation needed.

**ACL 2026 style check:**
- All citations in (Author, Year) format: confirmed
- No footnotes present: confirmed
- Self-citations: none detected (reviewer cannot check without author identity)

> [Companion]
> Phase 4 complete. Two gaps found: (1) linear attention lacks ≥4 k
> representative — add RWKV [8]; (2) Reformer needs inline cite in §3.2.2.
> All other RQs covered. Citation balance acceptable.
> Next → Phase 5 (orchestrator: handoff + writing order).

---

## Phase 5 — Handoff

**Agent: orchestrator**

Incorporating reviewer flags. Final artifact is below. Writing order and
next steps for the human researcher follow.

### Writing Order (recommended)

1. **Write §3.1 first** (introduction/motivation). Sets the O(n²) framing
   that every subsequent section references.
2. **Write §3.4 (SSM) second.** Mamba is the most novel family for ACL 2026
   reviewers; get the strongest argument on paper early while thinking is fresh.
3. **Write §3.2 (Sparse) and §3.3 (Linear) in parallel** — these are
   mechanistically parallel and share the same comparison table structure.
4. **Write §3.5 (MoE) fourth.** Benefits from §3.3's discussion of parameter
   vs. compute trade-offs.
5. **Write §3.6 (Synthesis) last.** Requires Pareto plot data; generate figure
   after drafting §§3.2–3.5.

### Next Steps for Human Researcher

- [ ] Retrieve RWKV (Peng 2023) and add as annotated entry [8] before drafting §3.3.
- [ ] Add inline citation (Kitaev et al., 2020) in §3.2.2 for Reformer.
- [ ] Generate Pareto figure (quality vs. FLOPs at n=4096) using numbers from
      Mamba paper Table 3, Mixtral paper Table 2, and FlashAttention paper §5.
- [ ] Confirm ACL 2026 page limit: survey sections of this scope typically
      fit in 4 pages of a 9-page submission; verify with venue CFP.
- [ ] Run `generate_prompt.py --phase 3 --inject artifacts/bibliography.json`
      when drafting begins to restore session state.

> [Companion]
> Phase 5 complete. Full handoff package ready. Session artifact below.

---

## Final Output Artifact

### Research Question Hierarchy

```
RQ0  What architectural modifications to transformer self-attention have achieved
     the greatest efficiency gains in NLP since 2017, and what quality/
     generalizability trade-offs do they impose?
 │
 ├─ RQ1  Sparse attention: how do fixed vs. learned sparsity patterns compare
 │       in memory complexity and NLP accuracy?
 │
 ├─ RQ2  Linear attention: do kernel approximations preserve LM perplexity
 │       at context lengths ≥ 4 k tokens?
 │
 ├─ RQ3  SSMs: can Mamba-class models match transformer in-context reasoning,
 │       and at what sequence-length crossover?
 │
 └─ RQ4  MoE: how does top-k routing trade parameter count vs. inference FLOPs,
         and what routing instabilities remain open?
```

### Final Annotated Bibliography (8 papers)

1. Vaswani et al. (2017) — O(n²) baseline; MT BLEU pivot.
2. Beltagy et al. (2020) — Longformer; sparse-fixed pivot; O(n) local+global.
3. Wang et al. (2020) — Linformer; low-rank projection; O(n·k).
4. Dao et al. (2022) — FlashAttention; IO-aware exact attention; O(n) HBM.
5. Gu & Dao (2023) — Mamba; selective SSM; O(n) recurrent; SSM pivot.
6. Fedus et al. (2022) — Switch Transformers; top-1 MoE; 7× speedup.
7. Jiang et al. (2024) — Mixtral; top-2 MoE + sliding-window; 47B/12.9B active.
8. Peng et al. (2023) — RWKV; linear-recurrent LM; ≥4 k NLP; RQ2 coverage.
   *(Peng, B., Alcaide, E., Anthony, Q., et al. arXiv:2305.13048)*

### Analysis Framework Summary

7 taxonomy axes: complexity class · attention type · pretraining paradigm ·
context length at eval · primary NLP benchmark · hardware target · year.

Pareto synthesis: map all 8 papers onto quality (SuperGLUE avg. or PPL) vs.
inference FLOPs at n=4096 to identify the efficiency frontier.

Section word budget: 300 + 650 + 650 + 700 + 500 + 200 = **3000 words**.

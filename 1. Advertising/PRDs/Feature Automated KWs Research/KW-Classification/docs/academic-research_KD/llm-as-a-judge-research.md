# LLM-as-a-Judge: Research Summary for Kepler

> **Purpose**: Distilled insights from academic research to inform Kepler's keyword classification evaluation approach.
>
> **Papers Analyzed**: 29 papers from arXiv (2023-2025)
> **Depth**: Full paper content extracted (HTML versions, not just abstracts)
> **Last Updated**: January 2026

---

## Table of Contents
1. [Approaches & Methodologies](#llm-as-a-judge-approaches--methodologies)
2. [Survey Papers (4)](#survey-papers)
3. [Foundational Papers (3)](#foundational-papers)
4. [Fine-Tuned Judge Models (5)](#fine-tuned-judge-models)
5. [Benchmarks & Evaluation (5)](#benchmarks--evaluation) *(NEW)*
6. [Bias Mitigation Methods (4)](#bias-mitigation-methods) *(NEW)*
7. [Multi-Judge & Aggregation (2)](#multi-judge--aggregation) *(NEW)*
8. [Reference-Free Evaluation (3)](#reference-free-evaluation) *(NEW)*
9. [Self-Improvement & Meta-Judging (2)](#self-improvement--meta-judging)
10. [Critique Generation (1)](#critique-generation)
11. [Complete Paper List](#complete-paper-list) *(NEW)*
12. [Summary Comparison](#summary-comparison)
13. [Relevance to Kepler](#relevance-to-kepler)
14. [Recommended Approach](#recommended-approach)

---

# LLM-as-a-Judge: Approaches & Methodologies

This section explains the core techniques and approaches used in LLM-as-a-Judge systems, extracted from the full papers.

## Scoring Methods

### 1. Discrete Scoring
Assign ratings on fixed scales (1-3, 1-5, 1-10).

```
"Each assistant receives an overall score on a scale of 1 to 10,
where a higher score indicates better overall performance."
```

### 2. Likert Scale with Dimensions
Hierarchical dimensional evaluation:
- Assign separate scores (1-3) for each dimension (accuracy, coherence, factuality)
- Derive overall score (1-5) from component ratings

### 3. Continuous Scoring
Fine-grained 0-1 or 0-100 scales for greater differentiation.

---

## Pairwise Comparison Modes

| Mode | Options | Use Case |
|------|---------|----------|
| **Two-Option** | A or B | Simple preference |
| **Three-Option** | A, B, or Tie | Allow equal quality |
| **Four-Option** | A, B, Both Good Tie, Both Bad Tie | Nuanced comparison |

> "Pairwise comparison is often used for ranking multiple options, where several comparisons are made between pairs to identify the better choice or establish a hierarchy."

---

## Prompt-Based Approaches

### In-Context Learning (ICL)
Leverage few-shot examples without training:

| Method | Technique |
|--------|-----------|
| **GPTScore** | Relevant examples for flexible assessment |
| **LLM-EVAL** | Crafted examples for multi-dimensional dialogue |
| **TALEC** | Custom criteria via iterative example refinement |
| **ALLURE** | Mitigates ICL bias through discrepancy iteration |

**Example Prompt**:
```
Here are examples of high-quality evaluations:
[Example 1: Input → Score 5 because...]
[Example 2: Input → Score 2 because...]

Now evaluate this response:
[New input]
```

### Chain-of-Thought (CoT) Evaluation
Decompose complex evaluation into explicit steps:

| Method | Approach |
|--------|----------|
| **G-EVAL** | CoT + form-filling paradigm |
| **ICE-Score** | Step-by-step code evaluation |
| **FineSurE** | Breaks into faithfulness, completeness, conciseness |
| **SocREval** | Socratic method systematic reasoning |

**Example CoT Steps**:
```
Step 1: "Read the article and identify main topic and key points"
Step 2: "Compare summary to article, checking coverage"
Step 3: "Assess logical order and coherence"
Step 4: "Assign score based on criteria"
```

### Definition Augmentation
Auto-refine evaluation criteria:

| Method | Innovation |
|--------|------------|
| **AUTOCALIBRATE** | Multi-stage gradient-free calibration |
| **SALC** | LLM generates context-aware criteria autonomously |
| **BiasAlert** | Integrates external knowledge for bias detection |

### Multi-Turn Optimization
Iterative interactions refining results:

| Method | Approach |
|--------|----------|
| **ACTIVE-CRITIC** | Infer criteria from data, dynamically optimize prompts |
| **Auto-Arena** | Multi-round debates between candidates |
| **KIEval** | LLM "interactor" for dynamic assessment |

---

## Tuning-Based Approaches

### Score-Based Tuning
Fine-tune on datasets with numerical scores:

| Method | Training Data |
|--------|---------------|
| **TIGERScore** | 42K synthetic error analysis samples |
| **ARES** | Prediction-powered inference for confidence |
| **PHUDGE** | Human-labeled evaluation datasets |

### Preference-Based Learning (DPO)
Train on pairwise preference data (A > B):

| Method | Key Innovation |
|--------|----------------|
| **JudgeLM** | Swap augmentation + reference support |
| **PROMETHEUS** | 100K responses with custom rubrics |
| **Con-J** | DPO on contrastive + SFT on positive |
| **AUTO-J** | Scoring + preference data combined |

---

## Post-Processing Techniques

### 1. Token Extraction
Pattern matching for format variability:
```
"Response 1 is better" → Extract "1"
"The better one is response 1" → Extract "1"
"Summary A is more coherent" → Extract "A"
```

### 2. Constrained Decoding
Enforce structured output via finite state machines:
- **DOMINO**: Preserves tokenization while enforcing constraints
- **XGrammar**: Accelerates grammar-constrained generation
- **SGLang**: Domain-specific language + optimized runtime

### 3. Logit Normalization (Probability Weighting)
Convert token probabilities to calibrated scores:

```
ρSC = ∏(ti∈α) P(ti|t<i) · ∏(ti∈β) P(ti|t<i)
ρSR = ∏(ti∈"Yes") P(ti|t<i)
Final Score = ρSC · ρSR
```

**G-EVAL Formula**:
```
score = Σ(i=1 to n) p(sᵢ) × sᵢ
```
Where p(sᵢ) = probability of each score token

### 4. Multi-Round Aggregation
Run evaluation multiple times and aggregate:
```python
scores = [evaluate(x) for _ in range(3)]
final = statistics.median(scores)  # or mean
```

---

## Multi-LLM Architectures

### Cooperation Models
Multiple LLMs work together:

| Method | Architecture |
|--------|--------------|
| **WideDeep** | Neural-level aggregation |
| **Peer Review** | Agents create, review, revise |
| **ABSEval** | 4 agents: synthesize, critique, execute, reason |

### Competition/Debate Models
LLMs argue to find truth:

| Method | Structure |
|--------|-----------|
| **Auto-Arena** | Multi-round debates + committee judge |
| **ChatEval** | Diverse role prompts + communication |
| **PRD** | Peer rank and discussion |

### Aggregation Methods

| Method | Technique |
|--------|-----------|
| **Majority Voting** | Most frequent answer wins |
| **PoLL** | Panel of diverse smaller models |
| **Weighted (PRE)** | Weight by human agreement |
| **PiCO** | Constrained optimization |
| **Bayesian (BWRS)** | Address win rate estimation bias |
| **Cascaded** | Weak models first, escalate if uncertain |

---

## Prompt Templates from Papers

### Scoring Template
```
Evaluate the quality of summaries written for a news article.
Rate each summary on four dimensions:
{Dimension_1}, {Dimension_2}, {Dimension_3}, {Dimension_4}.
Rate on a scale from 1 (worst) to 5 (best).
```

### Yes/No Evaluation
```
Is the sentence supported by the article?
Answer "Yes" or "No".
Article: {Article}
Sentence: {Sentence}
```

### Pairwise Comparison
```
Given a news article, which summary is better?
Answer "Summary 0" or "Summary 1".
You do not need to explain the reason.
Article: {Article}
Summary 0: {Summary_0}
Summary 1: {Summary_1}
```

### PROMETHEUS Rubric Template
```
###Task Description:
1. Write detailed feedback based strictly on the score rubric
2. Write score (1-5)

###The instruction to evaluate: {instruction}
###Response to evaluate: {response}
###Reference Answer (Score 5): {reference}
###Score Rubrics:
[criteria]: {criteria_description}
Score 1: {description_for_1}
Score 2: {description_for_2}
Score 3: {description_for_3}
Score 4: {description_for_4}
Score 5: {description_for_5}
```

### TIGERScore Error Format
```json
{
  "errors": [
    {
      "location": "second paragraph",
      "aspect": "factual_accuracy",
      "explanation": "Claims X but source says Y",
      "severity": "major",
      "penalty": -2.0,
      "suggestion": "Correct to match source"
    }
  ],
  "total_score": -2.0
}
```

---

## Criteria Decomposition Methods

### Hierarchical Decomposition (HD-EVAL)
Break coarse criteria into fine sub-dimensions:

```
Fluency (coarse)
├── Grammar (fine)
├── Engagingness (fine)
└── Readability (fine)
```

### Multi-Dimensional Rubrics (PROMETHEUS)
Define clear levels for each dimension:

| Dimension | Score 1 | Score 3 | Score 5 |
|-----------|---------|---------|---------|
| Accuracy | Completely wrong | Partially correct | Fully accurate |
| Completeness | Missing most | Covers main points | Comprehensive |
| Clarity | Confusing | Understandable | Crystal clear |

---

## Key Implementation Insights

### Position Bias Mitigation
```python
# From JudgeLM: Swap Augmentation
def evaluate_debiased(a, b, judge):
    score_ab = judge(a, b)  # A first
    score_ba = judge(b, a)  # B first (swapped)

    # Only accept if consistent
    if score_ab == inverse(score_ba):
        return score_ab
    else:
        return "uncertain"  # Flag for review
```

### Confidence-Based Filtering
```python
# From surveys: Self-validation
def evaluate_with_confidence(x, judge):
    result = judge(x)
    confidence = judge(f"How confident are you? {result}")

    if confidence < 0.7:
        return flag_for_human_review(x)
    return result
```

### Ensemble Judging
```python
# From PoLL: Panel of diverse models
def ensemble_evaluate(x):
    judges = [gpt4, claude, llama, mistral]
    scores = [j(x) for j in judges]

    # Majority voting
    return statistics.mode(scores)

    # Or weighted by known accuracy
    # return weighted_average(scores, weights)
```

---

# Survey Papers

## Paper 1: A Survey on LLM-as-a-Judge

| | |
|---|---|
| **arXiv** | [2411.15594](https://arxiv.org/abs/2411.15594) |
| **Full Text** | [HTML](https://arxiv.org/html/2411.15594) |
| **Authors** | Jiawei Gu et al. (18 authors) |
| **Date** | Nov 2024 |
| **Focus** | Reliability & bias mitigation |
| **Project** | [llm-as-a-judge.github.io](https://llm-as-a-judge.github.io/) |

### Key Contributions

**Four Primary Evaluation Methods**:
| Method | Description | Use Case |
|--------|-------------|----------|
| Score Generation | Discrete (1-5) or continuous (0-1) | Quality ratings |
| Yes/No Judgments | Binary pass/fail | Accuracy checks |
| Pairwise Comparison | A vs B ranking | Model comparison |
| Multi-Choice Selection | Pick best option | Answer selection |

**12+ Bias Types Documented**:
- Position Bias, Length Bias, Self-Enhancement, Verbosity Bias
- Authority Bias, Sentiment Bias, Familiarity Bias, Concreteness Bias

**Reliability Strategies**:
- Few-shot prompting with high-quality examples
- Chain-of-Thought step decomposition
- Criteria decomposition (hierarchical)
- Content shuffling (position randomization)
- Constrained output (JSON/XML)
- Multi-round evaluation
- Self-validation (confidence queries)

**Performance Benchmarks**:
| Model | Human Alignment | Position Consistency |
|-------|-----------------|---------------------|
| GPT-4 | 61.54% | 91.18% |
| GPT-3.5 | 54.72% | - |
| Qwen2.5-7B | 56.54% | - |

### Kepler Takeaways
- Implement position shuffling for bias mitigation
- Add self-validation step (confidence scores)
- Use multi-round evaluation (3x, median)

---

## Paper 2: LLMs-as-Judges: A Comprehensive Survey

| | |
|---|---|
| **arXiv** | [2412.05579](https://arxiv.org/abs/2412.05579) |
| **Authors** | Haitao Li et al. |
| **Date** | Dec 2024 |
| **Focus** | 5-perspective framework |
| **GitHub** | [Awesome-LLMs-as-Judges](https://github.com/CSHaitao/Awesome-LLMs-as-Judges) |

### Five Key Perspectives

| Perspective | Question | Coverage |
|-------------|----------|----------|
| Functionality | Why use LLM judges? | Performance eval, model enhancement |
| Methodology | How to build? | Single-LLM, Multi-LLM, Human-AI |
| Applications | Where to deploy? | Medical, Legal, Financial, Education |
| Meta-evaluation | How to evaluate judges? | Benchmarks, metrics |
| Limitations | What constraints? | Biases, vulnerabilities |

### System Architectures

**Single-LLM Prompt-Based**:
| Method | Examples |
|--------|----------|
| In-Context Learning | GPTScore, LLM-EVAL, ALLURE |
| Chain-of-Thought | G-EVAL, ICE-Score, FineSurE |
| Definition Augmentation | AUTOCALIBRATE, SALC |

**Single-LLM Tuning-Based**:
| Method | Examples |
|--------|----------|
| Score-Based Tuning | PHUDGE, AttrScore, ARES |
| Preference Learning (DPO) | JudgeLM, PandaLM, PROMETHEUS |

**Multi-LLM Aggregation**:
| Method | Description |
|--------|-------------|
| Voting | Majority vote, max voting (PoLL) |
| Weighted | Agreement-based weights (PRE, AIME) |
| Bayesian | BWRS, Dawid-Skene bias correction |
| Cascaded | Escalate to stronger model |

### Kepler Takeaways
- Consider multi-judge ensemble (GPT-4o + Claude)
- Use cascaded evaluation for cost optimization
- Implement weighted aggregation

---

## Paper 3: From Generation to Judgment

| | |
|---|---|
| **arXiv** | [2411.16594](https://arxiv.org/abs/2411.16594) |
| **Authors** | Multiple |
| **Date** | Nov 2024 |
| **Venue** | EMNLP 2025 |
| **Focus** | What/How/Benchmark taxonomy |

### Three-Dimensional Taxonomy

**Dimension 1: What to Judge**
| Category | Examples |
|----------|----------|
| Text Quality | Fluency, coherence, relevance |
| Factuality | Accuracy, grounding, hallucination |
| Safety | Harmlessness, bias, toxicity |
| Instruction Following | Task completion, format adherence |
| Reasoning | Logic, math, code correctness |

**Dimension 2: How to Judge**
| Approach | Description |
|----------|-------------|
| Reference-Based | Compare against gold standard |
| Reference-Free | Judge without ground truth |
| Decomposed | Break into sub-criteria |
| Holistic | Single overall score |

**Dimension 3: How to Benchmark**
| Method | Description |
|--------|-------------|
| Human Agreement | Correlation with human judgments |
| Consistency | Same input → same output |
| Discrimination | Can distinguish quality levels |
| Calibration | Scores match actual distribution |

### Kepler Takeaways
- Map criteria to standard categories
- Test consistency across runs
- Build calibration dataset

---

## Paper 4: LLM-as-a-Judge & Reward Model Survey

| | |
|---|---|
| **arXiv** | [2409.11239](https://arxiv.org/abs/2409.11239) |
| **Authors** | Guijin Son, Hyunwoo Ko, Hoyoung Lee, Yewon Kim, Seunghyeok Hong |
| **Date** | Sep 2024 |
| **Focus** | Comparative analysis of automated evaluators |

### Key Contributions

**Comprehensive Analysis**: Examined automated evaluators across diverse contexts including non-English prompts, factual verification, and complex reasoning.

**Three Major Findings**:

| Finding | Description |
|---------|-------------|
| **Language Transfer** | English evaluation capabilities influence language-specific evaluation more than language proficiency itself |
| **Error Detection Gaps** | LLMs fail to identify factual inaccuracies, cultural misrepresentations, and unwanted language |
| **Reasoning Limitations** | State-of-the-art evaluators struggle with challenging prompts in both English and Korean |

### Kepler Takeaways
- Consider multilingual evaluation capabilities
- Don't rely solely on LLM judges for factual accuracy checks
- Test judges on complex reasoning tasks before deployment

---

# Foundational Papers

## Paper 5: MT-Bench & Chatbot Arena

| | |
|---|---|
| **arXiv** | [2306.05685](https://arxiv.org/abs/2306.05685) |
| **Authors** | Lianmin Zheng et al. (UC Berkeley, Stanford) |
| **Date** | Jun 2023 |
| **Venue** | NeurIPS 2023 |
| **GitHub** | [FastChat/llm_judge](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge) |

### Key Contributions

**The paper that coined "LLM-as-a-Judge"**

**MT-Bench Categories** (8 categories, 10 multi-turn questions each):
- Writing, Roleplay, Extraction, Reasoning
- Math, Coding, STEM knowledge, Humanities/Social Science

**Bias Analysis with Numbers**:

| Bias Type | GPT-4 | Claude-v1 | GPT-3.5 |
|-----------|-------|-----------|---------|
| Position consistency | 65% | 23.8% | 46.2% |
| Verbosity attack failure | 8.7% | 91.3% | 91.3% |
| Self-enhancement | ~10% | ~25% | None |

**Agreement Rates**:
- GPT-4 vs humans on MT-Bench: **85%** (excluding ties)
- Human-to-human agreement: ~81%
- GPT-4 on Chatbot Arena: **95%** (excluding ties)
- Humans changed votes after seeing GPT-4 judgment: **34%**

**Released Resources**: 80 MT-bench questions, 3K expert votes, 30K conversations

### Kepler Takeaways
- Position bias is severe in some models (Claude-v1: only 23.8% consistent)
- GPT-4 most robust to verbosity attacks (8.7% failure vs 91%+ others)
- Swap positions and average for reliable results

---

## Paper 6: G-EVAL

| | |
|---|---|
| **arXiv** | [2303.16634](https://arxiv.org/abs/2303.16634) |
| **Authors** | Yang Liu et al. (Microsoft) |
| **Date** | Mar 2023 |
| **Venue** | EMNLP 2023 |
| **GitHub** | [nlpyang/geval](https://github.com/nlpyang/geval) |

### Key Contributions

**Three-Part Prompt Structure**:
1. **Task Introduction**: Defines the evaluation task
2. **Evaluation Criteria**: Specifies dimensions (coherence, fluency, etc.)
3. **Auto Chain-of-Thoughts**: LLM generates intermediate evaluation steps

**Probability Weighting Formula**:
```
score = Σ(i=1 to n) p(sᵢ) × sᵢ
```
Where `p(sᵢ)` = probability of each score token → enables fine-grained differentiation

**Auto-Generated CoT Example** (for coherence):
1. "Read the news article carefully and identify main topic and key points"
2. "Compare summary to article, checking coverage and logical order"

**Spearman Correlation Results**:

| Benchmark | G-Eval-4 | G-Eval-3.5 |
|-----------|----------|------------|
| SummEval (summarization) | **0.514** | 0.401 |
| Topical-Chat (dialogue) | **0.588** | 0.585 |
| QAGS (hallucinations) | **0.611** | 0.461 |

### Kepler Takeaways
- Probability weighting significantly improves over raw token output
- Auto-CoT reduces manual prompt engineering
- Form-filling paradigm ensures structured output

---

## Paper 7: LLM-Eval

| | |
|---|---|
| **arXiv** | [2305.13711](https://arxiv.org/abs/2305.13711) |
| **Authors** | Yen-Ting Lin et al. |
| **Date** | May 2023 |
| **Venue** | NLP4ConvAI 2023 |
| **Focus** | Multi-dimensional conversation evaluation |

### Key Contributions

**Single Prompt Multi-Dimensional Evaluation**

**Advantages**:
- No human annotations needed
- No ground-truth required
- Single LLM call (efficient)
- Unified schema across dimensions

**Key Insight**: One well-designed prompt can cover multiple dimensions simultaneously

### Kepler Takeaways
- Unified prompts can be more efficient
- Design schema to cover all dimensions in one call

---

# Fine-Tuned Judge Models

## Paper 8: PROMETHEUS

| | |
|---|---|
| **arXiv** | [2310.08491](https://arxiv.org/abs/2310.08491) |
| **Authors** | Seungone Kim et al. |
| **Date** | Oct 2023 |
| **Venue** | ICLR 2024 |
| **GitHub** | [prometheus-eval](https://github.com/prometheus-eval/prometheus-eval) |

### Key Contributions

**13B open-source judge matching GPT-4**

**Training Methodology**:
- Base model: Llama-2-Chat-13B
- Sequential generation: feedback first, then scores (1-5)
- Reference answers included to decompose evaluation
- Setup: 8xA100 GPUs, PyTorch FSDP, lr=1e-5

**Feedback Collection Dataset**:
| Component | Count |
|-----------|-------|
| Score Rubrics | 1,000 (fine-grained, customized) |
| Instructions | 20,000 (20 per rubric) |
| Responses & Feedback | 100,000 (5 scores per instruction) |

**Rubric Format**:
- **Criteria description**: "The pivotal aspects essential for addressing the given instruction"
- **Score descriptions (1-5)**: Detailed specifications for each level
- Examples: "Child-Safety", "Creativity", "Is the response formal enough to send to my boss?"

**Performance Results**:
| Metric | PROMETHEUS | GPT-4 | ChatGPT |
|--------|------------|-------|---------|
| Pearson correlation (45 rubrics) | **0.897** | 0.882 | 0.392 |
| Pairwise preference vs GPT-4 | 58.62% preferred | - | - |
| HHH Alignment accuracy | 79.19% | 88.69% | - |

**Prompt Template**:
```
###Task Description:
1. Write detailed feedback based strictly on the score rubric
2. Write score (1-5)
###The instruction to evaluate: [instruction]
###Response to evaluate: [response]
###Reference Answer (Score 5): [reference]
###Score Rubrics: [criteria with 5 descriptions]
```

### Kepler Takeaways
- Custom rubrics enable domain-specific evaluation
- Reference answers help but aren't always required
- PROMETHEUS tends toward critical feedback (useful for finding issues)

---

## Paper 9: JudgeLM

| | |
|---|---|
| **arXiv** | [2310.17631](https://arxiv.org/abs/2310.17631) |
| **Authors** | Lianghui Zhu et al. |
| **Date** | Oct 2023 |
| **Venue** | ICLR 2025 Spotlight |
| **GitHub** | [baaivision/JudgeLM](https://github.com/baaivision/JudgeLM) |

### Key Contributions

**Scalable fine-tuned judges (7B, 13B, 33B)**

**Training Data**:
- 105K seed questions from Alpaca-GPT4, Dolly-15K, GPT4All-LAION, ShareGPT
- 100K training samples, 5K validation samples
- All judgments from GPT-4 teacher

**Three Bias Mitigation Techniques**:

| Technique | Target Bias | Method | Impact |
|-----------|-------------|--------|--------|
| **Swap Augmentation** | Position | Swap answer positions during training | +5.44% consistency |
| **Reference Support** | Knowledge | Include reference answers | Enables external knowledge |
| **Reference Drop** | Format | Randomly remove references | Flexible with/without refs |

**Performance Results**:
| Metric | JudgeLM-33B |
|--------|-------------|
| Agreement with GPT-4 (internal) | **89.03%** |
| Agreement with humans (PandaLM test) | **75.18%** |
| Consistency (swap test) | **91.36%** |
| Human-to-human agreement | 82% |

### Kepler Takeaways
- Swap augmentation: simple technique, big improvement (+5.44%)
- JudgeLM exceeds human-to-human consistency (91% vs 82%)
- Reference support/drop gives flexibility

---

## Paper 10: PandaLM

| | |
|---|---|
| **arXiv** | [2306.05087](https://arxiv.org/abs/2306.05087) |
| **Authors** | Yidong Wang et al. |
| **Date** | Jun 2023 |
| **GitHub** | [WeOpenML/PandaLM](https://github.com/WeOpenML/PandaLM) |

### Key Contributions

**Training Methodology**:
- Two-stage: GPT-3.5 distillation + noise filtering
- LLaMA backbone with cross-entropy loss
- Position bias filtering: remove samples where swapped order produces conflicts
- Final: 300K cleaned training dataset
- Setup: DeepSpeed ZeRO Stage 2, 8x A100 GPUs, 2 epochs, AdamW

**Evaluation Dimensions** (beyond correctness):
- Relative conciseness
- Clarity
- Comprehensiveness
- Formality
- Instruction adherence
- Logical fallacies, repetitions, grammatical errors

**Performance Results**:
| Model | Accuracy |
|-------|----------|
| PandaLM-70B | **0.6687** |
| GPT-4 | 0.6647 |
| PandaLM-7B vs GPT-3.5 | 93.75% F1 |
| PandaLM-7B vs GPT-4 | 88.28% F1 |

**Human Eval**: PandaLM-tuned models achieved 79.8 superior vs 25.2 inferior responses against Alpaca baselines

**Bias Mitigation**:
- Response order swapping with conflict removal
- Inter-Annotator Agreement (IAA) threshold: 0.85
- 3 independent human annotators per sample

### Kepler Takeaways
- PandaLM-70B actually **outperforms GPT-4** (0.6687 vs 0.6647)
- Position bias filtering during training is effective
- No API = no data leakage concerns

---

## Paper 11: Auto-J

| | |
|---|---|
| **arXiv** | [2310.05470](https://arxiv.org/abs/2310.05470) |
| **Authors** | Junlong Li et al. (GAIR) |
| **Date** | Oct 2023 |
| **Venue** | ICLR 2024 |
| **GitHub** | [GAIR-NLP/auto-j](https://github.com/GAIR-NLP/auto-j) |

### Key Contributions

**13B generative judge for real-world scenarios**

**58 Scenarios Across 8 Categories**:
| Category | Scenarios |
|----------|-----------|
| Summarization | Post, text, note (3) |
| Exam Questions | Math reasoning, with/without math (3) |
| Code | Generation, simplification, explanation, correction, translation (5) |
| Creative Writing | Lyrics, social media, essays, blogs, ads, presentations (8) |
| Functional Writing | Product descriptions, news, bios, legal/technical docs, recipes (9) |
| Rewriting | Simplification, polishing, instructional, correction, paraphrasing (5) |
| General Communication | Brainstorming, planning, advice, fact-checking, chitchat (11) |
| NLP Tasks | Ranking, translation, analysis, classification, extraction (11) |

**Three Evaluation Modes**:
1. **Eval-P (Pairwise)**: "The key factors to distinguish: [factors]. Final decision: Response 1/2/Tie"
2. **Eval-C (Critique)**: Detailed critiques without explicit criterion names
3. **Eval-R (Rating)**: 1-10 ratings for best-of-N selection

**Performance Results**:
| Metric | Auto-J | ChatGPT | Claude-2 |
|--------|--------|---------|----------|
| Human agreement (pairwise) | **55.0%** | 42.7% | 42.6% |
| Spearman with GPT-4 (AlpacaEval) | **0.97** | - | - |

**Training Data**: 3,436 pairwise + 960 single-response + 332 hand-crafted criteria

### Kepler Takeaways
- 58 scenarios demonstrate broad generalizability
- Natural language critiques are interpretable
- 0.97 correlation with GPT-4 on system-level ranking

---

## Paper 12: TIGERScore

| | |
|---|---|
| **arXiv** | [2310.00752](https://arxiv.org/abs/2310.00752) |
| **Authors** | Dongfu Jiang et al. (TIGER Lab) |
| **Date** | Oct 2023 |
| **Venue** | TMLR 2024 |
| **GitHub** | [TIGER-AI-Lab/TIGERScore](https://github.com/TIGER-AI-Lab/TIGERScore) |

### Key Contributions

**Explainable, reference-free metric**

**Error Analysis Format** (4 components per error):
```json
{
  "location": "where the error occurs",
  "aspect": "error category (relevance, accuracy, fluency)",
  "explanation": "description + suggested correction",
  "penalty": -0.5 to -5.0
}
```
Final score = sum of all penalties (0 = perfect)

**MetricInstruct Dataset**:
| Source | Details |
|--------|---------|
| Real-world | 50+ models, 23 datasets, 6 tasks |
| Synthetic | GPT-4 generated errors for balance |
| Total | 42,484 instances |
| Filtering | ~35% removed for anomalies, +15% GPT-4 filtering |

**6 Tasks Covered**: Summarization, translation, data2text, long-form QA, math, instruction-following

**Performance Results**:
| Metric | TIGERScore-13B |
|--------|----------------|
| Kendall correlation (7 tasks) | **33.73** avg |
| vs reference-free baselines | +15% |
| vs reference-based baselines | +8% |
| Explanation accuracy (human) | **70.8%** |

### Kepler Takeaways
- Error localization enables actionable feedback
- Penalty-based scoring is intuitive and interpretable
- Reference-free outperforms most reference-based metrics

---

# Self-Improvement & Meta-Judging

## Paper 13: Self-Rewarding Language Models

| | |
|---|---|
| **arXiv** | [2401.10020](https://arxiv.org/abs/2401.10020) |
| **Authors** | Weizhe Yuan et al. (Meta) |
| **Date** | Jan 2024 |
| **Focus** | Self-improvement via self-judging |

### Key Contributions

**LLM judges itself during training**

**Iterative DPO Process**:
1. Model generates responses
2. Model judges its own responses (LLM-as-Judge prompt)
3. Use judgments as rewards for training
4. Repeat

**Result**: Llama 2 70B outperforms Claude 2, Gemini Pro, GPT-4 0613 on AlpacaEval 2.0

**Key Insight**: Judgment ability improves alongside generation ability

### Kepler Takeaways
- Self-judging can drive improvement
- Iterative refinement is powerful

---

## Paper 14: Meta-Rewarding Language Models

| | |
|---|---|
| **arXiv** | [2407.19594](https://arxiv.org/abs/2407.19594) |
| **Authors** | Meta AI |
| **Date** | Jul 2024 |
| **Focus** | LLM-as-a-Meta-Judge |

### Key Contributions

**Three Roles for the LLM**:
1. **Actor**: Generate responses
2. **Judge**: Assign rewards to responses
3. **Meta-Judge**: Evaluate its own judgments

**Training Loop**:
- Judgments → preference pairs → improve acting
- Meta-judgments → preference pairs → improve judging

**Results**: Llama-3-8B win rate 22.9% → 39.4% (AlpacaEval 2)

### Kepler Takeaways
- Judging ability can be explicitly trained
- Meta-judging provides feedback loop

---

# Critique Generation

## Paper 15: CritiqueLLM

| | |
|---|---|
| **arXiv** | [2311.18702](https://arxiv.org/abs/2311.18702) |
| **Authors** | Pei Ke et al. (Tsinghua) |
| **Date** | Nov 2023 |
| **GitHub** | [thu-coai/CritiqueLLM](https://github.com/thu-coai/CritiqueLLM) |

### Key Contributions

**Problem**: Existing models can't generate informative critiques

**Eval-Instruct Method** (automatic data construction):
1. Start with referenced pointwise critiques + pseudo references
2. Apply multi-path prompting strategies
3. Cross-validate to filter contradictions (7.7% elimination)

**Two Multi-Path Prompting Strategies**:
| Strategy | Description |
|----------|-------------|
| **P2P (Pointwise-to-Pairwise)** | Inject individual quality assessments into comparative critiques |
| **R2RF (Referenced-to-Reference-Free)** | Remove direct reference comparisons while preserving specifics |

**Evaluation Framework**:
- Pointwise grading: Rating scores + explanations
- Pairwise comparison: Win/tie/lose + supporting explanations
- Both support referenced and reference-free variants

**Performance Results (AlignBench)**:
| Metric | CritiqueLLM | ChatGPT | GPT-4 |
|--------|-------------|---------|-------|
| System-level Pearson (referenced) | **0.995** | - | 0.995 |
| Reference-free Pearson | **0.366** | 0.292 | - |
| Pairwise agreement (referenced) | **70.56%** | - | - |
| Pairwise agreement (ref-free) | **58.81%** | - | - |

**Beats GPT-4** in 3/8 tasks in reference-free setting

### Kepler Takeaways
- Multi-path prompting creates better training data
- CritiqueLLM matches GPT-4 on system-level (0.995 correlation)
- Informative critiques enable model improvement

---

# Benchmarks & Evaluation

## Paper 16: WildBench

| | |
|---|---|
| **arXiv** | [2406.04770](https://arxiv.org/abs/2406.04770) |
| **Full Text** | [HTML](https://arxiv.org/html/2406.04770) |
| **Authors** | Multiple institutions |
| **Date** | Jun 2024 |
| **Focus** | Real-world LLM evaluation with task-specific checklists |

### Key Contributions

**Dataset**: 1,024 challenging tasks from real user conversations with 20%+ multi-turn conversations.

**Two Evaluation Metrics**:

| Metric | Description | Correlation |
|--------|-------------|-------------|
| **WB-Reward** | Pairwise comparison with 5 outcomes (much better/slightly better/tie/slightly worse/much worse) | 0.98 Pearson with Chatbot Arena |
| **WB-Score** | Individual 1-10 scoring, rescaled via S'=(S-5)×2 | 0.95 Pearson |

**Task-Specific Checklists**: 5-10 interpretable, easy-to-verify questions per task, generated by GPT-4-Turbo + Claude-3-Opus.

**Length Bias Mitigation**: Converts slight wins/losses to ties when winner exceeds loser by K characters.

**WB-Reward Formula**:
```
+1 for much better
+0.5 for slightly better
0 for tie
-0.5 for slightly worse
-1 for much worse
```

### Kepler Takeaways
- Task-specific checklists improve evaluation quality
- Length bias mitigation is critical (configurable K threshold)
- Real-world queries better test practical performance

---

## Paper 17: RewardBench

| | |
|---|---|
| **arXiv** | [2403.13787](https://arxiv.org/abs/2403.13787) |
| **Full Text** | [HTML](https://arxiv.org/html/2403.13787) |
| **Authors** | Allen AI |
| **Date** | Mar 2024 |
| **Focus** | Benchmarking reward models across categories |

### Key Contributions

**Five Benchmark Categories**:

| Category | Samples | Description |
|----------|---------|-------------|
| Chat | 358 | Basic instruction-following |
| Chat Hard | 456 | Adversarial trick questions |
| Safety | 740 | Refusal behavior testing |
| Reasoning | 1,431 | Code + math problems |
| Prior Sets | 17.2K | Legacy test data |

**Total**: 2,958 prompts with manual validation

**Key Findings**:

| Finding | Details |
|---------|---------|
| **Classifier RMs > DPO** | ArmoRM-Llama3-8B (89.0) vs DPO models (~76) |
| **Chat Hard discriminates** | Most models 45-77% (vs 90%+ on easy chat) |
| **Scale matters** | But architecture improvements (Llama 3 base) matter more |
| **Length bias controlled** | Chosen/rejected response lengths balanced |

**Safety Behavior Categories**:
- Over-refusing (harms legitimate requests)
- Balanced (appropriate patterns)
- Under-refusing (permits harmful content)

### Kepler Takeaways
- Test judges on adversarial/hard cases, not just easy ones
- Classifier-based reward models outperform DPO
- Safety evaluation requires nuanced behavioral analysis

---

## Paper 18: JudgeBench

| | |
|---|---|
| **arXiv** | [2410.12784](https://arxiv.org/abs/2410.12784) |
| **Authors** | Multiple institutions |
| **Date** | Oct 2024 |
| **Venue** | ICLR 2025 |
| **Focus** | Challenging benchmark for evaluating LLM judges |

### Key Contributions

**Novel Dataset Construction**: Pipeline for converting difficult datasets into challenging response pairs with objective correctness labels.

**Four Domains Tested**:
- Knowledge
- Reasoning
- Mathematics
- Coding

**Judge Types Evaluated**:
- Prompted judges
- Fine-tuned judges
- Multi-agent judges
- Reward models

**Critical Finding**: "Many strong models (e.g., GPT-4o) performing just slightly better than random guessing" on JudgeBench.

### Kepler Takeaways
- Current LLM judges struggle with objectively difficult problems
- Don't assume judge accuracy from easy task performance
- Need challenging benchmarks for judge evaluation

---

## Paper 19: FLASK (Fine-grained Language Model Evaluation)

| | |
|---|---|
| **arXiv** | [2307.10928](https://arxiv.org/abs/2307.10928) |
| **Full Text** | [HTML](https://arxiv.org/html/2307.10928) |
| **Authors** | KAIST AI |
| **Date** | Jul 2023 |
| **Venue** | ICLR 2024 Spotlight |
| **Focus** | Fine-grained skill-based evaluation |

### Key Contributions

**Four Primary Abilities & 12 Skills**:

| Ability | Skills |
|---------|--------|
| **Logical Thinking** | Logical Correctness, Logical Robustness, Logical Efficiency |
| **Background Knowledge** | Factuality, Commonsense Understanding |
| **Problem Handling** | Comprehension, Insightfulness, Completeness, Metacognition |
| **User Alignment** | Readability, Conciseness, Harmlessness |

**Dataset**: 1,740 instances from 122 datasets with difficulty tiers (1-5).

**Correlation Results**:

| Evaluator | Skill-Specific | Skill-Agnostic |
|-----------|----------------|----------------|
| GPT-4 | **0.680** Spearman | 0.641 Spearman |

**FLASK-Hard**: 89 expert-level instances where even GPT-4 shows "up to 50% performance degradation."

### Kepler Takeaways
- Skill-specific evaluation outperforms holistic scoring
- Different skills scale differently with model size
- Include expert-level difficulty for robust evaluation

---

## Paper 20: Sage (2025)

| | |
|---|---|
| **arXiv** | [2512.16041](https://arxiv.org/abs/2512.16041) |
| **Date** | Dec 2025 |
| **Focus** | Annotation-free LLM judge evaluation |

### Key Contributions

**Evaluation Framework Based on Rational Choice Theory**:

| Metric | Description |
|--------|-------------|
| **Local Self-Consistency** | Pairwise preference stability across presentations |
| **Global Logical Consistency** | Transitivity across full preference sets |

**Dataset**: 650 questions combining structured benchmarks + real-world queries.

**Critical Findings**:
- Top models (Gemini-2.5-Pro, GPT-5) "fail to maintain consistent preferences in nearly a quarter of difficult cases"
- "Substantial inconsistency in human judgments" - humans may not be reliable ground truth
- Explicit rubrics help models maintain consistency

**Improvement Strategies**:
- Fine-tuned LLM judges
- Panel-based approaches
- Deep reasoning techniques

### Kepler Takeaways
- Even 2025 state-of-the-art models have consistency issues
- Explicit rubrics are essential for reliable evaluation
- Human annotations have their own reliability problems

---

# Bias Mitigation Methods

## Paper 21: PORTIA (Split and Merge)

| | |
|---|---|
| **arXiv** | [2310.01432](https://arxiv.org/abs/2310.01432) |
| **Full Text** | [HTML](https://arxiv.org/html/2310.01432) |
| **Authors** | Multiple institutions |
| **Date** | Oct 2023 |
| **Venue** | EMNLP 2024 |
| **Focus** | Position bias mitigation via content alignment |

### Key Contributions

**Three-Stage Algorithm**:

| Stage | Description |
|-------|-------------|
| **Format Recognition** | Identify split positions at sentence boundaries |
| **Length Alignment** | Divide answers into k segments of comparable length |
| **Semantic Alignment** | Maximize semantic similarity between corresponding segments |

**Results Achieved**:

| Metric | Improvement |
|--------|-------------|
| Consistency rate | +47.46% average relative improvement |
| Fixed coverage | 62.31% of previously inconsistent cases |
| GPT-4 consistency | Elevated to **98%** |
| Cost efficiency | GPT-3.5 achieves 88% GPT-4 agreement at 9.57% cost |

**Testing**: 11,520 answer pairs across 6 LLMs.

**Human validation**: PORTIA-enhanced GPT-3.5 exceeded standalone GPT-4 alignment.

### Kepler Takeaways
- Split-and-merge dramatically reduces position bias
- Can use cheaper models with PORTIA to match expensive model quality
- Content alignment preserves all original information

---

## Paper 22: Length-Controlled AlpacaEval

| | |
|---|---|
| **arXiv** | [2404.04475](https://arxiv.org/abs/2404.04475) |
| **Full Text** | [HTML](https://arxiv.org/html/2404.04475v2) |
| **Authors** | Multiple institutions |
| **Date** | Apr 2024 |
| **Venue** | COLM 2024 |
| **Focus** | Regression-based length bias correction |

### Key Contributions

**Core Problem**: AlpacaEval exhibits strong length bias—verbose models receive artificially higher scores.

**GLM Regression Approach**:
```
winrate^LC(m,b) = 100·E_x[logistic(θ_m−θ_b+(ψ_m−ψ_b)γ_x)]
```
The model zeros out the length component to answer: "What would preferences be if outputs had equal length?"

**Key Results**:

| Metric | Original | Length-Controlled |
|--------|----------|-------------------|
| Chatbot Arena Correlation | 0.94 | **0.98** |
| Length Gameability | 26% | **10%** |
| Adversarial vulnerability | High | Reduced (25.9% → 12.2%) |

**Implementation Details**:
- 805 instructions, 128+ models
- L2 regularization with 5-fold cross-validation
- Maintains [0%, 100%] range for interpretability

### Kepler Takeaways
- Simple regression can effectively debias length preferences
- Proprietary models (often concise) improved in rankings after length control
- Consider length normalization for fair comparison

---

## Paper 23: CALM (Justice or Prejudice)

| | |
|---|---|
| **arXiv** | [2410.02736](https://arxiv.org/abs/2410.02736) |
| **Full Text** | [HTML](https://arxiv.org/html/2410.02736) |
| **Authors** | Multiple institutions |
| **Date** | Oct 2024 |
| **Focus** | Comprehensive bias quantification framework |

### Key Contributions

**12 Identified Biases**:

| Bias Type | Description |
|-----------|-------------|
| Position Bias | Favors answers based on placement |
| Verbosity Bias | Prefers longer responses |
| Compassion-Fade | Influenced by model anonymity |
| Bandwagon | Susceptible to majority opinion |
| Distraction | Impact of irrelevant information |
| Fallacy-Oversight | Overlooks logical errors |
| Authority | Credits fake citations |
| Sentiment | Prefers emotional tone |
| Diversity | Shifts with identity markers |
| CoT Bias | Varies with explicit reasoning |
| Self-Enhancement | Favors own outputs |
| Refinement-Aware | Different when refinement disclosed |

**Methodology**: Attack-and-detect approach with Robustness Rate (RR) and Consistency Rate (CR).

**Models Tested**: ChatGPT, GPT-4-Turbo, GPT-4o, GLM-4, Claude-3.5, Qwen2-72B

**Key Finding**: Claude-3.5 shows greatest resilience; "advanced models may not always exhibit better performance."

### Kepler Takeaways
- Be aware of 12+ bias types affecting LLM judges
- Position bias severity increases with more candidates
- Implement bias detection mechanisms before deployment

---

## Paper 24: Internal Consistency Survey

| | |
|---|---|
| **arXiv** | [2407.14507](https://arxiv.org/abs/2407.14507) |
| **Date** | Jul 2024 |
| **Focus** | Self-feedback framework for LLM consistency |

### Key Contributions

**Self-Feedback Framework**:
- **Self-Evaluation Module**: Captures internal consistency signals
- **Self-Update Module**: Leverages signals to enhance responses

**Three Theoretical Perspectives**:

| Perspective | Description |
|-------------|-------------|
| **Hourglass Evolution** | How consistency evolves through processing stages |
| **Consistency ≈ Correctness** | Relationship between internal consistency and accuracy |
| **Latent vs Explicit Paradox** | Tensions between different reasoning levels |

**Internal Consistency Definition**: "Consistency in expressions among LLMs' latent, decoding, or response layers based on sampling methodologies."

### Kepler Takeaways
- Self-consistency signals can indicate evaluation reliability
- Consider sampling multiple times and checking agreement
- Internal model states may reveal confidence levels

---

# Multi-Judge & Aggregation

## Paper 25: PoLL (Panel of LLM Judges)

| | |
|---|---|
| **arXiv** | [2404.18796](https://arxiv.org/abs/2404.18796) |
| **Full Text** | [HTML](https://arxiv.org/html/2404.18796) |
| **Authors** | Multiple institutions |
| **Date** | Apr 2024 |
| **Focus** | Multi-model ensemble judging |

### Key Contributions

**Aggregation Methods**:

| Task Type | Method |
|-----------|--------|
| QA (binary) | Max voting |
| Chatbot Arena (1-5) | Average pooling |

**Panel Composition**: Command R + Claude Haiku + GPT-3.5 (3 distinct model families)

**Cost Analysis**:

| System | Cost (per million tokens) |
|--------|---------------------------|
| **PoLL (3 models)** | $1.25 input + $4.25 output |
| GPT-4 Turbo | $10 input + $30 output |
| **Savings** | **7-8× cheaper** |

**Bias Reduction**: "Smallest spread in scores, with standard deviation of 2.2" vs GPT-3.5's 6.1.

**Performance Results**:

| Metric | PoLL | GPT-4 |
|--------|------|-------|
| Cohen's κ (Natural Questions) | **0.763** | 0.627 |
| Kendall τ (Chatbot Arena) | **0.778** | 0.667 |

### Kepler Takeaways
- Panel of smaller models beats single GPT-4 at 1/8 cost
- Model diversity in panel reduces individual bias
- Use max voting for binary, average for scores

---

## Paper 26: ChatEval

| | |
|---|---|
| **arXiv** | [2308.07201](https://arxiv.org/abs/2308.07201) |
| **Date** | Aug 2023 |
| **Focus** | Multi-agent debate for evaluation |

### Key Contributions

**Debate-Based Evaluation**: Multiple LLM agents with diverse role prompts engage in structured communication to reach evaluation consensus.

**Architecture**: Decentralized peer ranking through direct LLM-to-LLM communication.

**Key Insight**: Debate forces models to articulate reasoning, exposing weaknesses in arguments.

### Kepler Takeaways
- Consider multi-agent debate for complex evaluations
- Diverse role prompts improve evaluation coverage
- Deliberation can reduce individual model biases

---

# Reference-Free Evaluation

## Paper 27: FActScore

| | |
|---|---|
| **arXiv** | [2305.14251](https://arxiv.org/abs/2305.14251) |
| **Full Text** | [HTML](https://arxiv.org/html/2305.14251) |
| **Authors** | Multiple institutions |
| **Date** | May 2023 |
| **Focus** | Fine-grained atomic fact evaluation |

### Key Contributions

**Atomic Fact Methodology**: Breaks text into "short sentences conveying one piece of information" for granular assessment.

**Scoring Formula**:
```
FActScore = (1/|A_y|) × Σ I[a is supported by C]
```
Percentage of atomic facts supported by knowledge source.

**Three Label Categories**:
- **Supported**: Wikipedia substantiates
- **Not-supported**: Wikipedia contradicts or lacks evidence
- **Irrelevant**: Unrelated to prompt

**Commercial LM Results**:

| Model | FActScore |
|-------|-----------|
| InstructGPT | 42.5% |
| ChatGPT | 58.3% |
| PerplexityAI | 71.5% |
| Human-written | ~88% |

**Key Findings**:
- **Entity frequency effect**: ChatGPT 80% → 16% accuracy for rare vs frequent entities
- **Position bias**: Later facts have higher error rates
- **Citation unreliability**: 36% of citations don't correlate with factual accuracy

**Automated Estimator**: <2% error rate vs human, saving ~$26K in annotation costs.

### Kepler Takeaways
- Atomic decomposition enables precise factuality measurement
- Entity frequency dramatically affects accuracy
- Citations don't guarantee factual accuracy

---

## Paper 28: Themis

| | |
|---|---|
| **arXiv** | [2406.18365](https://arxiv.org/abs/2406.18365) |
| **Full Text** | [HTML](https://arxiv.org/html/2406.18365) |
| **Authors** | Multiple institutions |
| **Date** | Jun 2024 |
| **Venue** | EMNLP 2024 |
| **Focus** | Reference-free NLG evaluation |

### Key Contributions

**Training Methodology** (Llama-3-8B base):
1. Supervised Fine-tuning: 67,180 samples, lr=1e-5, 3 epochs
2. Preference Alignment: 10,000 samples, rating-guided DPO, lr=3e-6

**NLG-Eval Corpus**: 500,000 samples across 9 NLG tasks, 58 datasets.

**Multi-Perspective Consistency Verification**:

| Mechanism | Description |
|-----------|-------------|
| Self-Consistency | Prioritize samples with high GPT-4 sampling agreement |
| Cross-Validation | Compare human and GPT-4 ratings |
| Evaluation Inspection | GPT-4 re-evaluates for analysis/rating consistency |

**Results**:

| Metric | Themis |
|--------|--------|
| Average Spearman | 0.542 (across 6 benchmarks) |
| Unseen task generalization | 0.545 |
| Robustness (perturbation) | 0.787 (better than GPT-4's 0.976) |

### Kepler Takeaways
- Reference-free evaluation is viable with proper training
- Multi-perspective consistency filtering improves data quality
- Smaller specialized models can outperform GPT-4 on robustness

---

## Paper 29: Shepherd

| | |
|---|---|
| **arXiv** | [2308.04592](https://arxiv.org/abs/2308.04592) |
| **Date** | Aug 2023 |
| **Focus** | 7B critique model for LLM outputs |

### Key Contributions

**Model**: 7B parameter model fine-tuned specifically for critiquing LLM outputs and suggesting refinements.

**Training Data**: High-quality feedback dataset curated from community feedback and human annotations.

**Performance**:

| Evaluation | Result |
|------------|--------|
| GPT-4 eval win rate | 53-87% vs alternatives |
| Human eval | "Closely ties with ChatGPT" |

**Key Innovation**: A smaller, specialized model (7B) can match or exceed larger general-purpose models through targeted training.

### Kepler Takeaways
- Specialized critique models can be cost-effective
- Quality training data matters more than model size
- Critique + refinement suggestions are valuable for improvement

---

# Complete Paper List

## All 29 Papers Analyzed

| # | Paper | arXiv | Year | Category |
|---|-------|-------|------|----------|
| 1 | A Survey on LLM-as-a-Judge | [2411.15594](https://arxiv.org/abs/2411.15594) | 2024 | Survey |
| 2 | LLMs-as-Judges Survey | [2412.05579](https://arxiv.org/abs/2412.05579) | 2024 | Survey |
| 3 | From Generation to Judgment | [2411.16594](https://arxiv.org/abs/2411.16594) | 2024 | Survey |
| 4 | LLM-as-a-Judge & Reward Model | [2409.11239](https://arxiv.org/abs/2409.11239) | 2024 | Survey |
| 5 | MT-Bench & Chatbot Arena | [2306.05685](https://arxiv.org/abs/2306.05685) | 2023 | Foundational |
| 6 | G-EVAL | [2303.16634](https://arxiv.org/abs/2303.16634) | 2023 | Foundational |
| 7 | LLM-Eval | [2305.13711](https://arxiv.org/abs/2305.13711) | 2023 | Foundational |
| 8 | PROMETHEUS | [2310.08491](https://arxiv.org/abs/2310.08491) | 2023 | Fine-Tuned |
| 9 | JudgeLM | [2310.17631](https://arxiv.org/abs/2310.17631) | 2023 | Fine-Tuned |
| 10 | PandaLM | [2306.05087](https://arxiv.org/abs/2306.05087) | 2023 | Fine-Tuned |
| 11 | Auto-J | [2310.05470](https://arxiv.org/abs/2310.05470) | 2023 | Fine-Tuned |
| 12 | TIGERScore | [2310.00752](https://arxiv.org/abs/2310.00752) | 2023 | Fine-Tuned |
| 13 | Self-Rewarding LMs | [2401.10020](https://arxiv.org/abs/2401.10020) | 2024 | Self-Improve |
| 14 | Meta-Rewarding LMs | [2407.19594](https://arxiv.org/abs/2407.19594) | 2024 | Self-Improve |
| 15 | CritiqueLLM | [2311.18702](https://arxiv.org/abs/2311.18702) | 2023 | Critique |
| 16 | WildBench | [2406.04770](https://arxiv.org/abs/2406.04770) | 2024 | Benchmark |
| 17 | RewardBench | [2403.13787](https://arxiv.org/abs/2403.13787) | 2024 | Benchmark |
| 18 | JudgeBench | [2410.12784](https://arxiv.org/abs/2410.12784) | 2024 | Benchmark |
| 19 | FLASK | [2307.10928](https://arxiv.org/abs/2307.10928) | 2023 | Benchmark |
| 20 | Sage | [2512.16041](https://arxiv.org/abs/2512.16041) | 2025 | Benchmark |
| 21 | PORTIA | [2310.01432](https://arxiv.org/abs/2310.01432) | 2023 | Bias Mitigation |
| 22 | Length-Controlled AlpacaEval | [2404.04475](https://arxiv.org/abs/2404.04475) | 2024 | Bias Mitigation |
| 23 | CALM | [2410.02736](https://arxiv.org/abs/2410.02736) | 2024 | Bias Mitigation |
| 24 | Internal Consistency Survey | [2407.14507](https://arxiv.org/abs/2407.14507) | 2024 | Bias Mitigation |
| 25 | PoLL | [2404.18796](https://arxiv.org/abs/2404.18796) | 2024 | Multi-Judge |
| 26 | ChatEval | [2308.07201](https://arxiv.org/abs/2308.07201) | 2023 | Multi-Judge |
| 27 | FActScore | [2305.14251](https://arxiv.org/abs/2305.14251) | 2023 | Reference-Free |
| 28 | Themis | [2406.18365](https://arxiv.org/abs/2406.18365) | 2024 | Reference-Free |
| 29 | Shepherd | [2308.04592](https://arxiv.org/abs/2308.04592) | 2023 | Reference-Free |

---

# Summary Comparison

## All Papers at a Glance

| # | Paper | Type | Key Contribution | Kepler Relevance |
|---|-------|------|------------------|------------------|
| 1 | Survey LLM-as-Judge | Survey | Reliability strategies, bias taxonomy | High - bias mitigation |
| 2 | LLMs-as-Judges Survey | Survey | 5-perspective framework, architectures | High - methodology |
| 3 | Generation to Judgment | Survey | What/How/Benchmark taxonomy | Medium - benchmarking |
| 4 | LLM-as-Judge & Reward Model | Survey | Language transfer, error detection gaps | Medium - limitations |
| 5 | MT-Bench/Arena | Foundational | Coined term, 80%+ human agreement | High - validation |
| 6 | G-EVAL | Foundational | CoT + form-filling, probability weighting | High - technique |
| 7 | LLM-Eval | Foundational | Single-prompt multi-dimensional | Medium - efficiency |
| 8 | PROMETHEUS | Fine-tuned | Open-source GPT-4 match, rubrics | High - alternative |
| 9 | JudgeLM | Fine-tuned | Swap augmentation, scalable | High - bias fix |
| 10 | PandaLM | Fine-tuned | Subjective factors, no API | Medium - local |
| 11 | Auto-J | Fine-tuned | 58 scenarios, interpretable | Medium - generality |
| 12 | TIGERScore | Fine-tuned | Error localization, penalties | High - explainability |
| 13 | Self-Rewarding | Self-improve | Self-judging training loop | Low - advanced |
| 14 | Meta-Rewarding | Self-improve | Meta-judge improves judging | Low - advanced |
| 15 | CritiqueLLM | Critique | Informative critiques, multi-path | Medium - feedback |
| 16 | WildBench | Benchmark | Task-specific checklists, 0.98 correlation | High - methodology |
| 17 | RewardBench | Benchmark | 2,958 prompts across 5 categories | High - testing |
| 18 | JudgeBench | Benchmark | Challenging test for judge reliability | High - validation |
| 19 | FLASK | Benchmark | 12 skills, 4 abilities framework | High - decomposition |
| 20 | Sage (2025) | Benchmark | Annotation-free judge evaluation | Medium - validation |
| 21 | PORTIA | Bias Mitigation | Split-and-merge, 98% GPT-4 consistency | **Very High** - bias fix |
| 22 | LC AlpacaEval | Bias Mitigation | Regression-based length debiasing | High - bias fix |
| 23 | CALM | Bias Mitigation | 12 bias types quantified | High - awareness |
| 24 | Internal Consistency | Bias Mitigation | Self-feedback framework | Medium - reliability |
| 25 | PoLL | Multi-Judge | Panel beats GPT-4 at 1/8 cost | **Very High** - cost savings |
| 26 | ChatEval | Multi-Judge | Multi-agent debate for evaluation | Medium - complex tasks |
| 27 | FActScore | Reference-Free | Atomic fact evaluation | Medium - factuality |
| 28 | Themis | Reference-Free | 500K sample corpus, 9 NLG tasks | Medium - NLG eval |
| 29 | Shepherd | Reference-Free | 7B critique model matches ChatGPT | High - cost savings |

---

# Relevance to Kepler

## Current Kepler Setup
Based on the optimizer module:
- Multi-criteria evaluation (accuracy, completeness, evidence quality)
- Binary and numeric scoring
- Rubric-based assessment with dimension weights
- GPT-4o as judge
- Structured JSON output

## What Kepler Is Already Doing Well
| Practice | Source Paper |
|----------|--------------|
| Criteria decomposition | Paper 2 (Methodology) |
| Weighted aggregation | Paper 2 (Multi-LLM) |
| Rubric-based scoring | Paper 7 (PROMETHEUS) |
| Structured output | Paper 1 (Constrained output) |

## Gaps to Address

| Gap | From Paper | Recommendation |
|-----|------------|----------------|
| Position bias | Paper 1, 8 | Swap augmentation |
| Single judge | Paper 2 | Add Claude for ensemble |
| No confidence | Paper 1 | Self-validation step |
| Few-shot missing | Paper 5 | Add 2-3 gold examples |
| No meta-evaluation | Paper 3 | Calibration dataset |
| Simple scores | Paper 11, 14 | Error localization |

---

# Recommended Approach

## Phase 1: Quick Wins

**From Paper 5 (G-EVAL)**:
```
Add CoT reasoning to judge prompts:
1. First, let me identify what the task requires...
2. Now, comparing the expected vs actual output...
3. Based on the rubric criteria...
```

**From Paper 8 (JudgeLM)**:
```python
# Swap augmentation for position bias
def evaluate_with_swap(expected, actual, rubric):
    score_1 = judge(expected, actual, rubric)
    score_2 = judge(actual, expected, rubric)  # swapped
    return (score_1 + score_2) / 2
```

## Phase 2: Reliability

**From Paper 1 (Survey)**:
```python
# Multi-round evaluation
def robust_evaluate(x, rubric, rounds=3):
    scores = [judge(x, rubric) for _ in range(rounds)]
    return statistics.median(scores)

# Confidence filtering
def evaluate_with_confidence(x, rubric):
    result = judge_with_confidence(x, rubric)
    if result.confidence < 0.7:
        flag_for_human_review(x)
    return result
```

## Phase 3: Multi-Judge

**From Paper 2 (Survey)**:
```python
# Ensemble judging
def ensemble_judge(x, rubric):
    gpt4_score = gpt4_judge(x, rubric)
    claude_score = claude_judge(x, rubric)

    if abs(gpt4_score - claude_score) > 0.3:
        # High disagreement - flag for review
        return human_review(x)
    return (gpt4_score + claude_score) / 2
```

## Phase 4: Explainability

**From Paper 11 (TIGERScore)**:
```python
# Error localization
def evaluate_with_explanation(x, rubric):
    return {
        "score": 0.7,
        "errors": [
            {
                "location": "branding_scope field",
                "error": "Classified as CB but evidence suggests OB",
                "penalty": -0.3,
                "suggestion": "Review brand ownership signals"
            }
        ]
    }
```

---

# Additional Resources

## GitHub Repositories
- [Awesome-LLMs-as-Judges](https://github.com/CSHaitao/Awesome-LLMs-as-Judges) - Curated paper list
- [prometheus-eval](https://github.com/prometheus-eval/prometheus-eval) - Open-source judge
- [JudgeLM](https://github.com/baaivision/JudgeLM) - Scalable judges
- [TIGERScore](https://github.com/TIGER-AI-Lab/TIGERScore) - Explainable metric

## Benchmarks
- [MT-Bench](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge)
- [Chatbot Arena](https://chat.lmsys.org/)
- [RewardBench](https://huggingface.co/spaces/allenai/reward-bench)

## Project Pages
- [LLM-as-a-Judge Project](https://llm-as-a-judge.github.io/)
- [TIGERScore Project](https://tiger-ai-lab.github.io/TIGERScore/)

---

*Document created: January 2026*
*Papers analyzed: 29 (from 2023-2025)*
*Full HTML versions analyzed where available*
*For: Kepler AI Classification Project*

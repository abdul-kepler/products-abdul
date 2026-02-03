# Academic Research Prompt Template

Use this prompt to conduct comprehensive academic research on any topic. Replace `{TOPIC}` with your research subject.

---

## The Prompt

```
I need comprehensive academic research on: {TOPIC}

## Research Requirements

1. **Find 15-25+ papers** from arXiv (and similar sources) on this topic
   - Include papers from 2023, 2024, and 2025
   - Cover surveys, foundational papers, and specialized methods
   - Prioritize papers from top venues (NeurIPS, ICLR, EMNLP, ACL, ICML)

2. **Fetch FULL content** from HTML versions (not just abstracts)
   - Use arxiv.org/html/{paper_id} format for detailed extraction
   - Extract: methodology, algorithms, formulas, results tables, key findings
   - If HTML unavailable, use abstract but note the limitation

3. **Organize findings into two documents**:

   **Document 1: Paper-by-Paper Reference**
   - Each paper with: arXiv link, HTML link, authors, date, venue
   - Key contributions, methodology details, performance results
   - Practical takeaways for implementation
   - Categories: Surveys, Foundational, Methods, Benchmarks, etc.

   **Document 2: Approach-by-Approach Analysis**
   - Taxonomy of approaches (how do methods differ?)
   - Common patterns across all approaches
   - Comparison tables (pros/cons, when to use)
   - Implementation code snippets where relevant
   - Decision tree for approach selection

4. **Include throughout both documents**:
   - Clickable arXiv references: [paper_id](https://arxiv.org/abs/paper_id)
   - HTML links where available: [HTML](https://arxiv.org/html/paper_id)
   - Complete paper list table at the end
   - Performance benchmarks with numbers
   - Cost analysis if applicable

5. **Save to**: `docs/academic-research/{topic-name}/`

## Output Format

For each paper, extract:
- **Methodology**: How does it work? What's the algorithm/approach?
- **Key Innovation**: What's new compared to prior work?
- **Results**: Specific numbers (accuracy, correlation, improvement %)
- **Limitations**: What doesn't it solve?
- **Practical Takeaways**: How can we use this?

## Quality Checks
- Verify HTML pages load (some return 404)
- Cross-reference findings across multiple papers
- Note when information comes from abstract vs full paper
- Include 2025 papers for latest developments
```

---

## Example Topics

Replace `{TOPIC}` with any of these or your own:

| Topic | Example Query |
|-------|---------------|
| RAG Systems | "Retrieval-Augmented Generation approaches, chunking strategies, retrieval methods" |
| Prompt Engineering | "Prompt optimization, automatic prompt generation, prompt tuning methods" |
| LLM Fine-tuning | "Parameter-efficient fine-tuning, LoRA, QLoRA, adapter methods" |
| AI Agents | "LLM-based agents, tool use, planning, multi-agent systems" |
| Hallucination Detection | "Factuality verification, hallucination mitigation, grounding methods" |
| Code Generation | "LLM code generation, program synthesis, code evaluation metrics" |
| Multimodal LLMs | "Vision-language models, image understanding, multimodal reasoning" |
| LLM Efficiency | "Model compression, quantization, inference optimization, KV cache" |
| Evaluation Metrics | "NLG evaluation, automatic metrics, human correlation" |
| Safety & Alignment | "RLHF, constitutional AI, red teaming, jailbreak prevention" |

---

## Workflow Used

This is the methodology that produced the LLM-as-a-Judge research:

```
1. Web Search → Find papers on arXiv
   - Search: "{topic} arxiv 2024 2025"
   - Look for survey papers first (they reference other important papers)

2. Fetch Abstract → Get paper overview
   - URL: https://arxiv.org/abs/{paper_id}
   - Extract: title, authors, date, venue, abstract summary

3. Fetch Full HTML → Get detailed content
   - URL: https://arxiv.org/html/{paper_id}
   - Extract: methodology, algorithms, results tables, formulas
   - Note: Some papers don't have HTML versions (404 error)

4. Organize by Category
   - Surveys (comprehensive overviews)
   - Foundational (seminal papers that started the field)
   - Methods (specific techniques/approaches)
   - Benchmarks (evaluation datasets/metrics)
   - Applications (domain-specific uses)

5. Cross-Reference
   - Find common patterns across papers
   - Build comparison tables
   - Identify research gaps

6. Create Documents
   - Paper-by-paper: Reference guide with all details
   - Approach-by-approach: Conceptual analysis and taxonomy
```

---

## Tips for Best Results

1. **Start with surveys** - They cite the most important papers in the field
2. **Check HTML availability** - Not all papers have HTML versions
3. **Include recent papers** - 2024-2025 papers have latest developments
4. **Look for benchmarks** - They help compare approaches objectively
5. **Extract specific numbers** - Accuracy %, correlation scores, cost savings
6. **Note venue/acceptance** - ICLR, NeurIPS, EMNLP papers are peer-reviewed

---

## File Structure

```
docs/academic-research/
├── {topic-name}/
│   ├── {topic}-papers.md          # Paper-by-paper reference
│   ├── {topic}-approaches.md      # Approach analysis
│   └── README.md                  # Summary and key findings
└── RESEARCH_PROMPT_TEMPLATE.md    # This file
```

---

*Template created: January 2026*
*Based on: LLM-as-a-Judge research methodology (29 papers analyzed)*

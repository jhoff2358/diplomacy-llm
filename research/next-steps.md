# Next Steps for Research

## Recent Updates

**January 2, 2026**: Experiment 002 (Multi-Option Planning) completed. Research folder reorganized.

**Key findings from 002:**
- PLAN phase working well for strategic reasoning (exceeded all metrics)
- Core finding: **Spatial/Mechanical Reasoning Gap** (see `findings/spatial-reasoning-gap.md`)
- Deception/information management emerged as sophisticated behavior

---

## Current Priority: Experiment 003

**See: `experiments/003-spatial-learning.md`**

**The question**: Can spatial reasoning limitations be overcome with learning, or is this a fundamental LLM limitation?

**The approach**: Combine the learning mechanisms from Game 001 (explicit reflection works) with the spatial reasoning prompts from Hypothesis 8/10.

**Why this matters**: If spatial reasoning can be learned, we have a path forward. If not, we need to consider structural solutions (external validators, different map representations, etc.).

---

## Background: Spatial/Mechanical Reasoning Gap

**Goal**: Understand when spatial reasoning works vs fails, and design interventions.

**The spectrum of failures observed:**

| Type | Example | Worked? |
|------|---------|---------|
| Simple adjacency | Turkey caught Italy's lie ("EMS doesn't border Greece") | **Yes!** |
| Self-consistency | France ordered conflicting moves | No |
| Counterfactual | Germany's unsound excuse; E/F didn't verify | No |
| Cascade reasoning | Turkey didn't anticipate chain collapse | No |

**Key insight**: Simple adjacency queries work; complex reasoning (counterfactuals, cascades, self-checks) fails.

**Research questions:**
- What makes Turkey/Italy different from Germany/E-F?
- Is this Gemini-specific or LLM-universal?
- Can simple prompts unlock better spatial reasoning?

**Possible Interventions** (not yet tested):
- **Self-check**: "Before submitting, verify each order is mechanically possible"
- **Adversarial verification**: "Could your opponent achieve this differently?"
- **Cascade prompting**: "If move A fails, what happens to move B?"
- **Explicit board state**: Show unit positions in structured format

### 1. Test Hypothesis 1: Structured Error Review
**Goal**: Determine if forcing explicit error review improves learning.

**Implementation**:
- Modify `modes/gunboat/reflect.md` to add error review section
- Run new game with same configuration
- Compare invalid order repetition rate

**Success Criteria**:
- Reduction in Type 1 (Unprocessed Feedback) failures
- No invalid order repeated after first occurrence

### 2. Test Hypothesis 6: Success/Failure Evaluation
**Goal**: Determine if explicit success metrics prevent rationalization loops.

**Implementation**:
- Add strategy audit section to reflect prompt
- Require explicit SC trajectory analysis
- Force consideration of alternatives after 3+ turns of stagnation

**Success Criteria**:
- Reduction in strategic loop duration
- Earlier pivots after stagnation

---

## Medium-Term Research

### 3. Cross-Model Comparison
**Goal**: Determine if findings generalize across models.

**Approach**:
- Run same game configuration with Claude, GPT-4, Gemini
- Compare learning patterns, error rates, strategic adaptation
- Identify model-specific vs. universal failure modes

### 4. Failure Memory Implementation
**Goal**: Test if dedicated failure files improve learning.

**Approach**:
- Create `lessons_learned.md` template
- Prompt agents to document errors and rules
- Measure rule retention and application

### 5. Attention Analysis
**Goal**: Understand where agents focus in context.

**Approach**:
- Vary position of failure feedback in context
- Measure learning rate by feedback salience
- Test graduated context (recent failures highlighted)

---

## Long-Term Questions

### Mechanism Questions
1. **Is the gap attention, memory, or reasoning?**
   - Design experiments to isolate each factor
   - Test with explicit attention prompts
   - Test with shorter/longer context windows

2. **Why did Turkey reflect in 1904 but not 1912?**
   - Analyze context window size at each point
   - Compare error salience (first occurrence vs. late game)
   - Test whether winning position reduces self-criticism

3. **Can we train better in-context learners?**
   - Fine-tune on mistake → reflection → correction sequences
   - Create synthetic training data from game records
   - Reward self-correction in RLHF

### Generalization Questions
1. **Does this apply beyond Diplomacy?**
   - Test similar patterns in other domains (coding, chess, negotiation)
   - Identify domain-specific vs. universal learning failures

2. **Is spatial reasoning the core issue?**
   - Test agents on explicit map/graph problems
   - Compare performance with and without spatial context
   - Design interventions specific to spatial reasoning

---

## Experimental Infrastructure Needs

### Game Runner Improvements
- [ ] Automated game execution with configurable prompts
- [ ] Metrics collection (invalid orders, SC progression, learning events)
- [ ] A/B testing framework for prompt variants

### Analysis Tools
- [ ] Order validity checker (parse orders, check adjacency)
- [ ] Strategic loop detector (identify repeated order patterns)
- [ ] Learning event extractor (find rule documentation in files)

### Visualization
- [ ] SC progression charts
- [ ] Error timeline visualization
- [ ] Learning event highlighting

---

## Research Questions Prioritized

| Priority | Question | Approach |
|----------|----------|----------|
| P0 | What determines spatial reasoning success vs failure? | Compare Turkey/Italy (worked) vs Germany/E-F (failed) |
| P0 | Can simple prompts unlock spatial reasoning? | Test self-check, adversarial verification prompts |
| P0 | Is spatial reasoning gap LLM-universal? | Test same game with Claude, GPT-4 |
| P1 | Does structured error review improve learning? | Run A/B test with modified prompts |
| P1 | Does success/failure evaluation prevent loops? | Run A/B test with strategy audit |
| P1 | Is the gap attention, memory, or reasoning? | Design isolation experiments |
| P2 | Can we train better in-context learners? | Fine-tuning experiments |
| P2 | Does this apply beyond Diplomacy? | Cross-domain testing |

---

## Notes for Future Sessions

When returning to this research:
1. Review `findings/` for current understanding
2. Check `hypotheses/interventions.md` for experiment status
3. Update `data/game-summary.md` with new game results
4. Document new findings in appropriate files

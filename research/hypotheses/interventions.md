# Hypotheses for Improving In-Context Learning

Proposed interventions to test, organized by which failure type they address.

> **Update (Jan 2026)**: Game 002 revealed the **Spatial/Mechanical Reasoning Gap** as a core finding. New hypotheses 8-10 target this specifically. See `findings/spatial-reasoning-gap.md`.

---

## Hypothesis 1: Structured Error Review

**Target**: Type 1 (Unprocessed Feedback)

**Mechanism**: Force agents to explicitly review failed orders before planning new ones.

**Implementation**:
```markdown
Before planning, review your last turn's results:
- Which orders failed? Why did they fail?
- What rule or constraint did you violate?
- How will you avoid this in your new orders?
```

**Prediction**: Should reduce repeated invalid orders by forcing attention to feedback.

**Metrics**:
- Count of repeated invalid orders per game
- Count of rule violations after first occurrence

**Status**: Not tested

---

## Hypothesis 2: Self-Verification Step

**Target**: Type 2 (Rule Without Understanding) and Type 3 (Plan-Action Disconnect)

**Mechanism**: Add explicit verification between planning and order generation.

**Implementation**:
```markdown
Verify each order:
- Does the supporting unit border the target territory?
- Is this move physically possible given the map?
- Does this order match your stated plan?
```

**Prediction**: Should catch geographic errors and plan-order mismatches.

**Metrics**:
- Invalid order rate before/after
- Plan-order consistency score

**Status**: Not tested

---

## Hypothesis 3: Counterfactual Prompting

**Target**: Type 4 (Strategic Rationalization)

**Mechanism**: Ask agents to consider alternatives before committing.

**Implementation**:
```markdown
You're about to order [X].
- What could go wrong?
- Is there an alternative that better serves your stated goal?
- Have you tried this before? What happened?
```

**Prediction**: Should break rationalization loops by forcing explicit consideration of alternatives.

**Metrics**:
- Strategic diversity (unique strategies per game)
- Time to pivot after stagnation

**Status**: Not tested

---

## Hypothesis 4: Failure Memory File

**Target**: Type 1 (Unprocessed Feedback)

**Mechanism**: Create a dedicated file for documenting failures and lessons.

**Implementation**:
- Prompt agents to maintain a `lessons_learned.md` file
- Require consulting this file before orders
- Structure: Date, Error, Rule Learned, How to Avoid

**Prediction**: Makes learned rules more salient in context, reducing attention-based failures.

**Metrics**:
- Rules documented vs. rules followed
- Error repetition rate

**Status**: Not tested

---

## Hypothesis 5: External Validation Layer

**Target**: All types (as safety net)

**Mechanism**: Add a separate validation pass that checks orders against known constraints.

**Implementation**:
After agent generates orders, a validator checks:
- Adjacency requirements (unit borders target)
- Unit type restrictions (armies can't go to sea)
- Consistency with stated plans

**Tradeoffs**:
- Pro: Catches errors before they cause game failures
- Con: This is a band-aid, not true learning
- Con: Agent might rely on validator rather than learning

**Possible Use**: As training signal - show agent which orders would have been rejected.

**Status**: Not tested

---

## Hypothesis 6: Explicit Success/Failure Evaluation

**Target**: Type 4 (Strategic Rationalization)

**Mechanism**: Force explicit evaluation of whether current strategy is working.

**Implementation**:
```markdown
STRATEGY AUDIT (Required):
1. What has your strategy been for the last 2-3 turns?
2. Are you GAINING SCs, STAGNANT, or LOSING SCs?
3. If stagnant/losing for 3+ turns: What DIFFERENT approach could you try?
```

**Prediction**: Should prevent rationalization by requiring explicit success metrics.

**Metrics**:
- Time spent in stagnant strategies
- Strategy pivot rate after SC loss

**Status**: Not tested

---

## Hypothesis 7: Graduated Context Salience

**Target**: Type 1 (Unprocessed Feedback)

**Mechanism**: Make recent failures more salient in context than old history.

**Implementation**:
- Highlight last turn's failures at top of context
- Summarize older history to save tokens
- Weight recent failures in prompt structure

**Prediction**: Should increase attention to recent feedback.

**Metrics**:
- Error repetition rate by recency
- Attention patterns (if measurable)

**Status**: Not tested

---

## Experimental Design

### Baseline
- Current system: reflect-only mode, no structured error review
- Metrics: Error rate, strategic diversity, learning events

### Treatment Groups
Each hypothesis should be tested independently:
1. Control (baseline)
2. Structured Error Review only
3. Self-Verification only
4. Counterfactual Prompting only
5. Combined (all interventions)

### Metrics Framework

**Learning Metrics**:
- Rule violations after first occurrence (should decrease with learning)
- Time to learn (turns between first error and correction)
- Generalization (does learning one rule prevent similar errors?)

**Strategic Metrics**:
- Strategic diversity (unique strategies per agent per game)
- Pivot rate (how quickly agents change failing strategies)
- Win rate (ultimate success measure)

**Efficiency Metrics**:
- Token usage (interventions add prompts)
- Turns to victory/elimination

---

## Priority Order

Based on likely impact and ease of implementation:

1. **Hypothesis 1 (Structured Error Review)** - Low effort, high impact on Type 1
2. **Hypothesis 6 (Success/Failure Evaluation)** - Low effort, high impact on Type 4
3. **Hypothesis 4 (Failure Memory File)** - Medium effort, compounds with H1
4. **Hypothesis 2 (Self-Verification)** - Medium effort, catches Type 2/3
5. **Hypothesis 3 (Counterfactual)** - Medium effort, alternative to H6
6. **Hypothesis 7 (Context Salience)** - Requires code changes
7. **Hypothesis 5 (External Validation)** - Safety net, not learning

---

## Notes

These hypotheses are designed to be **general-purpose** interventions for in-context learning, not Diplomacy-specific fixes. The goal is to understand the mechanisms of in-context learning, not just to make better Diplomacy agents.

---

## Spatial Reasoning Hypotheses (NEW - from Game 002)

These target the Spatial/Mechanical Reasoning Gap discovered in Game 002.

---

## Hypothesis 8: Order Self-Check

**Target**: Spatial reasoning gap (self-consistency failures)

**Mechanism**: Prompt agents to verify each order before submission.

**Implementation**:
```markdown
Before submitting orders, verify each one:
- Is the unit currently in the location you're ordering from?
- Does the target location border the source?
- If supporting, does the supporting unit stay in place? Are you trying to move into its space?
- If part of a chain, what happens if one move fails?
```

**Prediction**: Should catch France-type errors (conflicting orders).

**Metrics**:
- Self-conflicting order rate
- Invalid move rate

**Status**: Not tested

---

## Hypothesis 9: Adversarial Claim Verification

**Target**: Spatial reasoning gap (counterfactual verification)

**Mechanism**: Prompt agents to challenge mechanical claims from others.

**Implementation**:
```markdown
When another player explains why they can't do X:
- Could they achieve the same result with different moves?
- Is their explanation geographically/mechanically sound?
- What are they NOT mentioning?
```

**Prediction**: Should catch Germany-type excuses.

**Metrics**:
- Rate of unsound claims being accepted
- Rate of valid challenges raised

**Status**: Not tested

---

## Hypothesis 10: Cascade Reasoning Prompt

**Target**: Spatial reasoning gap (chain move failures)

**Mechanism**: Force explicit reasoning about dependent moves.

**Implementation**:
```markdown
For chain moves (A→B, B→C, C→D):
- What happens if the final move (C→D) fails?
- Trace backwards: which earlier moves also fail?
- Is this defensive? Could it accidentally block an enemy move?
```

**Prediction**: Should improve Turkey-type chain reasoning.

**Metrics**:
- Chain move success prediction accuracy
- Cascade failure awareness in notes

**Status**: Not tested

---

## Updated Priority Order

Based on Game 002 findings, reordered by likely impact:

1. **Hypothesis 8 (Order Self-Check)** - Direct fix for France-type errors, low effort
2. **Hypothesis 1 (Structured Error Review)** - Still important for Type 1 failures
3. **Hypothesis 10 (Cascade Reasoning)** - Addresses Turkey-type chain issues
4. **Hypothesis 6 (Success/Failure Evaluation)** - Prevents strategic rationalization
5. **Hypothesis 9 (Adversarial Verification)** - Harder to test, but interesting
6. **Hypothesis 2 (Self-Verification)** - Overlaps with H8
7. **Hypothesis 4 (Failure Memory)** - Compounds with H1
8. **Hypothesis 3 (Counterfactual)** - Alternative to H6
9. **Hypothesis 7 (Context Salience)** - Requires code changes
10. **Hypothesis 5 (External Validation)** - Safety net, not learning

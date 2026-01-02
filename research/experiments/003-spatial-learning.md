# Experiment 003: Can Spatial Reasoning Be Learned?

## Research Question

**Can LLMs overcome spatial reasoning limitations through learning, or is this a fundamental limitation?**

## Background

### What We Know

**From Game 001 (Gunboat, 12 years)**:
- Agents CAN learn from mistakes when they explicitly reflect on them
- Passive exposure to feedback doesn't work
- Learning requires: attention → rule extraction → written documentation → reference

**From Experiment 002 (PLAN phase, 3 seasons)**:
- Strategic reasoning works excellently (option generation, deception, perspective-taking)
- Spatial/mechanical reasoning fails for anything beyond simple adjacency queries
- The gap manifests as: conflicting orders, unsound excuses, cascade blindness

### The Open Question

Game 001 showed agents can learn rules like "armies can't support into sea" when they explicitly reflect on failures. But:
- Can they learn to *check for conflicts before submitting*?
- Can they learn to *verify mechanical claims from others*?
- Can they learn to *reason about cascades*?

Or is spatial reasoning fundamentally harder than rule memorization?

## Hypothesis

Spatial reasoning failures can be reduced through a combination of:
1. **Structured self-check prompts** (Hypothesis 8 from interventions.md)
2. **Learning from spatial errors** (applying Game 001's reflection-learning insight)

If agents can learn "armies can't support into sea" through reflection, they should be able to learn "check if supporting units are in the way" too.

## Design

### Interventions to Test

**From Hypothesis 8 (Order Self-Check)**:
```markdown
Before submitting orders, verify each one:
- Is the unit currently in the location you're ordering from?
- Does the target location border the source?
- If supporting, does the supporting unit stay in place? Are you trying to move into its space?
- If part of a chain, what happens if one move fails?
```

**From Hypothesis 10 (Cascade Reasoning)**:
```markdown
For chain moves (A→B, B→C, C→D):
- What happens if the final move fails?
- Trace backwards: which earlier moves also fail?
```

**Learning Integration**:
- If a spatial error occurs, force explicit reflection in lessons_learned.md
- Track whether subsequent seasons show improvement

### Comparison Groups

| Group | Interventions | Purpose |
|-------|---------------|---------|
| A (Control) | Current PLAN phase only | Baseline spatial error rate |
| B (Prompts) | PLAN + self-check prompts | Do prompts alone help? |
| C (Learning) | PLAN + forced reflection on spatial errors | Does learning help? |
| D (Combined) | PLAN + prompts + learning | Synergy? |

### Metrics

**Primary**:
- Self-conflicting order rate (France-type errors)
- Chain move failure prediction (Turkey-type errors)
- Mechanical claim verification rate (Germany-type errors)

**Secondary**:
- Strategic quality (option diversity, adaptation) - shouldn't regress
- Token usage - prompts add overhead
- Learning curve - do errors decrease over seasons?

## Protocol

1. Run each group through a full game (or until clear pattern emerges)
2. Document every spatial reasoning error
3. Track whether errors recur after reflection
4. Compare error rates across groups

## Expected Outcomes

| Outcome | Implication |
|---------|-------------|
| B and C both improve | Multiple paths to spatial reasoning |
| Only B improves | Prompts work, learning doesn't help |
| Only C improves | Learning works, but needs initial failures |
| D >> B or C alone | Synergy between prompts and learning |
| Nothing helps | Spatial reasoning may be a fundamental LLM limitation |

## Status

**Not started** - Waiting for experiment design approval

## Files to Modify

- `modes/base/reflect.md` - Add self-check prompts
- `modes/base/plan.md` - Add cascade reasoning prompts
- Possibly new `modes/spatial/` overlay for spatial-specific interventions

## Related

- `findings/spatial-reasoning-gap.md` - The core finding this builds on
- `findings/reflection-learning-gap.md` - The learning mechanism we're testing
- `hypotheses/interventions.md` - Hypotheses 8 and 10

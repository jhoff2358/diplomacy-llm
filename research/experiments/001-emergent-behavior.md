# Experiment 001: Emergent Behavior Through Minimal Prompts

**Date Started**: January 2026
**Status**: Exploratory (informal testing, no rigorous results yet)

## Hypothesis

LLMs can develop their own best practices for note-taking, planning, and diplomacy without explicit templates or prescribed structures.

## Background

Previous research (see `findings/reflection-learning-gap.md`) showed agents CAN learn when they write about failures, but DON'T learn from passive exposure. The original prompts were highly prescriptive - templates for lessons, categories, planning structures.

**Question**: What happens if we strip away the scaffolding and let behavior emerge naturally?

## Experimental Design

### What We Changed

**Before** (Prescriptive):
```
## PART 1: LEARN FROM LAST SEASON
Look at the game history. Focus on:
- Which of your orders failed? Why?
- Were there any surprises?
...

**Update your lessons learned file(s) with specific, actionable lessons:**

<FILE name="<filename>.md" mode="append">
## [Category]
- [Specific lesson]
</FILE>
```

**After** (Emergent):
```
**DEBRIEF PHASE** (1 of 3)

Each season has three phases:
1. **Debrief** (now) — Private reflection. Review what happened, update your files.
2. **Turn** (next) — Messaging. Talk to other countries, negotiate.
3. **Reflect** — Private again. Finalize strategy and submit orders.

What happened last season? Did anything surprise you? Did any orders fail?

Write anything worth remembering to your files:
<FILE name="<filename>.md" mode="append">...</FILE>
```

### Key Design Decisions

1. **Phase awareness**: Tell them the season structure so they don't try to do everything at once
2. **No templates**: No `[Category]`, `[Goal 1]`, `Talk to [Country] about [topic]`
3. **Light questions**: "Did anything surprise you?" not "Focus on: [list of 5 things]"
4. **Freedom in file organization**: "Use any filename" not "lessons_learned.md"
5. **Turn phase is recurring**: "You'll get several of these" - like checking your phone
6. **Full file access**: Removed append-only restrictions from debrief

### What We're Watching For

**Short-term (seasons 1-3)**:
- [ ] Do they write anything to files during debrief?
- [ ] How do they organize notes? One file? Multiple?
- [ ] Do they plan at all, or just react?
- [ ] Quality of first messages - generic or strategic?

**Medium-term (seasons 4-8)**:
- [ ] Does file organization improve over time?
- [ ] Do some countries develop better practices than others?
- [ ] Are lessons actually referenced later, or just written and forgotten?
- [ ] Do any countries start planning ahead?

**Long-term**:
- [ ] Do countries develop distinct "personalities"?
- [ ] Does any country independently discover useful patterns (e.g., tracking promises)?
- [ ] Do better note-takers perform better in the game?

## Predictions

**Before running**:

1. **Short-term**: Generic, shallow notes. "Need to defend Munich." No structure.

2. **Medium-term**: Differentiation by accident. Some country gets burned badly and writes a detailed post-mortem that actually helps. Others stay shallow.

3. **Long-term**: They will NOT converge on optimal note-taking because:
   - No feedback loop on note quality
   - Context pressure as files grow
   - No meta-learning (can't see how others organize)

4. **What would change our mind**: After 6+ seasons, a country's notes become more structured without prompting, or they reference old lessons appropriately.

## Current Status

Ran informal tests with various prompt variations during 1901. No rigorous data collection - mostly vibes-based exploration to understand agent behavior before committing to a specific approach.

**Observations** (informal):
- Agents do write to files when given freedom
- Quality varies significantly between countries
- Not clear yet if minimal prompts help or hurt

**Next**: Experiment 002 (Multi-Option Planning) builds on this exploration with a more specific hypothesis about strategic flexibility.

## Related Files

- `modes/base/plan.md` - Current planning prompt (evolved from debrief)
- `modes/base/turn.md` - Minimal turn prompt
- `modes/base/reflect.md` - Simplified reflect prompt
- `src/agent.py` - First season detection for debrief

## Future Variations to Test

1. **Cross-pollination**: Let countries occasionally see how others organize files
2. **Explicit feedback**: After adjudication, tell them what worked/failed
3. **Personality seeds**: Initial prompt variations to encourage divergence
4. **Graduated scaffolding**: Start with templates, remove them after 3 seasons

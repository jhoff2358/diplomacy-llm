# Finding: Spatial/Mechanical Reasoning Gap

**Date Discovered**: January 2, 2026
**Related Experiment**: 002-multi-option-planning
**Status**: Core finding - explains multiple observed behaviors

## Summary

LLMs can reason brilliantly about strategy, diplomacy, and deception - but struggle with spatial/mechanical aspects of the game that would be obvious to a human looking at a map. This manifests in multiple ways:

1. **Order generation** - submitting internally conflicting orders
2. **Excuse generation** - making mechanically unsound claims
3. **Claim verification** - accepting others' mechanical claims without checking
4. **Cascade reasoning** - not anticipating what happens when moves fail

Crucially, spatial reasoning **sometimes works** (Turkey catching Italy's geographic lie), which makes this an interesting research target rather than a fundamental limitation.

---

## Case Studies

### Case 1: France Spring 1902 - Conflicting Orders (Clear Error)

```
A PIC S A YOR - BEL   <- Picardy supports (stays in place)
A PAR - PIC           <- Paris tries to move to occupied Picardy (BOUNCES)
```

**Strategic intent**: Support England + reposition toward front
**Mechanical reality**: Supporting unit stays in place; can't move into occupied space
**Result**: Wasted move - Paris army does nothing
**Classification**: Clear spatial reasoning failure

France's strategic reasoning was sophisticated - they identified multiple options, chose trust-rebuilding after analyzing the diplomatic situation, and coordinated with England. The failure isn't in the *thinking* - it's in the *translation to orders*.

### Case 2: Germany Fall 1901 - Unsound Excuse That Worked (Ambiguous)

Germany told both England and France: "I can't support into Belgium because I need Ruhr for Holland"
Ordered: A Ruh -> Hol, A Kie -> Ruh

**Mechanical reality**: Germany could have done A Kie -> Hol directly and used A Ruh to support whoever. Units end up in the same places (Hol, Ruh, Den) either way.

**Result**: E/F bounced in Belgium, Germany got both centers AND maintained "Honest Broker" neutrality

**Open question - was this:**
- **Brilliant meta-play?** Germany knew the excuse was unsound but bet E/F wouldn't notice
- **Lucky mistake?** Germany genuinely believed Ruh was needed for Hol

**Why E/F didn't catch it**: Spatial verification requires asking "wait, couldn't you just do Kie->Hol and use Ruh to support?" - a counterfactual that's harder to reason about than simple adjacency.

### Case 3: Turkey Spring 1902 - Chain Without Understanding Cascade (Soft Error)

Ordered: F Ank -> Con, A Con -> Bul, A Bul -> Gre, F Smy -> Aeg

**Turkey's reasoning** (from notes):
- "Move out of the corner"
- "Threaten Greece"

**What actually happens:**
1. A Bul -> Gre fails (Austria holds Greece)
2. Therefore A Con -> Bul fails (Bul didn't vacate)
3. Therefore F Ank -> Con fails (Con didn't vacate)
4. Whole chain collapses, all units stay in place

**Accidental benefit**: By staying in Bul, Turkey blocked Austria's A Ser -> Bul!

**What Turkey's notes DON'T mention:**
- What if Greece fails?
- What happens to dependent moves if the chain breaks?
- Could this accidentally defend Bulgaria?

**Classification**: Incomplete reasoning that happened to work out. Turkey might conclude "my chain move was good" without understanding that it only worked because of Austria's specific orders.

### Case 4: Turkey Catches Italy - Geographic Reasoning Success!

Italy claimed F ION -> EMS was to "trap Austrian fleet in Greece"
Turkey responded: "EMS borders Smyrna and Syria, but it does NOT border Greece. His claim that it helps 'trap' the Austrian fleet in Greece is geographically false."

**Why this worked**: Simple adjacency query ("Does X border Y?")
**Key insight**: Geographic reasoning CAN work for simple, direct queries

---

## The Spectrum

| Example | Type | Outcome | Did They Understand? |
|---------|------|---------|---------------------|
| France S1902 | Order generation | Wasted move | No - didn't see conflict |
| Germany F1901 | Excuse generation | Benefited Germany | Unclear - lucky or meta? |
| E/F vs Germany | Claim verification | Accepted bad claim | No - didn't verify |
| Turkey S1902 | Cascade reasoning | Accidentally defended Bul | Probably no |
| Turkey vs Italy | Claim verification | Caught the lie | **Yes!** |

---

## What Makes Turkey/Italy Different?

The Turkey/Italy case is our one clear success. Possible factors:

| Factor | Turkey/Italy (worked) | Germany/E-F (failed) |
|--------|----------------------|---------------------|
| **Query type** | Simple adjacency ("Does EMS border Greece?") | Counterfactual ("Could Germany do it differently?") |
| **Stakes** | Turkey directly threatened | E/F trusted "Honest Broker" |
| **Suspicion** | Turkey already suspicious of Italy | E/F not looking for problems |
| **Self vs Other** | Verifying opponent's claim | (N/A - both verifying others) |

**Hypothesis**: Simple geographic queries ("Does X border Y?") work; complex counterfactuals ("Could you achieve X via different moves?") fail.

---

## The Core Research Question

**Can we get LLMs to notice things that are obvious on a map but hard to spot in text?**

The Turkey/Italy case proves it's possible. The question is: what prompts or structures unlock this capability more reliably?

### Types of Spatial Reasoning (in order of apparent difficulty)

1. **Simple adjacency** - "Does X border Y?" → Sometimes works (Turkey/Italy)
2. **Self-consistency** - "Do my orders conflict?" → Failed (France)
3. **Counterfactual** - "Could I achieve this differently?" → Failed (Germany excuse, E/F verification)
4. **Cascade** - "If move A fails, what happens to move B?" → Failed (Turkey chain)

---

## Possible Interventions (Not Yet Tested)

### For Order Generation (France-type errors)
- **Self-check prompt**: "Before submitting, verify each order is mechanically possible"
- **Conflict detection**: "Are any of your units trying to occupy the same space?"
- **Rule reminder**: "Remember: supporting units stay in place"

### For Claim Verification (Germany/E-F type errors)
- **Adversarial prompting**: "Before accepting a claim, ask: could they achieve this differently?"
- **Verification phase**: Explicitly prompt agents to check mechanical claims from others

### For Cascade Reasoning (Turkey-type errors)
- **Dependency prompting**: "If your first move fails, what happens to dependent moves?"
- **Failure simulation**: "Assume move X fails. Trace what happens to the rest of your orders."

### Structural Changes
- **Explicit board state**: Show unit positions visually or in structured format
- **Adjacency reference**: Include a machine-readable map in context

---

## Related Findings

- `reflection-learning-gap.md` - Different failure mode (learning from past mistakes)
- `learning-failure-taxonomy.md` - May need to add "spatial reasoning failures" as a category

---

## Open Questions

1. **Is this Gemini-specific or LLM-universal?** Need to test with Claude, GPT-4
2. **What's the minimum intervention?** Can a simple prompt fix this, or do we need structural changes?
3. **Does the Turkey/Italy success generalize?** Can we prompt for more "Does X border Y?" style checks?
4. **Is the Germany case meta-play or luck?** Would be fascinating if agents learned to exploit others' spatial reasoning weakness

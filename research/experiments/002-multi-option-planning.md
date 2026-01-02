# Experiment 002: Multi-Option Planning

**Date Started**: January 2026
**Status**: Active
**Builds On**: Experiment 001 (Emergent Behavior)

## Hypothesis

Agents get "locked in" to strategies and can't adapt because they commit to a single plan before diplomacy begins. By generating **multiple strategic options** before conversations, agents will have flexibility to pivot based on how diplomacy actually unfolds.

## Background

Experiment 001 tested minimal prompts for emergent behavior. While this was a useful baseline, we observed that agents still tended to commit early to a single strategy and then rationalize their way through conversations rather than genuinely adapting.

The reflection-learning gap research (see `findings/reflection-learning-gap.md`) showed agents CAN learn when they explicitly process information. This experiment tests whether explicit **option generation** before diplomacy enables better adaptation.

## Key Insight

The problem may not be learning from *past* mistakes, but preparing for *future* flexibility. If an agent enters conversations with only one plan, they'll defend it rather than adapt. If they enter with multiple viable options, they can genuinely negotiate.

## Experimental Design

### What We Changed

**Before** (DEBRIEF phase):
```
**DEBRIEF PHASE** (1 of 3)

What happened last season? Did anything surprise you? Did any orders fail?

Write anything worth remembering to your files.
```

**After** (PLAN phase):
```
**PLAN PHASE** (1 of 3)

{if:not_first_season}
Quick check: Did anything go wrong last season? Any failed orders or broken promises worth noting?
{endif}

Now, think about your options for this season:
- What different moves could you make? What are the tradeoffs?
- How might conversations go? What will others want from you?
- When should you be honest vs. strategic with information?

Write your thinking to your files. You don't need to decide yet — just prepare.
```

**REFLECT phase update**:
```
Messaging is over. Look back at the options you considered during planning.
How did conversations change your thinking? Time to decide.
```

### Key Design Decisions

1. **Multiple options, not one plan**: "What different moves could you make?" not "What's your plan?"
2. **Anticipate others**: "What will others want from you?" - think about their perspective
3. **Strategic honesty**: "When should you be honest vs. strategic?" - acknowledge deception as a tool
4. **No commitment yet**: "You don't need to decide yet" - explicitly defer the decision
5. **Light error review**: Keep a brief "did anything go wrong?" but don't make it the focus
6. **Reflect references planning**: Close the loop by asking how conversations changed their thinking

### What We're Watching For

**Option Generation**:
- [ ] Do agents actually generate multiple options, or still commit to one?
- [ ] How concrete are the options? (Vague "attack or defend" vs. specific move sets)
- [ ] Do they consider others' perspectives when generating options?

**Adaptation During Diplomacy**:
- [ ] Do agents reference their options during TURN phase conversations?
- [ ] Do they update their thinking based on what others say?
- [ ] Is there evidence of genuine negotiation vs. just pitching their preferred plan?

**Decision Quality**:
- [ ] In REFLECT, do agents reference the options they considered?
- [ ] Do final orders show influence from diplomatic conversations?
- [ ] Are decisions better reasoned (explicit tradeoff discussion)?

**Comparison to Experiment 001**:
- [ ] More strategic flexibility?
- [ ] Better diplomatic outcomes?
- [ ] Higher quality file organization?

## Predictions

**Before running**:

1. **Option generation will be shallow**: Agents will generate 2-3 options but one will be obviously preferred. They won't genuinely consider alternatives.

2. **Anticipation will help messaging**: Thinking about "what will others want?" should improve first messages. Less generic "let's be friends", more targeted proposals.

3. **Deception framing might backfire**: Explicitly mentioning "honest vs. strategic" could either:
   - Help: Agents think more carefully about information sharing
   - Hurt: Agents become paranoid or overly deceptive

4. **Reflect callback will be ignored**: Agents probably won't reference their earlier options. The context window pressure will push them toward just making a decision.

**What would change our mind**:
- Agents generate genuinely distinct options with real tradeoffs
- REFLECT phase shows explicit "I considered X but after talking to Y, I'm doing Z"
- Diplomatic conversations show agents updating based on new information

## Success Metrics

| Metric | How to Measure | Target |
|--------|----------------|--------|
| Option diversity | Count distinct move sets in plan files | 2+ per country |
| Perspective-taking | References to other countries' interests in plan | Present in 50%+ |
| Adaptation evidence | REFLECT references to plan options | Present in 30%+ |
| Strategic pivots | Orders differ from initial preferred option | Occurs sometimes |

## Related Files

- `modes/base/plan.md` - New plan phase prompt
- `modes/base/reflect.md` - Updated to reference planning
- `experiments/001-emergent-behavior.md` - Previous experiment this builds on

## Results (Game: Spring 1901 - Spring 1902)

**Date**: January 2, 2026
**Model**: Gemini
**Duration**: 3 seasons (Spring 1901, Fall 1901, Winter 1901 builds, Spring 1902 orders)

### Prediction Assessment

| Prediction | Result | Notes |
|------------|--------|-------|
| Option generation will be shallow | **WRONG** | All 7 countries generated genuinely distinct options with real tradeoffs |
| Anticipation will help messaging | **CORRECT** | First messages were targeted proposals, not generic "let's be friends" |
| Deception framing might backfire | **HELPED** | Countries used deception strategically and deliberately (Italy lied to Turkey) |
| Reflect callback will be ignored | **WRONG** | Multiple countries referenced their earlier options when deciding |

### Evidence: Option Generation

**All 7 countries generated multiple strategic options:**

| Country | Options Generated | Specificity |
|---------|-------------------|-------------|
| France | "Security Bounce", "Aggressive Push", "German Pivot" | High - included specific move sets |
| Germany | "Honest Broker" persona with explicit flexibility | High - documented contingencies |
| Austria | "Forward Defense" vs defensive alternatives | High - named specific units |
| Italy | Lepanto, Western Gambit, Austrian Attack | High - standard openings with tradeoffs |
| Russia | "Humble leader" to avoid "Kill the Leader" | Medium - persona-focused |
| Turkey | Juggernaut vs defensive options | Medium - alliance-focused |
| England | Northern Opening with contingencies | High - specific move sets |

**Example (France Spring 1901):**
```
### Strategic Options:
1.  **The Standard Opening:**
    - A Par -> Bur (or Par -> Pic if I trust Germany)
    - A Mar -> Spa
    - F Bre -> MAO
    - *Pros:* Sets up for two builds (Spa/Por).
    - *Cons:* If England moves to the Channel, I'm defending Brest in the Fall.

2.  **The Northern Gamble:**
    - F Bre -> Eng
    - *Pros:* If it works, I control the sea.
    - *Cons:* Permanent enemy in England.

3.  **The Defensive/Supportive:**
    - A Mar S A Par -> Bur
    - *Pros:* Guarantees Burgundy if I really don't trust the Kaiser.
    - *Cons:* Slows down my take of Spain.
```

### Evidence: Perspective-Taking

**All 7 countries showed perspective-taking:**

- **Germany**: Tipped off Austria about Russia/Austria messaging discrepancy to build trust
- **France**: Planned "paranoia-based apology" to England after Belgium betrayal
- **Turkey**: Recognized Italy's EMS move was geographically suspicious ("EMS borders Smyrna and Syria, but it does NOT border Greece")
- **Austria**: Tracked "Central Triple" (Austria/Germany/Italy) understanding each partner's needs
- **Italy**: Understood Turkey would be suspicious and planned deliberate misdirection
- **Russia**: Framed builds as defensive to avoid "Kill the Leader" alliance
- **England**: Understood France's Belgium move was betrayal, not miscommunication

### Evidence: Information Management

**Deception as explicit strategic tool:**

- **Italy** (explicit in notes): "I will tell Turkey I've changed my mind and will move to the Adriatic instead" while actually planning F ION -> EMS
- **Russia**: Played "humble leader" while being the 6-center front-runner
- **Germany**: Used "Honest Broker" persona to play both sides of the Belgium dispute
- **France**: Shared different intel to different neighbors strategically

### Evidence: Adaptation During Diplomacy

**Strategic pivots observed:**

- **France**: Pivoted from Belgium aggression (Fall 1901) to offering support to England (Spring 1902)
- **Germany**: Added `A Hol S A Yor - Bel` during Spring 1902 diplomacy (not in original plan)
- **England**: Went from hostile to accepting "documented bounce" with France
- **Austria**: Adjusted Lepanto timing based on Italy coordination

### Success Metrics - Final Measurements

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Option diversity | 2+ per country | 7/7 countries | **EXCEEDED** |
| Perspective-taking | Present in 50%+ | 7/7 countries | **EXCEEDED** |
| Adaptation evidence | Present in 30%+ | ~4/7 countries | **MET** |
| Strategic pivots | Occurs sometimes | Yes (France, Germany) | **MET** |

### New Finding: Spatial/Mechanical Reasoning Gap

While strategic reasoning improved dramatically, we discovered a deeper issue: agents struggle with spatial/mechanical aspects that would be obvious on a map. See `findings/spatial-reasoning-gap.md` for full analysis.

#### Case 1: France Spring 1902 - Conflicting Orders (Clear Error)
```
A PIC S A YOR - BEL   <- Picardy supports (stays in place)
A PAR - PIC           <- Paris moves to Picardy (BOUNCES)
```
France's strategic intent was sound (support England + reposition), but the orders conflict. A supporting unit stays in place, so PAR can't move there. **Classification**: Clear spatial reasoning failure.

#### Case 2: Germany Fall 1901 - Unsound Excuse That Worked (Ambiguous)
Germany told E/F: "I can't support Belgium, I need Ruh for Holland"
Reality: Could have done Kie->Hol directly and used Ruh to support. E/F bounced, Germany benefited.
**Open question**: Brilliant meta-play (betting E/F won't notice) or lucky mistake?

#### Case 3: Turkey Spring 1902 - Chain Without Understanding Cascade (Soft Error)
Turkey ordered: F Ank -> Con, A Con -> Bul, A Bul -> Gre
Reality: Greece fails → whole chain collapses → accidentally defends Bulgaria from Austria's attack!
Turkey's notes say "move out of corner" and "threaten Greece" but don't mention cascade implications.
**Classification**: Incomplete reasoning that happened to work out.

#### Case 4: Turkey Catches Italy - Geographic Reasoning Success!
Italy claimed EMS was to "trap Austrian fleet in Greece"
Turkey: "EMS borders Smyrna and Syria, but it does NOT border Greece"
**Why it worked**: Simple adjacency query. Geographic reasoning CAN work for direct queries.

#### The Spectrum
| Type | Example | Worked? |
|------|---------|---------|
| Simple adjacency | Turkey vs Italy | **Yes** |
| Self-consistency | France orders | No |
| Counterfactual | Germany excuse / E-F verification | No |
| Cascade reasoning | Turkey chain | No |

### Conclusions

1. **Hypothesis confirmed**: Multi-option planning enables genuine adaptation during diplomacy
2. **Predictions mostly wrong**: Agents performed better than expected on option generation and reflection callbacks
3. **Deception worked well**: Explicit acknowledgment of "honest vs. strategic" led to sophisticated information management
4. **New failure mode discovered**: Strategic reasoning improved, but plan-to-order translation can still fail

### Recommendations

1. Keep the PLAN phase - it's working for strategic reasoning
2. Consider adding order validation to catch execution conflicts
3. Test with other models (Claude, GPT-4) to see if findings generalize

## Future Variations

1. **Explicit option count**: "Generate exactly 3 options" vs. current open-ended
2. **Forced tradeoffs**: Require pros AND cons for each option
3. **Commitment delay**: Don't allow orders until 2nd reflect phase
4. **Option sharing**: Let countries share their options with allies (risky but interesting)
5. **Order validation**: Add a review step before order submission

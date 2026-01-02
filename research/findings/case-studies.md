# Case Studies: Agent-by-Agent Analysis

Detailed analysis of agent behavior across games.

---

## Game 002: PLAN Phase Experiment (Spring 1901 - Spring 1902)

These cases focus on **spatial/mechanical reasoning** - see `spatial-reasoning-gap.md` for full analysis.

### France: Conflicting Orders (Clear Error)
**Season**: Spring 1902

```
A PIC S A YOR - BEL   <- Picardy supports (stays in place)
A PAR - PIC           <- Paris tries to move to Picardy (BOUNCES)
```

**Strategic intent**: Support England + reposition toward front
**Mechanical reality**: Supporting units stay in place; can't move into occupied space
**Result**: Wasted move - Paris army does nothing
**Classification**: Clear spatial reasoning failure (self-consistency)

France's strategic reasoning was sophisticated - they identified multiple options, chose trust-rebuilding after analyzing the diplomatic situation, and coordinated with England. The failure isn't in the *thinking* - it's in the *translation to orders*.

### Germany: Unsound Excuse That Worked (Ambiguous)
**Season**: Fall 1901

Germany told both England and France: "I can't support into Belgium because I need Ruhr for Holland"
```
A Ruh -> Hol
A Kie -> Ruh
```

**Mechanical reality**: Could have done `A Kie -> Hol` directly and used Ruh to support whoever
**Result**: E/F bounced in Belgium, Germany got both centers AND maintained "Honest Broker" neutrality

**Open question**:
- If Germany *knew* the excuse was unsound but bet E/F wouldn't notice → brilliant meta-play
- If Germany genuinely believed Ruh was needed → lucky mistake

**Why E/F didn't catch it**: Spatial verification requires counterfactual reasoning ("wait, couldn't you just do Kie->Hol?") - harder than simple adjacency queries.

### Turkey: Chain Without Understanding Cascade (Soft Error)
**Season**: Spring 1902

```
F Ank -> Con
A Con -> Bul
A Bul -> Gre  <- Fails (Austria holds Greece)
F Smy -> Aeg
```

**What actually happens**:
1. A Bul -> Gre fails (Austria holds Greece)
2. Therefore A Con -> Bul fails (Bul didn't vacate)
3. Therefore F Ank -> Con fails (Con didn't vacate)
4. Whole chain collapses, all units stay in place

**Accidental benefit**: By staying in Bul, Turkey blocked Austria's `A Ser -> Bul`!

**Turkey's reasoning** (from notes): "Move out of corner", "Threaten Greece"
**What's missing**: No mention of cascade implications or defensive benefits

**Classification**: Incomplete reasoning that happened to work out

### Turkey Catches Italy: Geographic Reasoning Success!
**Season**: Fall 1901

Italy claimed `F ION -> EMS` was to "trap Austrian fleet in Greece"
Turkey responded: "EMS borders Smyrna and Syria, but it does NOT border Greece. His claim that it helps 'trap' the Austrian fleet in Greece is geographically false."

**Why this worked**: Simple adjacency query ("Does X border Y?")
**Key insight**: Geographic reasoning CAN work for simple, direct queries

---

## Game 001: Gunboat Experiment (12 years, 1901-1912)

These cases focus on **learning over time** - see `reflection-learning-gap.md` for full analysis.

---

## Turkey (Winner - 14 SCs)

### Overview
Turkey won the game but got stuck in a learning loop at the end. They demonstrated both successful and failed learning.

### Successful Learning: Spring 1904 Naval Support
- **Error**: Ordered armies to support fleet into Ionian Sea
- **Reflection**: Wrote *"A disaster of command... armies cannot support moves into open sea"*
- **Outcome**: Never repeated this class of error
- **Learning Type**: Explicit reflection → Rule extraction → Behavior change

### Failed Learning: Fall 1912 Armenia-Moscow
- **Error**: Ordered `A Arm S Sev - Mos` (invalid - Armenia doesn't border Moscow)
- **Feedback**: Game history showed `FAILS (Army can't support that territory)`
- **Reflection**: No mention in strategy files
- **Outcome**: Repeated exact same error next turn
- **Learning Type**: Type 1 - Unprocessed Feedback

### Strategic Behavior
Turkey showed the best strategic adaptation:
- Named operations with clear objectives
- Explicit phase transitions (consolidation → projection → fortification)
- Willingness to trade territory for position
- Explicit math and contingency planning

**Key Files**:
- `countries/Turkey/reflections.md`
- `countries/Turkey/strategy.md`

---

## France (Survived - 9 SCs)

### Overview
France survived with 9 SCs but got stuck in a 7-year strategic loop.

### The Iron Square Loop
- **Pattern**: Same defensive formation from Fall 1905 to Fall 1912
- **Orders**: `A Bel H`, `A Pic S Bel`, `A Bur S Bel`, `A Gas S Bur`
- **Rationalization**: Called it "impenetrable" rather than questioning its value
- **Learning Type**: Type 4 - Strategic Rationalization

### Key Quote
> "Germany has played defensively for 5 years. He is currently fighting Turkey in the East. A stab now would be suicidal."

This was written while Turkey had 14 SCs and was approaching solo victory. France never questioned whether holding Belgium mattered.

### Missed Opportunity
France spent 1902-1909 destroying England (already dying) while Turkey grew unchecked. No opportunity cost analysis.

**Key Files**:
- `countries/France/strategy.md` (860 lines showing repetition)
- `countries/France/journal.md`

---

## Germany (Survived - 8 SCs)

### Overview
Germany survived with 8 SCs but spent 10 years attacking Belgium with the same failed strategy.

### The Trust Building Loop
- **Pattern**: `A Hol - Bel`, `A Ruh S A Hol - Bel`, `A Mun - Bur` for 10 years
- **Rationalization**: Called it "trust building" and "diplomatic signaling"
- **Learning Type**: Type 4 - Strategic Rationalization

### Key Quote
> "I am doing the exact same thing. I am setting up the shot. Please take it." (to England, who never did)

### Learning Success: Spring 1908 Error
Germany did learn from one error:
> "I committed a rookie blunder ordering `A Ber S Sil - War`. Berlin does not border Warsaw."

However, this learning was specific and didn't generalize to systematic adjacency checking.

**Key Files**:
- `countries/Germany/fall_1904_strategy.md`
- `countries/Germany/fall_1912_strategy.md`
- `countries/Germany/game_notes.md`

---

## Russia (Survived - 2 SCs)

### Overview
Russia collapsed from 5 SCs to 2 but demonstrated good learning from rule violations.

### Successful Learning: Black Sea Support
- **Error**: Ordered `A Sev S F Rum - BLA` (army can't support into sea)
- **Reflection**: Wrote *"My attempt to support a fleet into the Black Sea with an Army in Sevastopol was illegal. A Sev cannot move to BLA, therefore it cannot support a move to BLA."*
- **Rule Extracted**: "Armies cannot swim"
- **Outcome**: Never repeated, pivoted strategy to land expansion

### Strategic Adaptation
Russia adapted to their declining position by adopting a "kingmaker" role - too costly for anyone to eliminate but unable to win.

**Key Files**:
- `countries/Russia/winter_1906_strategy.md`
- `countries/Russia/spring_1907_analysis.md`

---

## England (Eliminated)

### Overview
England was eliminated after 9 years of "perfect defense, zero offense."

### Rule Learning
England documented learning "Armies cannot support Fleets in sea zones" extensively. However:

### Critical Failure: Liverpool-London Move
- **Error**: Ordered `A Lvp -> Lon` (invalid - no land path between them)
- **Context**: Had extensively planned this move in strategy documents
- **Outcome**: France walked into London unopposed
- **Learning Type**: Type 2 - Rule Without Understanding

England learned a specific rule but didn't understand the underlying principle (adjacency requirements).

### Strategic Failure
England maintained the "Iron Bar" defense (`F NTH S F ENG`) for 8 years while slowly dying. Never pivoted to offense.

**Key Files**:
- `countries/England/diplomatic_read.md`
- `countries/England/strategy_england.md`

---

## Italy (Eliminated)

### Overview
Italy had a brilliant start (took Trieste and Budapest in 1901) but overextended against Turkey.

### Strategic Error
Italy correctly identified the Juggernaut threat but thought they could manage it:
> "I have effectively crippled Austria in year 1. This is dangerous."

They knew the danger but didn't pivot to containment.

### Learning Pattern
Italy showed good tactical learning within turns but poor strategic adaptation across years.

**Key Files**:
- `countries/Italy/strategy_journal.md`

---

## Austria (Eliminated)

### Overview
Austria was eliminated early after an aggressive Italian stab in Spring 1901.

### Limited Data
Austria was reduced to a "zombie state" by 1902, providing limited learning data.

### Key Quote
> "The Austrian Empire has been reduced to the City-State of Trieste... If they agree to finish me off, I die. Objective: Survive to 1904."

Austria understood their situation clearly but couldn't prevent it.

**Key Files**:
- `countries/Austria/1901_fall.md`

---

## Cross-Agent Patterns

### Who Learned Best?
1. **Turkey** - Best at explicit reflection and rule extraction (when they did it)
2. **Russia** - Good at learning from rule violations
3. **Germany** - Learned one specific error but rationalized strategic failures
4. **England** - Documented rules but didn't understand underlying principles
5. **France** - Trapped in rationalization loop

### Common Failure Modes
- **Strategic Rationalization**: 3/7 agents (France, Germany, England)
- **Unprocessed Feedback**: 2/7 agents (Turkey late-game, Italy)
- **Rule Without Understanding**: 2/7 agents (England, Germany)
- **Plan-Action Disconnect**: 1/7 agents (Turkey build choice)

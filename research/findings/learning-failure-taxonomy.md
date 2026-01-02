# Taxonomy of Learning Failures

We identified four distinct types of learning failures in the Diplomacy agents.

> **Note**: Types 2 and 3 are closely related to the **Spatial/Mechanical Reasoning Gap** documented in `spatial-reasoning-gap.md`. The underlying issue is that LLMs struggle with map mechanics that would be obvious to a human looking at a board.

---

## Type 1: Unprocessed Feedback

**Definition**: Agent receives explicit failure message but doesn't write about it → no learning occurs.

**Mechanism**: Feedback exists in game history but isn't attended to during reflection.

**Example**: Turkey's Armenia-Moscow support loop
- Agent ordered `A Arm S Sev - Mos`
- Game history showed: `FAILS (Army can't support that territory)`
- Agent's reflections: No mention of this failure
- Agent repeated the exact same invalid order next turn

**Evidence**:
- `countries/game_history.md` lines 1167, 1216
- `countries/Turkey/reflections.md` (notably absent)

**Why It Happens**:
- Game history grows long; individual failures get less attention
- No prompt structure forcing review of failed orders
- Agent focused on "what to do next" rather than "what went wrong"

---

## Type 2: Rule Without Understanding

**Definition**: Agent documents a rule but doesn't understand the underlying principle → applies it inconsistently.

**Mechanism**: Pattern memorization without spatial/causal model.

> **Connection to Spatial Reasoning Gap**: This is a manifestation of the spatial reasoning gap. Agents can memorize "armies can't support into sea" but don't understand the underlying principle (adjacency requirements). See `spatial-reasoning-gap.md` for the full spectrum of spatial reasoning failures.

**Example**: England learned "armies can't support fleets in sea zones" but then tried `A Lvp -> Lon` (invalid - no land path) without recognizing it as the same class of error.

**Evidence**:
- `countries/England/diplomatic_read.md` lines 154-162 (rule documented)
- `countries/England/strategy_england.md` lines 265-295 (invalid move planned)
- `countries/game_history.md` line 529: `A Lvp - Lon FAILS (illegal move, no convoyable path)`

**Why It Happens**:
- Agent learned a specific rule but not the underlying principle (units can only interact with adjacent territories)
- No mental model of the map's topology
- Rules stored as patterns, not as derivations from first principles

---

## Type 3: Plan-Action Disconnect

**Definition**: Agent writes a plan, then generates orders that don't implement it.

**Mechanism**: No verification step between planning and order generation.

> **Connection to Spatial Reasoning Gap**: In Game 002, France demonstrated this by ordering `A PAR - PIC` while also ordering `A PIC S A YOR - BEL`. The plan was sound (support England + reposition), but the agent didn't notice that supporting units stay in place. See `spatial-reasoning-gap.md` Case 1.

**Example**: Turkey planned to move an army north, had 3 open home centers (Ankara, Constantinople, Smyrna), but built in the southernmost one (Smyrna) - maximizing transit time.

**Evidence**:
- `countries/Turkey/strategy.md` lines 669-671: Build `A Smy` with stated goal of marching north
- Ankara was available and would have been 2 turns closer to the front

**Why It Happens**:
- Planning and order generation are separate phases
- No explicit "does this order match my plan?" check
- Agent may be pattern-matching ("build F Smy" is common) rather than reasoning

---

## Type 4: Strategic Rationalization

**Definition**: Agent recognizes stagnation but rationalizes it as intentional.

**Mechanism**: Confirmation bias in self-evaluation.

**Examples**:

### Germany's "Trust Building" (10 years)
- Attacked Belgium with same orders for 10 years
- Quote: *"I am doing the exact same thing. I am setting up the shot. Please take it."*
- Framed repetition as "diplomatic signaling" rather than failed strategy

**Evidence**: `countries/Germany/fall_1904_strategy.md` lines 40-42

### France's "Iron Square" (7+ years)
- Maintained identical defensive formation from Fall 1905 through Fall 1912
- Quote: *"Germany has played defensively for 5 years... A stab now would be suicidal."*
- Rationalized stagnation as "impenetrable" rather than questioning if it mattered

**Evidence**: `countries/France/strategy.md` lines 18-31 (repeated verbatim for 7 years)

**Why It Happens**:
- Agents are good at justifying their decisions post-hoc
- No prompt forcing "is this WORKING?" evaluation
- Defensive success (not losing) conflated with strategic success (winning)

---

## Summary Table

| Type | Failure Mode | Root Cause | Key Example |
|------|--------------|------------|-------------|
| 1 | Unprocessed Feedback | Feedback not attended to | Turkey Arm→Mos loop |
| 2 | Rule Without Understanding | Pattern without principle | England Lvp→Lon move |
| 3 | Plan-Action Disconnect | No verification step | Turkey Smyrna build |
| 4 | Strategic Rationalization | Confirmation bias | Germany 10-year Belgium |

---

## Implications for Agent Design

Each failure type suggests a different intervention:

| Type | Intervention |
|------|--------------|
| 1 | Structured error review before planning |
| 2 | Force explicit verification of each order |
| 3 | Add plan-order consistency check |
| 4 | Require explicit success/failure evaluation |

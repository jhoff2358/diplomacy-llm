# Game 002 Summary: PLAN Phase Experiment

## Game Configuration

| Setting | Value |
|---------|-------|
| Mode | Standard (with messaging) |
| Turn Structure | PLAN → TURN (x3) → REFLECT |
| Model | Gemini |
| Duration | 3 seasons (Spring 1901 - Spring 1902) |
| Status | In progress |

## Key Finding

**Spatial/Mechanical Reasoning Gap**: Strategic reasoning worked excellently, but agents struggle with map mechanics.

## Board State (Spring 1902)

| Country | SCs | Trend |
|---------|-----|-------|
| Russia | 6 | Leading |
| Austria | 5 | Stable |
| England | 5 | Stable |
| France | 5 | Stable |
| Germany | 5 | Stable |
| Italy | 4 | Contested with Turkey |
| Turkey | 4 | Contested with Italy |

## Spatial Reasoning Cases

### Case 1: France Spring 1902 - Conflicting Orders (Clear Error)
```
A PIC S A YOR - BEL   <- Picardy supports (stays in place)
A PAR - PIC           <- Paris tries to move to Picardy (BOUNCES)
```
**Result**: Wasted move - Paris army does nothing.

### Case 2: Germany Fall 1901 - Unsound Excuse That Worked (Ambiguous)
Germany told E/F: "I can't support Belgium, I need Ruh for Holland"
```
A Ruh -> Hol
A Kie -> Ruh
```
**Reality**: Could have done `A Kie -> Hol` and used Ruh to support either side.
**Result**: E/F bounced in Belgium, Germany got both centers AND stayed "neutral."
**Open question**: Brilliant meta-play or lucky mistake?

### Case 3: Turkey Spring 1902 - Chain Without Understanding Cascade (Soft Error)
```
F Ank -> Con
A Con -> Bul
A Bul -> Gre  <- Fails (Austria holds Greece)
F Smy -> Aeg
```
**What happens**: Greece fails → whole chain collapses → all units stay in place.
**Accidental benefit**: Turkey blocks Austria's `A Ser -> Bul`!
**Classification**: Incomplete reasoning that happened to work out.

### Case 4: Turkey Catches Italy - Geographic Reasoning Success!
Italy claimed `F ION -> EMS` was to "trap Austrian fleet in Greece."
Turkey responded: "EMS borders Smyrna and Syria, but it does NOT border Greece."

**Why it worked**: Simple adjacency query ("Does X border Y?").

## Strategic Successes

Unlike spatial reasoning, strategic reasoning worked excellently:

| Metric | Target | Actual |
|--------|--------|--------|
| Option diversity | 2+ per country | 7/7 |
| Perspective-taking | 50%+ | 7/7 |
| Adaptation | 30%+ | ~4/7 |
| Strategic pivots | Sometimes | Yes |

**Highlights**:
- Italy successfully lied to Turkey about fleet movements
- Germany played "Honest Broker" while benefiting from E/F conflict
- France pivoted from aggression to offering support after diplomatic tension
- Turkey caught Italy's geographic lie

## Key Events

### Spring 1901
- Standard openings across the board
- Germany adopts "Honest Broker" persona

### Fall 1901
- France takes Belgium (breaking trust with England)
- Germany's "I need Ruh for Hol" excuse works
- Italy lies to Turkey about EMS move

### Spring 1902
- France offers support to England (pivot from aggression)
- Turkey catches Italy's geographic lie
- France's conflicting orders waste a move
- Turkey's chain move accidentally defends Bulgaria

## Files Generated

Country files in `countries/*/`:
- `void.md` - Scratchpad with strategic planning
- `orders.md` - Submitted orders
- `strategy.md` - Strategic notes
- `lessons_learned.md` - Accumulated lessons

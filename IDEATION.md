# Diplomacy LLM - Future Improvements & Ideas

This document contains ideas for improving the strategic depth and long-term planning capabilities of the LLM agents. These are **not backwards compatible** with current games and represent potential future directions.

---

## Problem Statement

### Current Limitations
1. **Context Window Bloat**: All conversation history is loaded in full, consuming massive token budget
2. **Short-term Thinking**: Plans and notes only reflect current season, no multi-season strategy
3. **Tactical Blindness**: Missing subtle Diplomacy mechanics (coast rules, support cutting, convoy tactics)
4. **No Strategic Continuity**: Each turn is somewhat isolated, no building institutional memory
5. **Shallow Analysis**: Quick tactical decisions without deep board evaluation

### Real Example
England repeatedly used `F Nor S F Bar -> Stp` instead of the superior `A Nor -> Stp, F Bar S A Nor -> Stp` which prevents Sweden from cutting support (since Sweden can only access St. Petersburg's south coast). This is a subtle tactical awareness issue.

---

## Solution 1: Hierarchical Memory System

### Overview
Replace the flat `plans.md` and `notes.md` with a multi-layered memory hierarchy that separates strategic thinking from tactical execution.

### File Structure
```
<Country>/
├── strategy.md          # Long-term strategic goals (rarely updated, high-level)
├── tactical_analysis.md # Deep tactical insights and board analysis
├── plans.md            # Current season operational plans
├── notes.md            # Short-term tactical observations
└── conversation_summaries.md  # Condensed conversation history
```

### `strategy.md` - Long-Term Strategic Goals
**Updated:** Every 2-4 seasons, or when major strategic shifts occur
**Model:** Main (expensive) model

**Contents:**
- **Win Condition**: What victory path is being pursued (e.g., "Mediterranean dominance", "Northern alliance", "Central stalemate line")
- **Multi-Season Objectives**: 3-5 season lookahead
- **Core Alliances**: Which alliances are strategic vs. tactical
- **Territorial Goals**: Long-term SC targets and defensive positions
- **Endgame Vision**: What does the board look like at 10+ SCs?

**Example:**
```markdown
# England Strategy - Updated Spring 1903

## Win Condition
Northern Fleet Dominance - Control Scandinavia, penetrate Baltic, pressure St. Petersburg

## Multi-Season Objectives (Next 5 Seasons)
1. Secure Norway permanently (F1903-F1904)
2. Contest Sweden with Russia (S1904-W1904)
3. Establish Baltic presence (F1904-S1905)
4. Decision point on France: Maintain alliance or pivot west (F1905)

## Core Alliances
- **France**: Strategic partner through 1905. Critical for Western security.
- **Russia**: Tactical accommodation. Expect conflict post-1904 over Scandinavia.

## Territorial Goals
- Primary: Norway, Sweden, Denmark, St. Petersburg
- Secondary: Holland, Belgium (if France alliance breaks)
- Defensive: Maintain Channel dominance, never let fleets into Irish Sea

## Endgame Vision
12-14 SC position controlling North Sea, Norwegian Sea, and Baltic.
Stalemate line through Scandinavia-Prussia-Silesia if needed.
```

### `tactical_analysis.md` - Deep Board Analysis
**Updated:** Every season, during strategic review phase
**Model:** Main (expensive) model

**Contents:**
- **Current Board Evaluation**: SC count, unit positioning, control zones
- **Tactical Opportunities**: Specific move sequences available
- **Threat Assessment**: What attacks could happen next season
- **Mechanical Insights**: Coast rules, convoy routes, support cutting opportunities
- **Key Chokepoints**: Critical territories for control
- **Unit Efficiency**: Fleet vs. Army needs by region

**Example:**
```markdown
# England Tactical Analysis - Spring 1903

## Board Evaluation
- SCs: 5 (England: 3, Norway: 1, Denmark: 1)
- Fleet Superiority: Strong in North Sea, contested in Norwegian Sea
- Army Weakness: Only 1 army, limits land pressure

## Tactical Opportunities This Season
1. **St. Petersburg North Coast Attack**
   - Current: F Barents supports F Norway -> St. Petersburg (vulnerable to Swe cut)
   - Superior: A Norway -> St. Petersburg (nc), F Barents supports
   - Why: Sweden can only access Stp(sc), cannot cut support from Barents!
   - Risk: Medium - Russia may defend with F Stp(sc) -> BOT

2. **Swedish Pressure**
   - Option A: Wait for Russian conflict in south
   - Option B: Coordinate with Germany for dual pressure
   - Recommendation: Wait - Germany is unreliable

## Threat Assessment
- **France**: Low immediate threat, but watch English Channel
- **Germany**: Medium - could move on Holland/Belgium if I'm distracted
- **Russia**: High - Will contest Scandinavia aggressively

## Mechanical Insights
- St. Petersburg coast rules create support cutting asymmetries
- Norwegian Sea convoys possible but risky with Russian fleets
- Denmark is a critical chokepoint for Baltic access

## Unit Efficiency
- Need 2-3 fleets in Norwegian Sea region for dominance
- Consider army build in London for flexibility
- Fleet in North Sea is defensive anchor, don't move
```

### `plans.md` - Current Season Operational Plans
**Updated:** Every turn
**Model:** Main model during turn

Same as current implementation - focused on immediate actions and diplomacy.

### `notes.md` - Short-term Tactical Notes
**Updated:** Every turn
**Model:** Main model during turn

Same as current implementation - quick observations, message tracking.

### `conversation_summaries.md` - Condensed History
**Updated:** Automatically when conversations exceed N messages
**Model:** Cheap model

**Format:**
```markdown
## France
**Last 10 messages**: [full text of recent messages]

**Earlier conversation summary** (40 messages):
- Spring 1901: Agreed to Channel DMZ, coordinate on Scandinavia
- Fall 1901-Spring 1902: Planned Belgium/Holland division if Germany weakens
- Fall 1902: Discussed Russia as long-term threat, maintain current borders
- Winter 1902: Reaffirmed alliance, France to pressure Iberia
```

### Implementation Notes
- **Context Loading Priority**: Strategy → Tactical Analysis → Plans → Notes → Recent Conversations → Summaries
- **Token Budget**: Reserve 40% for strategy/tactical, 60% for current operations
- **Update Triggers**:
  - Strategy: Manual command or every 2-4 seasons
  - Tactical: Before each season starts
  - Plans/Notes: Every turn (current behavior)

---

## Solution 2: Conversation Summarization

### Problem
By Spring 1903, conversations can be 100+ messages. Loading all of them eats the context window and provides diminishing value.

### Approach
Keep recent messages in full, summarize older history.

### Implementation

#### Conversation Structure
```markdown
## Spring 1901
[Messages 1-10]

## Fall 1901
[Messages 11-25]

## SUMMARY: Spring 1901 - Fall 1901
- Established alliance against Russia
- Agreed to bounce in Black Sea
- Coordinated on Balkans division
[...condensed from 25 messages to ~100 words]

## Winter 1901
[Messages 26-30]

## Spring 1902
[Messages 31-50]

## RECENT (Last 20 messages)
[Full text of last 20 messages]
```

#### Summarization Command
```bash
python3 diplomacy.py summarize
```

- Reads all conversation files
- For each conversation with >40 messages:
  - Keep last 20 messages in full
  - Summarize messages 21-40 by season (cheap model)
  - Summarize messages 41+ into high-level summary (cheap model)
- Rewrites conversation files with summaries inline

#### Context Loading
`ContextLoader` loads full conversation files (which now contain summaries embedded).

---

## Solution 3: Strategic Review Command

### Purpose
Dedicated deep-thinking session using expensive model to update strategy and tactical analysis.

### Command
```bash
python3 diplomacy.py review <country>
```

Or run for all countries:
```bash
python3 diplomacy.py review-all
```

### Process
1. Load full context (game_history, current strategy, tactical analysis, all conversations)
2. Use **main (expensive) model** with extended thinking prompt
3. Ask LLM to:
   - Evaluate current strategic position
   - Identify tactical opportunities on the board
   - Update multi-season plans
   - Assess alliance value
   - Identify mechanical/tactical insights
4. Write to `strategy.md` and `tactical_analysis.md`
5. **Does NOT send messages or update plans/notes** - pure thinking

### Prompt Structure
```
You are playing as {country} in a Diplomacy game. This is a STRATEGIC REVIEW session.

Your task is to think deeply about your position and update your long-term strategy.

[Full context including game_history, conversations, current strategy, tactical analysis]

Think through the following:

1. STRATEGIC POSITION
   - Where are you now vs. where you want to be in 5 seasons?
   - Which alliances are serving you? Which need to shift?
   - What is your path to 18 SCs?

2. TACTICAL OPPORTUNITIES
   - Analyze the current board deeply
   - What mechanical advantages exist (coasts, supports, convoys)?
   - What move sequences could gain you SCs in next 2-3 seasons?

3. THREATS & VULNERABILITIES
   - Who could attack you and how?
   - What defensive positions do you need to hold?
   - Where are you overextended?

4. MECHANICAL INSIGHTS
   - Coast rules: Any support cutting opportunities?
   - Convoy routes: Any disruption or usage opportunities?
   - Support patterns: What's the optimal way to take key territories?

Output your analysis in two parts:

<STRATEGY>
[Long-term strategic goals, alliances, win condition, 3-5 season objectives]
</STRATEGY>

<TACTICAL_ANALYSIS>
[Deep board analysis, specific opportunities, threats, mechanical insights]
</TACTICAL_ANALYSIS>
```

### When to Run
- Manually when you want deeper thinking
- Optionally: Automatically at start of each year (Spring 1902, Spring 1903, etc.)
- After major board shifts (elimination of a country, major alliance break)

### Cost Consideration
Uses expensive model, so run strategically. But produces much better long-term play.

---

## Solution 4: Diplomacy Tactics Primer

### Problem
LLMs don't inherently know Diplomacy-specific tactics and mechanics.

### Solution
Add a **static knowledge base** to the context that teaches core concepts.

### File: `diplomacy_tactics.md` (Static, Version Controlled)

```markdown
# Diplomacy Tactics Reference

## Coast Mechanics
- Territories with multiple coasts: Spain, Bulgaria, St. Petersburg
- **Critical Rule**: A fleet on one coast can only be supported by units that can reach that coast
- **Example**: St. Petersburg (nc) can be attacked from Barents, but Sweden can only reach St. Petersburg (sc)
  - Therefore: F Barents supports A Norway -> Stp(nc) CANNOT be cut by F Sweden
  - But: F Barents supports F Norway -> Stp(nc) CAN be cut by F Sweden moving to Barents

## Support Cutting
- Any attack on a unit cuts its support (even if attack bounces)
- **Tactical principle**: Identify which enemy units can cut your supports
- **Counter-tactic**: Use units that cannot be cut (wrong coast, blocked paths)

## Convoy Disruption
- To disrupt a convoy, attack any fleet in the convoy chain
- Convoys are vulnerable but powerful for surprise attacks
- **When to convoy**: Surprise attacks, reaching distant targets
- **When not to convoy**: High-risk situations, telegraphed moves

## Common Opening Principles
- England: Secure home centers, contest Norway, watch France
- France: Iberia + neutrals, manage England/Germany/Italy triangle
- Germany: Denmark + Sweden, balance East vs West pressure
- Russia: Scandinavia vs. Balkans choice, watch Austria-Turkey
- Austria: Balkans or Italian focus, DMZ with Italy vs. Russia often critical
- Italy: Austrian threat vs. Western expansion
- Turkey: Balkans priority, manage Austria-Russia relationship

## Stalemate Lines
- Defensive positions that are nearly unbreakable with proper play
- Common lines: Scandinavia-Prussia-Silesia, Iberia-MAO-Ireland
- **Strategic use**: Secure position when ahead, force draws when behind

## Unit Efficiency
- Fleets: Needed for islands, coasts, and sea control
- Armies: Needed for inland territories and flexibility
- **Build decision**: What theaters are you expanding into?

## Alliance Timing
- Early alliances (1901-1903): Critical for expansion, high trust needed
- Mid-game alliances (1904-1907): Tactical, expect betrayal
- Late-game alliances (1908+): Pure strategic calculation, temporary

## Tactical Patterns
- **The Bounce**: Deliberate mutual attack to prevent third party from entering
- **The Convoy Attack**: Unexpected army movement via fleets
- **The Support Swap**: Two units support each other's movements
- **The Beleaguered Garrison**: Defending unit receives multiple supports but also faces multiple attacks (defender holds if support ≥ attacks)
```

### Integration
Add this to context in `ContextLoader.format_context()`:

```python
# Load tactics primer
tactics_file = Path("diplomacy_tactics.md")
if tactics_file.exists():
    tactics = tactics_file.read_text()
else:
    tactics = ""

context = f"""Welcome to the Game of Diplomacy!

You are playing as {self.country}.

# DIPLOMACY TACTICS REFERENCE
{tactics}

# GAME HISTORY
{game_history}
...
```

### Maintenance
- Version controlled with the repo
- Can be expanded as you notice common tactical blindness
- Doesn't cost extra tokens after first inclusion (stays ~2-3KB)

---

## Solution 5: Reflection Command (Manual Deep Thinking)

### Concept
Similar to strategic review, but focused on **one specific question or situation**.

### Command
```bash
python3 diplomacy.py reflect <country> "<question>"
```

### Examples
```bash
# General strategic reflection
python3 diplomacy.py reflect England "Should I break my alliance with France?"

# Tactical analysis
python3 diplomacy.py reflect Germany "What's the best way to take Denmark from Russia?"

# Board evaluation
python3 diplomacy.py reflect Turkey "Am I in a winning position? What's my path to 18 SCs?"
```

### Process
1. Load full context
2. Use main (expensive) model
3. Ask LLM the specific question with full context
4. LLM outputs detailed analysis
5. **Output to terminal only** (doesn't update any files)
6. User can manually incorporate insights into strategy/plans

### Use Case
- Quick tactical questions mid-game
- Evaluating specific diplomatic decisions
- Getting second opinion on a complex situation

---

## Solution 6: XML Tag Extensions

### New Tag: `<STRATEGY>`
Update long-term strategic goals (writes to `strategy.md`).

```xml
<STRATEGY>
Updated win condition: Northern dominance through Scandinavia + Baltic.
Core alliance with France through 1905, then reassess.
Target 12 SCs by Spring 1906.
</STRATEGY>
```

### New Tag: `<TACTICAL>`
Update tactical analysis (writes to `tactical_analysis.md`).

```xml
<TACTICAL>
Key opportunity: St. Petersburg (nc) attack using A Nor + F Bar support.
Sweden cannot cut due to coast mechanics.
Build recommendation: Fleet in London for North Sea dominance.
</TACTICAL>
```

### Parsing
Update `agent.py` to parse these tags and write to appropriate files.

---

## Solution 7: Prompt Engineering for Deeper Thinking

### Current Prompt Issues
- Doesn't encourage multi-season planning
- Doesn't ask for tactical analysis
- Doesn't reference Diplomacy mechanics explicitly

### Improved Turn Prompt

```python
initial_prompt = f"""{context}

Each turn, you should:
1. **Think strategically** - Consider your long-term goals (next 3-5 seasons)
2. **Analyze tactically** - Identify specific opportunities on the board (coast mechanics, support patterns, convoy routes)
3. **Plan diplomatically** - What alliances serve your strategy? Who needs to be managed?
4. **Execute** - Send messages, update your plans and notes

Before taking actions, ask yourself:
- What does the board look like in 3 seasons if my current plan succeeds?
- What tactical opportunities exist right now (support cuts, convoy attacks, coast advantages)?
- Which alliances are strategic (long-term) vs. tactical (temporary)?
- What is my path to 18 supply centers?

**Diplomacy Mechanics Reminder:**
- Coast rules: Some supports cannot be cut (wrong coast)
- Support cutting: Any attack cuts support (even if it bounces)
- Beleaguered garrison: Defender holds if supports ≥ attacks
- Convoys: Vulnerable but powerful for surprise

To take actions this turn, use:

<MESSAGE to="Country">Your message</MESSAGE>
<PLANS>Your updated operational plans for this season</PLANS>
<NOTES>Your tactical notes and observations</NOTES>

Optional (for deeper updates):
<STRATEGY>Your long-term strategic goals (multi-season)</STRATEGY>
<TACTICAL>Specific tactical analysis and opportunities</TACTICAL>

What would you like to do this turn?"""
```

### Changes
- Explicitly asks for 3-5 season lookahead
- Prompts for tactical analysis
- Reminds of key mechanics
- Encourages strategic vs. tactical distinction

---

## Solution 8: Board State Analysis Helper

### Problem
LLMs struggle to "see" the board from text descriptions.

### Solution
**Automated board analysis tool** that parses `game_history.md` and outputs structured analysis.

### Command
```bash
python3 diplomacy.py board-analysis
```

### Output
```markdown
# Board Analysis - Spring 1903

## Supply Center Control
England: 5 (Lon, Lvp, Edi, Nwy, Den)
France: 5 (Par, Mar, Bre, Spa, Por)
Germany: 5 (Ber, Kie, Mun, Hol, Bel)
Russia: 6 (Mos, Stp, Sev, War, Rum, Bul)
Austria: 4 (Vie, Bud, Tri, Ser)
Italy: 4 (Rom, Nap, Ven, Tun)
Turkey: 5 (Con, Ank, Smy, Arm, Gre)

## Unit Counts by Type
England: 4F, 1A
France: 3F, 2A
Germany: 2F, 3A
Russia: 2F, 4A
Austria: 0F, 4A
Italy: 2F, 2A
Turkey: 2F, 3A

## Border Tensions (Countries with Adjacent Units)
- England-Russia: Norwegian Sea, Barents Sea
- England-Germany: North Sea
- France-Germany: Belgium
- Russia-Turkey: Black Sea, Armenia
- Russia-Austria: Galicia
- Austria-Italy: Trieste, Venice

## Growth Trends
▲ Russia: +2 SCs since 1901
▲ Germany: +2 SCs since 1901
▼ Austria: -1 SC since 1901
→ Others: Stable or +1

## Critical Territories (Contested or Strategic)
- Sweden: Unoccupied, contested by England-Russia
- St. Petersburg: Russian, under English pressure
- Serbia: Austrian, under Turkish pressure
- Tunis: Italian, French may contest

## Probable Next Phase Conflicts
1. England vs Russia: Scandinavia (Swe, Stp)
2. Austria vs Turkey: Balkans (Ser, Gre, Bul)
3. Germany: Stable, watching neighbors
```

### Integration
- Can be auto-generated at start of each season
- Included in context for strategic review
- Helps LLMs "see" patterns and power dynamics

---

## Solution 9: Training Data / Fine-Tuning (Long-term)

### Concept
If you play many games, collect the data and fine-tune a model on Diplomacy gameplay.

### Data to Collect
- Board positions at each phase
- Messages sent between countries
- Orders submitted
- Outcomes (who won, who got eliminated, SC counts over time)

### Fine-Tuning Approach
- Train on "good" Diplomacy play (from strong players or successful games)
- Model learns tactical patterns, timing of betrayals, alliance formation

### Challenges
- Need large dataset (many full games)
- Gemini may not support fine-tuning
- Could use OpenAI o1/o3 or other fine-tuneable models

### Value
- Would dramatically improve tactical awareness
- Learn subtle patterns that are hard to prompt-engineer

---

## Solution 10: Multi-Model Architecture

### Concept
Use different models for different tasks based on their strengths.

### Model Assignments
- **Strategic Planning** (review, long-term): Claude Opus / GPT-4 / O1 (best reasoning)
- **Tactical Execution** (turns, messages): Gemini Pro (current setup, good creativity)
- **Summarization** (conversation summaries): Gemini Flash (cheap and effective)
- **Board Analysis** (mechanical calculations): GPT-4o-mini (fast and accurate for structured tasks)

### Benefits
- Optimize cost vs. performance
- Leverage each model's strengths
- Could even have models "debate" strategy (one model's strategy reviewed by another)

### Implementation
Add to `config.yaml`:
```yaml
models:
  strategic: claude-opus-4
  tactical: gemini-3-pro-preview
  summary: gemini-flash-latest
  analysis: gpt-4o-mini
```

---

## Solution 11: Persistent Agent Memory (Advanced)

### Concept
Instead of stateless sessions, maintain a **persistent agent** across turns with memory.

### Architecture
- Each country has a long-running agent with memory
- Agent maintains internal state across turns
- Can "remember" tactical insights without re-loading context

### Challenges
- Requires different infrastructure (not stateless calls)
- More complex to implement
- May reduce transparency (harder to debug)

### Benefits
- Much better long-term continuity
- Can build true "institutional memory"
- More human-like strategic evolution

### Technology
- LangGraph for agent orchestration
- Vector DB (Pinecone, Weaviate) for memory retrieval
- More complex than current architecture

---

## Solution 12: Game Theory Integration

### Concept
Add explicit game theory analysis to tactical thinking.

### Analysis Types
- **Nash Equilibrium**: What are the stable outcomes?
- **Prisoner's Dilemma**: Alliance cooperation vs. betrayal payoffs
- **Commitment Problems**: How to make alliances credible
- **Iterative Elimination**: Remove dominated strategies

### Implementation
- Add game theory primer to context
- Prompt LLMs to think in game theory terms
- Example: "Model the France-England alliance as a repeated prisoner's dilemma"

### Value
- More sophisticated alliance reasoning
- Better betrayal timing
- Clearer risk assessment

---

## Solution 13: Illegal Move Learning & Feedback Loop

### Problem
LLMs sometimes submit illegal moves that get lost in game history:
- **Example 1**: A Bul tried to support BLA (armies can't support into water)
- **Example 2**: A Ukr tried to support Gal (need to specify unit being supported)
- Currently these failures aren't explicitly tracked or learned from

### The Opportunity
**Don't prevent illegal moves** - they're valuable learning experiences! But make sure they're:
1. Explicitly highlighted in game history
2. Tracked in a dedicated learning file
3. Referenced in prompts to encourage learning

### Implementation

#### 1. Illegal Moves Tracker File
Create `<Country>/illegal_moves.md` to track and learn from mistakes:

```markdown
# Illegal Moves Log - Austria

## Fall 1901: Army Bulgaria -> Support Black Sea
**Order Attempted:** A Bul S F Ank -> BLA
**Result:** ILLEGAL - Armies cannot support into sea territories
**Lesson:** Armies can only support into land territories or coastal territories. Use fleets to support naval movements.
**What I Should Have Done:** Move A Bul to another land territory, or use it to support a land attack

## Spring 1902: Army Ukraine -> Support Galicia
**Order Attempted:** A Ukr S Gal
**Result:** ILLEGAL - Support orders must specify which unit is being supported and where it's moving
**Correct Format:** A Ukr S A War -> Gal (support Army Warsaw moving to Galicia)
**Lesson:** Support syntax requires: [Supporting Unit] S [Unit Being Supported] -> [Destination]
```

#### 2. Illegal Move Detection (Optional Automation)
Add a validation helper (doesn't prevent, just detects and logs):

```python
# In diplomacy.py
def validate_orders(country: str, orders_text: str) -> List[str]:
    """
    Parse orders and detect common illegal move patterns.
    Returns list of warnings (but doesn't prevent submission).
    """
    warnings = []

    # Pattern: Army supporting into sea
    if re.search(r'A \w+ S.*->\s*(BLA|MAO|NAO|NWG|BAR|ADR|AEG|ION|TYS|EAS|WES|GOB|BOT|BAL|HEL|SKA|NTH|IRI|ENG|MID)', orders_text, re.IGNORECASE):
        warnings.append("⚠ Army cannot support into pure sea territory")

    # Pattern: Incomplete support syntax
    if re.search(r'S \w+\s*$', orders_text):
        warnings.append("⚠ Support order appears incomplete - need to specify unit and destination")

    # Pattern: Fleet trying to move inland
    if re.search(r'F \w+\s*->\s*(Boh|Tyr|Gal|Sil|War|Mos|Ukr|Ser|Bud|Rum|Bul)', orders_text, re.IGNORECASE):
        warnings.append("⚠ Fleet cannot move to inland territory")

    return warnings
```

**Usage in collect_orders():**
```python
orders = agent.get_orders()

# Validate and warn (but still record)
warnings = validate_orders(country, orders)
if warnings:
    print(f"\n⚠ POSSIBLE ILLEGAL MOVES DETECTED:")
    for warning in warnings:
        print(f"  {warning}")
    print(f"  (Recording anyway for learning purposes)\n")

f.write(orders)
```

#### 3. Game History Formatting for Illegal Moves
When you update `game_history.md` after adjudication, explicitly call out illegal moves:

```markdown
## Fall 1901 - Results

### Austria
- A Vie -> Bud: **Success**
- A Ser H: **Success**
- **A Bul S BLA: ILLEGAL MOVE** ❌
  - **Why:** Armies cannot support into sea territories
  - **Effect:** Unit held in Bulgaria (no support given)

### Turkey
- F Ank -> BLA: **Success** (no support received from Austria)
```

#### 4. Include Illegal Moves in Context
Update `context.py` to load illegal moves log:

```python
def load_illegal_moves(self) -> str:
    """Load the illegal moves learning file."""
    illegal_file = self.country_dir / "illegal_moves.md"
    if illegal_file.exists():
        content = illegal_file.read_text().strip()
        return content if content else "No illegal moves recorded yet."
    return "No illegal moves recorded yet."
```

```python
def format_context(self) -> str:
    """Format all context into a single prompt for the LLM."""

    game_history = self.load_game_history()
    plans = self.load_plans()
    notes = self.load_notes()
    illegal_moves = self.load_illegal_moves()
    conversations = self.load_conversations()

    context = f"""Welcome to the Game of Diplomacy!

You are playing as {self.country}.

# GAME HISTORY
{game_history}

# YOUR ILLEGAL MOVES LOG
{illegal_moves}

**IMPORTANT:** Review your illegal moves log before submitting orders. Learn from past mistakes!

# YOUR PLANS
{plans}
...
```

#### 5. Enhanced Order Prompt
Update `get_orders()` prompt to reference illegal moves:

```python
prompt = f"""{context}

It is time to submit your orders for this phase.

**Before submitting:**
1. Review your ILLEGAL MOVES LOG above - don't repeat past mistakes!
2. Common illegal move types:
   - Armies cannot support into pure sea territories
   - Support syntax must be: [Unit] S [Other Unit] -> [Destination]
   - Fleets cannot move to inland territories
   - Must specify coast for territories with multiple coasts

Please provide your orders for all your units. Be specific and clear about what each unit should do.

Your orders:"""
```

#### 6. Manual Illegal Moves Logging
After each adjudication, you manually add to `<Country>/illegal_moves.md`:

```bash
# Quick script: add_illegal_move.sh
#!/bin/bash
COUNTRY=$1
SEASON=$2
ORDER=$3
REASON=$4
LESSON=$5

echo "## $SEASON: $ORDER" >> "$COUNTRY/illegal_moves.md"
echo "**Result:** ILLEGAL - $REASON" >> "$COUNTRY/illegal_moves.md"
echo "**Lesson:** $LESSON" >> "$COUNTRY/illegal_moves.md"
echo "" >> "$COUNTRY/illegal_moves.md"
```

Usage:
```bash
./add_illegal_move.sh Austria "Fall 1901" "A Bul S BLA" \
  "Armies cannot support into sea territories" \
  "Armies can only support into land territories or coastal territories"
```

### Benefits of This Approach

1. **Experiential Learning**: LLMs learn from actual mistakes, not just rules
2. **Explicit Feedback Loop**: Illegal moves are highlighted, not buried
3. **Pattern Recognition**: Over time, LLMs build intuition about what's legal
4. **Debugging Aid**: You can see what the LLM misunderstands
5. **Emergent Behavior**: Watch how quickly they stop making the same mistakes

### Integration with Other Solutions

- **Tactics Primer (Solution 4)**: Teaches rules proactively
- **Illegal Moves Log**: Teaches rules reactively (from experience)
- **Together**: Cover both theoretical knowledge and practical learning

### Example: Full Learning Cycle

**Turn 1 - Make Mistake:**
```
Austria submits: A Bul S BLA
Result: Illegal move (armies can't support sea)
```

**You Update History:**
```markdown
## Fall 1901 Results
**A Bul S BLA: ILLEGAL MOVE** ❌
- Why: Armies cannot support into sea territories
- Effect: Unit held in Bulgaria
```

**You Log Mistake:**
```markdown
# illegal_moves.md
## Fall 1901: A Bul S BLA
**Result:** ILLEGAL - Armies cannot support into sea territories
**Lesson:** Use fleets to support naval operations
```

**Turn 2 - Context Includes:**
```
# YOUR ILLEGAL MOVES LOG
## Fall 1901: A Bul S BLA
**Result:** ILLEGAL - Armies cannot support into sea territories
**Lesson:** Use fleets to support naval operations
```

**Turn 2 - LLM Sees:**
- Game history showing the illegal move failed
- Illegal moves log explicitly calling it out
- Prompt reminding them to check the log

**Result:** Much less likely to repeat the mistake!

### Wild Idea: Automated Illegal Move Injection

For testing/training purposes, you could:
1. Deliberately inject common illegal move scenarios
2. See how quickly the LLM learns to avoid them
3. Measure learning rate across different models

This could be research data for "how do LLMs learn game rules from experience?"

---

## Solution 14: Move History Analysis (Complement to Illegal Moves)

### Concept
Track not just illegal moves, but also **poor tactical moves** that were legal but suboptimal.

### File: `<Country>/move_analysis.md`

```markdown
# Move Analysis - England

## Spring 1902: Missed Support Cut Opportunity
**What Happened:** F Nor -> Stp, F Bar S F Nor -> Stp
**What Could Have Been:** A Nor -> Stp(nc), F Bar S A Nor -> Stp(nc)
**Why Better:** Sweden can only reach Stp(sc), cannot cut support from Barents
**Lesson:** Consider coast mechanics when planning supports - some positions prevent cuts

## Fall 1902: Overextended Fleet
**What Happened:** F North Sea -> Norwegian Sea
**Result:** Left English Channel undefended, France moved in
**Lesson:** Don't overextend - maintain defensive positions in critical areas
```

### When to Add
- After each season, review orders and identify 1-2 suboptimal moves
- Not illegal, just tactically weak
- Helps build strategic intuition over time

### Integration
Include in context like illegal moves:
```python
move_analysis = self.load_move_analysis()
```

This creates a **continuous improvement loop** beyond just learning rules.

---

## Prioritized Implementation Roadmap

If you were to implement these in order:

### Phase 1: Low-Hanging Fruit (High Value, Low Complexity)
1. **Illegal Move Learning** (Solution 13) - Track and learn from mistakes
2. **Diplomacy Tactics Primer** (Solution 4) - Add static knowledge base
3. **Improved Turn Prompts** (Solution 7) - Better prompt engineering
4. **Strategic Review Command** (Solution 3) - Manual deep thinking tool

### Phase 2: Core Infrastructure (Medium Complexity, High Value)
5. **Hierarchical Memory System** (Solution 1) - strategy.md + tactical_analysis.md
6. **Move Analysis Tracking** (Solution 14) - Learn from suboptimal moves
7. **Conversation Summarization** (Solution 2) - Manage context window
8. **XML Tag Extensions** (Solution 6) - Support new memory types

### Phase 3: Advanced Features (Higher Complexity)
9. **Board Analysis Helper** (Solution 8) - Automated board state parsing
10. **Reflection Command** (Solution 5) - Ad-hoc strategic questions
11. **Multi-Model Architecture** (Solution 10) - Optimize cost/performance

### Phase 4: Research Projects (Long-term)
12. **Training Data Collection** (Solution 9) - Build dataset for fine-tuning
13. **Persistent Agent Memory** (Solution 11) - Non-stateless architecture
14. **Game Theory Integration** (Solution 12) - Formal strategic analysis

---

## Cost-Benefit Analysis

### Highest ROI
1. **Illegal Move Learning** (Solution 13) - Near-zero cost, immediate learning from mistakes
2. **Tactics Primer** (Solution 4) - Near-zero cost, teaches mechanics immediately
3. **Better Prompts** (Solution 7) - Zero cost, significant depth improvement
4. **Strategic Review** (Solution 3) - Uses expensive model but dramatically improves planning

### Biggest Impact on Tactical Depth
1. **Illegal Move Learning** (Solution 13) - Direct feedback on mistakes
2. **Move Analysis** (Solution 14) - Learn from suboptimal plays
3. **Hierarchical Memory** (Solution 1) - Separates strategy from tactics, enables long-term thinking
4. **Strategic Review** (Solution 3) - Dedicated deep-thinking time
5. **Tactics Primer** (Solution 4) - Teaches mechanical nuances

### Best for Context Window Management
1. **Conversation Summarization** (Solution 2) - Directly addresses bloat
2. **Hierarchical Memory** (Solution 1) - Structured, efficient context
3. **Board Analysis** (Solution 8) - Condensed board state instead of full history

### Best for Learning & Improvement Over Time
1. **Illegal Move Learning** (Solution 13) - Experiential learning from failures
2. **Move Analysis** (Solution 14) - Learn from tactical mistakes
3. **Training Data Collection** (Solution 9) - Build dataset for fine-tuning
4. **Persistent Agent Memory** (Solution 11) - Continuous learning across games

---

## Open Questions

1. **Model Selection**: Stick with Gemini family, or mix in Claude/GPT for strategic thinking?
2. **Update Frequency**: How often should strategy.md and tactical_analysis.md update?
3. **Automation vs. Manual**: Should strategic reviews be automatic or user-triggered?
4. **Backwards Compatibility**: Start fresh games for new features, or try to migrate existing games?
5. **Data Collection**: Worth collecting game data for future fine-tuning?

---

## Real Examples from Current Game

### Example 1: England's St. Petersburg Support Cutting Miss

The Norway support cutting issue is a perfect example of tactical depth problems:

**What Happened:**
- England used: `F Nor -> Stp, F Bar S F Nor -> Stp`
- Russia could cut: `F Swe -> Bar` (cuts support)

**What Should Happen:**
- England uses: `A Nor -> Stp(nc), F Bar S A Nor -> Stp(nc)`
- Russia CANNOT cut: `F Swe` can only reach `Stp(sc)`, not `Stp(nc)`, so can't attack Barents

**Why LLM Missed This:**
- Doesn't deeply understand coast mechanics
- Didn't analyze which units can cut which supports
- Focused on "get fleet to St. Petersburg" without tactical optimization

**How Solutions Would Fix:**
- **Tactics Primer** (Solution 4): Explicitly teach coast-based support cutting
- **Tactical Analysis** (Solution 1): Include "support cutting analysis" in board review
- **Better Prompts** (Solution 7): Ask "which units can cut your supports?"
- **Strategic Review** (Solution 3): Deep thinking mode would likely catch this
- **Move Analysis** (Solution 14): Log this as suboptimal, prevent future repeats

### Example 2: Bulgaria's Illegal Support to Black Sea

**What Happened:**
- Austria ordered: `A Bul S BLA` (trying to support Black Sea)
- Result: Illegal move - armies cannot support into pure sea territories

**Why This Is Valuable:**
- LLM learned (or should learn) a fundamental game rule through experience
- This mistake shouldn't be repeated with proper logging

**How Solutions Would Fix:**
- **Illegal Move Learning** (Solution 13): Explicitly log and learn from this
- **Tactics Primer** (Solution 4): Preemptively teach this rule
- **Better Prompts** (Solution 7): Remind about unit type restrictions
- **Game History Formatting**: Highlight illegal moves clearly

### Example 3: Ukraine's Incomplete Support Syntax

**What Happened:**
- Country ordered: `A Ukr S Gal` (incomplete - didn't specify what to support)
- Result: Illegal move - support syntax requires specifying unit and destination

**Why This Matters:**
- Syntax errors are different from strategic errors
- Easy to fix with proper examples and validation
- Should be rare after first occurrence

**How Solutions Would Fix:**
- **Illegal Move Learning** (Solution 13): Show correct syntax in log
- **Order Validation** (Solution 13): Warn about syntax issues (but still allow)
- **Tactics Primer** (Solution 4): Include syntax reference
- **Better Prompts** (Solution 7): Show order format examples

### Pattern Across All Examples

These three examples illustrate different types of learning needs:
1. **Subtle Tactical Depth** (St. Petersburg) - Requires strategic thinking
2. **Game Rule Learning** (Bulgaria) - Requires experiential feedback
3. **Syntax Understanding** (Ukraine) - Requires clear examples

The proposed solutions cover all three categories:
- **Solutions 1, 3, 7**: Address tactical depth
- **Solutions 4, 13**: Address rule learning
- **Solutions 4, 13**: Address syntax clarity

This is the type of multi-layered improvement that separates good from great Diplomacy play, and it's exactly what these improvements target.

# Diplomacy LLM

A research framework using Diplomacy as a testbed to study LLM agent behavior in multi-agent strategic environments. LLM sessions play against each other with human adjudication of moves.

## Quick Start

```bash
python diplomacy.py setup      # Install dependencies, create .env
python diplomacy.py init       # Initialize game files
python diplomacy.py season     # Run a full season
```

## How It Works

Each country is controlled by a separate LLM session. The LLMs:
- Send diplomatic messages to each other
- Maintain private strategy files
- Learn from past mistakes
- Submit orders when prompted

**You** manually:
- Adjudicate moves on a Diplomacy board
- Update `game_history.md` with results
- Advance the season in `config.yaml`

## Research

This project studies emergent LLM behaviors including strategic deception, spatial reasoning, and multi-agent coordination. See [`research/`](research/) for findings and experiments.

**Core finding**: LLMs reason well about strategy and deception but struggle with spatial/mechanical reasoning that would be obvious to a human looking at a map.

## Season Flow

Each season runs through three phases:

```
PLAN → TURN (x N rounds) → REFLECT
```

1. **PLAN**: Consider strategic options, plan messaging strategy
2. **TURN** (multiple rounds): Execute messaging plan, react to other countries
3. **REFLECT**: Organize files, submit orders

## Commands

| Command | Description |
|---------|-------------|
| `season` | Run a full season (all phases) |
| `plan [country]` | Consider strategic options, plan the season |
| `<country>` | Run a single turn for one country |
| `all` | Run turns for all countries |
| `reflect [country]` | Organize files, submit orders |
| `query <country> "question"` | Ask a country a direct question |
| `overseer` | Analyze conversations for loose ends |
| `status` | Show game state |
| `init` | Initialize new game |
| `cleanup` | Reset all game files |
| `setup` | Install dependencies |

## File Structure

```
diplomacy-llm/
├── config.yaml          # Game settings (season, models, features)
├── diplomacy.py         # CLI entry point
├── src/                 # Python modules
│   ├── agent.py         # LLM interaction
│   ├── orchestrator.py  # Phase execution
│   ├── mode_loader.py   # Prompt loading
│   └── context.py       # Context building
├── modes/               # Prompt templates
│   ├── base/            # Default prompts
│   ├── gunboat/         # No-messaging variant
│   └── fow/             # Fog of war variant
└── countries/           # Generated at runtime
    ├── France/
    │   ├── void.md              # Scratchpad
    │   ├── orders.md            # Current orders
    │   ├── strategy.md          # Strategy notes
    │   └── lessons_learned.md   # Accumulated lessons
    ├── Germany/
    └── ...
```

## Mode System

Prompts are loaded from `modes/` with overlay support:

- `modes/base/` - Default prompts (always loaded)
- `modes/gunboat/` - Overrides for no-messaging mode
- `modes/fow/` - Overrides for fog of war mode

Enable modes in `config.yaml`:
```yaml
features:
  gunboat: true   # No messaging between countries
  fog_of_war: true  # Countries only see nearby units
```

## Typical Workflow

```bash
# 1. Update config.yaml with new season
# 2. Update game_history.md with adjudication results

python diplomacy.py season    # Run full season

# 3. Review orders in each country's orders.md
# 4. Adjudicate on your board
# 5. Repeat!
```

## Key Files

| File | Purpose |
|------|---------|
| `config.yaml` | Game settings, current season, model selection |
| `countries/*/game_history.md` | Board state and move history (you update this) |
| `countries/*/void.md` | Country's scratchpad (cleared periodically) |
| `countries/*/lessons_learned.md` | Accumulated lessons from past mistakes |
| `countries/*/orders.md` | Current season's orders |

## Configuration

```yaml
# config.yaml
model: gemini-3-flash-preview      # Main model for reflect phase
cheap_model: gemini-3-flash-preview  # Fast model for debrief/turn

game:
  current_season: Spring 1901

season:
  turn_rounds: 3  # Messaging rounds per season

features:
  gunboat: false  # Set true for no-messaging mode
```

## For Developers

See [ARCHITECTURE.md](ARCHITECTURE.md) for:
- Module responsibilities
- How to add new phases
- Mode system internals
- Known technical debt

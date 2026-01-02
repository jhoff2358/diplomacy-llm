# Quick Start Guide

## Setup

1. **Get your Gemini API key:**
   Visit https://aistudio.google.com/app/apikey

2. **Run setup:**
   ```bash
   python diplomacy.py setup
   ```

3. **Add your API key to `.env`:**
   ```bash
   nano .env
   # Replace 'your_api_key_here' with your actual key
   ```

4. **Initialize the game:**
   ```bash
   python diplomacy.py init
   ```

## Your First Season

### Run a complete season:

```bash
python diplomacy.py season
```

This runs all three phases automatically:

1. **PLAN** - Each country considers strategic options and plans messaging
2. **TURN** (multiple rounds) - Countries exchange messages, react to others
3. **REFLECT** - Countries organize notes and submit orders

### After the season completes:

1. Review orders in `countries/*/orders.md`
2. Adjudicate moves on your board (physical or online)
3. Update `countries/*/game_history.md` with results
4. Update `config.yaml` with the new season
5. Run the next season!

## Manual Control

Instead of `season`, run phases individually:

```bash
# Plan phase (all countries)
python diplomacy.py plan

# Individual turns
python diplomacy.py france
python diplomacy.py germany

# All turns in order
python diplomacy.py all

# Reflect phase (all countries)
python diplomacy.py reflect
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `season` | Run full season (plan + turns + reflect) |
| `plan [country]` | Consider strategic options, plan the season |
| `<country>` | Run a single turn |
| `all` | Run turns for all countries |
| `reflect [country]` | Organize notes, submit orders |
| `status` | Show game state |
| `init` | Initialize new game |
| `cleanup` | Reset all game files |

## Troubleshooting

**"GEMINI_API_KEY not found"**
- Check that `.env` exists and has your key
- Format: `GEMINI_API_KEY=your_actual_key` (no quotes)

**Country seems confused about game state**
- Make sure `game_history.md` is up to date with adjudication results

**Want to start fresh**
- Run `python diplomacy.py cleanup` then `python diplomacy.py init`

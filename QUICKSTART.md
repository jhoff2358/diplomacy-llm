# Quick Start Guide

## First Time Setup

1. **Get your Gemini API key:**
   ```bash
   # Visit: https://aistudio.google.com/app/apikey
   # Copy your API key
   ```

2. **Run setup:**
   ```bash
   ./setup.sh
   ```

3. **Add your API key to `.env`:**
   ```bash
   # Edit .env and replace 'your_api_key_here' with your actual key
   nano .env
   ```

4. **Initialize game history:**
   ```bash
   python initialize_game.py
   ```

   This creates a shared `game_history.md` file with standard Diplomacy starting positions.

## Starting Your First Game

### Step 1: Verify initial game state

The `game_history.md` file (shared by all countries) should now contain all starting positions:

```markdown
## Spring 1901

### Current Board State

**Austria** (3 centers, 3 units)
- Supply Centers: Budapest, Trieste, Vienna
- Units: A Budapest, A Vienna, F Trieste

**England** (3 centers, 3 units)
- Supply Centers: Edinburgh, Liverpool, London
- Units: F Edinburgh, F London, A Liverpool

(etc for all countries...)
```

### Step 2: Run some turns

```bash
# Have France think about the situation
python diplomacy.py france

# France might want to message Germany
# When prompted, choose option 1 (send message)
# Enter: Germany
# Season: Spring 1901
# Message: Hello neighbor! Interested in working together?

# Now run Germany's turn
python diplomacy.py germany

# Germany will see France's message in their context!
```

### Step 3: Collect orders

```bash
# When you're ready for orders
python diplomacy.py orders

# This creates orders.md with everyone's moves
```

### Step 4: Adjudicate manually

- Execute the orders on your board (physical or online)
- Note what happened (successes, bounces, conflicts)

### Step 5: Update game state

Edit the shared `game_history.md` file with:
- What orders were given
- What happened (moves that worked, bounces, etc.)
- Updated unit positions for all countries
- Updated supply center ownership

### Step 6: Repeat!

Continue the cycle: negotiations → orders → adjudicate → update state → negotiations...

## Example Turn Workflow

```bash
# Morning coffee: Run a few countries
python diplomacy.py france
python diplomacy.py england
python diplomacy.py germany

# Check who's talking to who
python diplomacy.py status

# Lunchtime: Run a few more
python diplomacy.py austria
python diplomacy.py italy

# Evening: Collect orders
python diplomacy.py orders

# Adjudicate moves on your board
# Update game_history.md file

# Next day: New season begins!
```

## Tips

- **Pacing:** You control the flow - run as many or few turns as you want
- **Messages:** Messages automatically appear in both countries' contexts
- **Seasons:** Use season headers like "Spring 1901", "Fall 1901", "Spring 1902"
- **Plans/Notes:** Countries can use these for private strategy thoughts
- **Option 5:** If you want to probe deeper into a country's thinking, use option 5 to continue chatting

## Commands Quick Reference

| Command | Description |
|---------|-------------|
| `python diplomacy.py france` | Run a turn for France |
| `python diplomacy.py orders` | Collect orders from all countries |
| `python diplomacy.py status` | Show game overview |

## Troubleshooting

**"GEMINI_API_KEY not found"**
- Check that `.env` exists and has your key
- Make sure it's `GEMINI_API_KEY=your_actual_key` (no quotes needed)

**Country seems confused about game state**
- Check that `game_history.md` is up to date
- Make sure you updated it after last turn

**Want to reset a country's plans/notes**
- Just delete or edit the file: `rm France/plans.md`

Have fun! Watch the alliances form and the inevitable betrayals unfold!

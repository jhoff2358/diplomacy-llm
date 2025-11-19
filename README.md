# Diplomacy LLM

A multi-agent framework where 7 LLM sessions play Diplomacy against each other, with human adjudication of moves.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get a Gemini API key:**
   - Go to https://aistudio.google.com/app/apikey
   - Create an API key
   - Copy `.env.example` to `.env` and add your key

3. **Initialize the game:**
   ```bash
   python initialize_game.py
   ```

4. **Start playing!** (see gameplay workflow below)

## How It Works

Each of the 7 Diplomacy countries is controlled by a separate Gemini LLM session. The LLMs:
- Send diplomatic messages to each other
- Update their own strategic plans and notes
- Submit orders when asked

**You** manually:
- Orchestrate the turn order
- Adjudicate moves on a real Diplomacy board
- Update the game state files as the game progresses

### What the LLMs See

**Shared (all countries see):**
- `game_history.md` - Current board state and move history
- `conversations/` - Diplomatic conversations they're part of

**Private (only that country sees):**
- `plans.md` - Their strategic plans
- `notes.md` - Their notes

### How LLMs Communicate

The LLMs use XML tags to take actions:
```xml
<MESSAGE to="Austria">
Your diplomatic message here
</MESSAGE>

<MESSAGE to="Austria,Germany">
Group message (comma-separated)
</MESSAGE>

<PLANS>
Full replacement of strategic plans
</PLANS>

<NOTES>
Full replacement of notes
</NOTES>
```

## Typical Season Workflow

### 1. Start of Season

Update the current season in `config.yaml`:
```yaml
game:
  current_season: Spring 1902  # Update this!
```

Activate your venv (only need to do once per terminal session):
```bash
source venv/bin/activate
```

Randomize the turn order (do this once per season):
```bash
./randomize_order.sh
```

### 2. Diplomacy Phase (Multiple Rounds)

Run all countries in the saved turn order:
```bash
./run_all_turns.sh
```

This runs all 7 countries sequentially in the randomized order. The LLMs will send messages to each other, update their plans, etc.

**Run this multiple times** to let the LLMs have several rounds of back-and-forth diplomacy.

#### Check Readiness (Optional)

Before collecting orders, you can check if countries want more discussion:
```bash
python3 diplomacy.py readiness
```

This uses a cheap model (gemini-flash-latest) to ask each country if they're ready for orders or need more negotiation.

If they need more discussion, run `./run_all_turns.sh` again.

### 3. Collect Orders

When diplomacy is done, collect orders from all countries:
```bash
python3 diplomacy.py orders
```

This creates `orders.md` with all 7 countries' orders.

### 4. Adjudicate & Update

1. Execute the orders on your Diplomacy board (physical or online)
2. Update `game_history.md` with:
   - What moves happened
   - Any bounces or conflicts
   - Current board state (unit positions, supply centers)
3. Update `config.yaml` with the new season
4. Go back to step 1!

## Commands

### Run All Countries (Sequential)
```bash
./run_all_turns.sh
```
Runs all 7 countries in the saved turn order. Run multiple times per season for multiple diplomacy rounds.

### Randomize Turn Order
```bash
./randomize_order.sh
```
Randomizes and saves the turn order. Do this **once per season** at the start. The same order persists across multiple `run_all_turns.sh` calls.

### Run Single Country
```bash
python3 diplomacy.py <country>
```
Run one country's turn (e.g., `python3 diplomacy.py france`). Requires venv activated.

### Check Readiness
```bash
python3 diplomacy.py readiness
```
Ask all countries if they're ready for orders or need more discussion. Uses cheap model to save costs. Requires venv activated.

### Collect Orders
```bash
python3 diplomacy.py orders
```
Collect orders from all countries and save to `orders.md`. Requires venv activated.

### Check Status
```bash
python3 diplomacy.py status
```
Show game status: active conversations, which countries have plans/notes. Requires venv activated.

### Reset Game
```bash
./reset_game.sh
```
Clear all conversations, plans, and notes. Keeps `config.yaml` and `game_history.md`.

## Example Season Flow

```bash
# Start of Spring 1902
# 1. Update config.yaml: current_season: "Spring 1902"
# 2. Update game_history.md with Winter 1901 build results

source venv/bin/activate          # Activate venv once

./randomize_order.sh              # Set turn order for this season

./run_all_turns.sh                # Round 1 of diplomacy
./run_all_turns.sh                # Round 2 of diplomacy
./run_all_turns.sh                # Round 3 of diplomacy

python3 diplomacy.py readiness    # Check if ready for orders

./run_all_turns.sh                # More diplomacy if needed

python3 diplomacy.py orders       # Collect orders

# Adjudicate moves on your board
# Update game_history.md with results
# Repeat for Fall 1902!
```

## File Structure

```
diplomacy-llm/
├── config.yaml              # Game config (current_season goes here!)
├── game_history.md          # Shared board state (you update this)
├── conversations/           # Shared diplomatic messages
│   ├── Austria-Turkey.md
│   ├── England-France.md
│   └── ...
├── turn_order.txt           # Saved turn order (generated by randomize_order.sh)
├── orders.md                # Generated by orders command
├── Austria/                 # Private plans.md and notes.md
├── England/
├── France/
├── Germany/
├── Italy/
├── Russia/
├── Turkey/
├── .env                     # Your API key
└── (code files...)
```

## Tips

- **Randomize once per season** - The turn order persists across multiple rounds
- **Run multiple diplomacy rounds** - Let the LLMs negotiate back-and-forth
- **Update game_history.md after each phase** - LLMs need accurate board state
- **Use readiness check** - Saves money by using cheap model to gauge readiness
- **Watch for emergent behavior** - LLMs naturally form alliances, lie, and backstab!

## Model Configuration

Set in `config.yaml`:
```yaml
model: gemini-3-pro-preview  # Default model for turns
```

The `readiness` command automatically uses `gemini-flash-latest` to save costs.

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Create `.env` with your API key
- **"turn_order.txt not found"**: Run `./randomize_order.sh` first
- **Rate limits**: Wait a moment and try again
- **ModuleNotFoundError**: Make sure you activated the venv with `source venv/bin/activate`

## Have Fun!

Watch the AIs negotiate, scheme, and (inevitably) betray each other. This is emergent multi-agent gameplay at its finest! 🎭

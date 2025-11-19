# Diplomacy LLM

A multi-agent framework where 7 LLM sessions play Diplomacy against each other, with human adjudication of moves.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get a Gemini API key:**
   - Go to https://aistudio.google.com/app/apikey
   - Create an API key

3. **Configure the API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## How It Works

The game has:
- **`gamestate.json`** - Current season, phase, turn number (you manually update this)
- **Shared `game_history.md`** - The current board state and move history (visible to all countries)
- **Shared `conversations/`** - All diplomatic conversations (bilateral and group chats)
- **7 country folders** - One for each Diplomacy country (Austria, England, France, Germany, Italy, Russia, Turkey)

Each country folder contains:
- `plans.md` - Strategic plans (private to that country)
- `notes.md` - Additional notes (private to that country)

Countries can see conversations they're part of and update their plans/notes using XML tags in their responses.

You manually orchestrate the game by running turns for each country, updating `gamestate.json` as the game progresses, and manually adjudicating moves on a real Diplomacy board.

## Usage

### Run a Country's Turn

```bash
python diplomacy.py france
```

This will:
1. Load all context for France (game state, conversations, plans, notes)
2. Ask the LLM what it wants to do
3. LLM responds using XML tags to send messages and update files
4. Actions are automatically executed

The LLM uses these tags:
- `<MESSAGE to="Austria">...</MESSAGE>` - Send a message
- `<MESSAGE to="Austria,Germany">...</MESSAGE>` - Group message
- `<PLANS>...</PLANS>` - Update plans (full replacement)
- `<NOTES>...</NOTES>` - Update notes (full replacement)

### Collect Orders from All Countries

```bash
python diplomacy.py orders
```

This asks all 7 countries for their orders and saves them to `orders.md`.

### Check Game Status

```bash
python diplomacy.py status
```

Shows overview of all countries' conversations and files.

## Typical Game Flow

1. **Start of a new season:**
   - Update `game_history.md` with the current board state
   - Include what happened last turn (moves, bounces, retreats, etc.)

2. **Negotiation phase:**
   ```bash
   python diplomacy.py france
   python diplomacy.py germany
   python diplomacy.py england
   # ... run turns for countries as you see fit
   ```

   Countries can send messages to each other during their turns.

3. **Orders phase:**
   ```bash
   python diplomacy.py orders
   ```

   All countries submit their orders.

4. **Manual adjudication:**
   - Execute the orders on your physical/online Diplomacy board
   - Update `game_history.md` with results
   - Repeat!

## Tips

- You control the pacing - run as many or as few turns as you want before collecting orders
- Conversations are stored in shared `conversations/` folder with participants in alphabetical order
- Each conversation file is organized by season with headers like `## Spring 1901`
- The LLMs will naturally develop strategies - you can let personalities emerge organically
- Group chats are supported (e.g., `Austria-England-France.md`)
- Check `orders.md` after running the orders command to see what everyone wants to do

## File Structure

```
diplomacy-llm/
├── game_history.md          # Shared game state (all countries see this)
├── conversations/           # Shared conversations
│   ├── Austria-France.md
│   ├── England-Germany.md
│   ├── Austria-Germany-Italy.md  # Group chat example
│   └── ...
├── Austria/
│   ├── plans.md
│   └── notes.md
├── England/
│   └── ...
├── (other countries...)
├── config.yaml
├── .env
├── context.py
├── agent.py
├── diplomacy.py
└── README.md
```

## Model Configuration

The framework uses Gemini 2.0 Flash Experimental by default (set in `config.yaml`). You can change this to other Gemini models if needed.

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Make sure you've created `.env` file with your API key
- **Rate limits**: If you hit rate limits, just wait a moment and try again
- **Empty responses**: Sometimes the LLM might be brief - you can use option 5 to continue the conversation

## Have Fun!

This is a research project exploring multi-agent LLM interactions. Enjoy watching the AIs negotiate, form alliances, and (inevitably) betray each other!

# Architecture Guide

A guide for contributors and future Claude sessions working on this codebase.

## Project Goals

1. **Research testbed** - Study how LLMs reason about strategy, deception, and spatial problems
2. **LLMs that learn from experience** - Agents accumulate lessons in `lessons_learned.md` and avoid repeating mistakes
3. **Purposeful messaging** - Agents plan before they talk (plan phase), not just react
4. **Flexible prompt system** - Easy to iterate on prompts without touching Python code
5. **Mode variants** - Support gunboat (no messaging), fog of war, and other rule variants

## Season Flow

Each season runs through three phases:

```
PLAN → TURN (x N rounds) → REFLECT
```

### 1. PLAN (start of season)
- **Model:** cheap_model
- **Purpose:** Consider strategic options, plan messaging strategy
- **File access:** lessons_learned.md, void.md only (append-only)
- **Output:** Strategic plan in void.md

### 2. TURN (multiple rounds)
- **Model:** cheap_model
- **Purpose:** Execute messaging plan, react to other countries
- **File access:** void.md only
- **Output:** Messages sent, notes accumulated in void.md

### 3. REFLECT (end of season)
- **Model:** main model (more capable)
- **Purpose:** Organize notes, submit final orders
- **File access:** All files
- **Output:** Organized strategy files, orders.md with final moves

## Key Modules

### src/agent.py
LLM interaction and response parsing. Contains:
- `DiplomacyAgent` class - manages chat sessions
- `initialize_*_session()` - set up prompts for each phase
- `take_*_turn()` - execute a phase and parse response
- `parse_response()` - extract FILE, MESSAGE, NOTE tags from LLM output
- `execute_actions()` - apply parsed actions to filesystem

### src/orchestrator.py
Phase execution and season coordination:
- `run_country_*()` - run a phase for one country
- `run_all_*()` - run a phase for all countries
- `run_season()` - execute complete season flow
- `run_classic_season()` / `run_gunboat_season()` - mode-specific flows

### src/mode_loader.py
Prompt loading with overlay support:
- Loads prompts from `modes/base/` first
- Overlays mode-specific prompts (e.g., `modes/gunboat/`)
- Supports `{variable}` substitution and `{block:name}` references
- Handles `.md.disable` files to suppress prompts

### src/context.py
Context building for prompts:
- `ContextLoader` class - assembles context for a country
- Reads game_history.md, messages, country files
- Applies fog of war filtering if enabled

### src/utils.py
Shared utilities:
- Config loading
- Country name resolution
- Path helpers

### src/game_manager.py
Game lifecycle:
- `initialize_game()` - create country folders and files
- `cleanup()` - remove all game files
- `show_status()` - display game state

## Mode System

Prompts are loaded with overlay behavior:

```
modes/
├── base/           # Always loaded first
│   ├── turn.md
│   ├── reflect.md
│   ├── plan.md
│   └── ...
├── gunboat/        # Loaded if features.gunboat = true
│   ├── reflect.md  # Overrides base/reflect.md
│   └── ...
└── fow/            # Loaded if features.fog_of_war = true
    ├── rules.md    # Concatenates with base/rules.md
    └── ...
```

### Prompt Types

**Override prompts** (last mode wins):
- turn.md, reflect.md, plan.md, context_header.md

**Concatenated prompts** (all modes combined):
- rules.md, file_management.md, order_format.md

### Template Syntax

```markdown
# Variables
You are playing as {country}.
Current season: {season}

# Block references (loads and inserts another prompt)
{block:rules}
{block:order_format}

# Conditionals
{if:wipe_void}
Your void.md will be cleared.
{endif}
```

### Disabling Prompts

Create a `.md.disable` file to suppress a prompt in a mode:
```
modes/gunboat/messaging_instructions.md.disable
```

## Adding a New Phase

1. **Create the prompt:** `modes/base/{phase}.md`

2. **Add agent methods in src/agent.py:**
   ```python
   def initialize_{phase}_session(self):
       context = self.context_loader.format_context()
       mode_loader = ModeLoader(self.config)
       self.chat = self.model.start_chat(history=[])
       return mode_loader.get_prompt("{phase}", {
           "context": context,
           "country": self.country
       })

   def take_{phase}_turn(self):
       prompt = self.initialize_{phase}_session()
       response = self.chat.send_message(prompt)
       actions = self.parse_response(response.text)
       return response.text, actions
   ```

3. **Add orchestrator function in src/orchestrator.py:**
   ```python
   def run_country_{phase}(country: str):
       agent = DiplomacyAgent(country, use_cheap_model=True)
       response_text, actions = agent.take_{phase}_turn()
       agent.execute_actions(actions, season, restrict_files=[...])
   ```

4. **Wire into CLI in diplomacy.py**

---

## Future Improvements

These are identified improvements not yet implemented.

### ~~Move Hardcoded Filenames to Config~~ ✓ DONE

Filenames are now configurable in `config.yaml` under `paths:`:
```yaml
paths:
  scratchpad: void.md
  orders: orders.md
  lessons: lessons_learned.md
```

Prompt templates use `{scratchpad_file}`, `{orders_file}`, `{lessons_file}` variables.

### Phase Configuration in Config

**Problem:** Adding a phase requires editing 3+ Python files.

**Solution:**
```yaml
phases:
  plan:
    prompt: plan
    model: cheap_model
    allow_messages: false
    restrict_files: [lessons_learned.md, void.md]
    append_only: [lessons_learned.md, void.md]
  turn:
    prompt: turn
    model: cheap_model
    allow_messages: true
    restrict_files: [void.md]
  reflect:
    prompt: reflect
    model: model
    allow_messages: false
    restrict_files: null  # all allowed
```

**Benefit:** Add/modify phases via config only.

### Split orchestrator.py

**Problem:** 400+ lines, handles too much.

**Solution:** Split into:
- `orchestrator.py` - phase workflow coordination
- `season.py` - season execution logic
- `turn_order.py` - turn order management

### Extract overseer()

**Problem:** Business logic lives in CLI dispatcher (diplomacy.py).

**Solution:** Move to `src/overseer.py`.

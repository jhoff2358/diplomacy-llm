#!/usr/bin/env python3
"""
Initialize Diplomacy game.
In FoW mode, creates per-country game_state.md and game_history.md.
In classic mode, creates shared game_state.md and game_history.md in root,
which get copied to country folders on each turn.
"""

from pathlib import Path
from utils import load_config, is_fow, is_gunboat, get_all_countries


def create_game_history_template(country: str) -> str:
    """Create empty game history template for a country (FoW mode)."""
    return f"""# Game History - {country}

This file tracks the orders and results you have witnessed.
Updated manually by the game master with fog-of-war filtered information.

## Spring 1901

*No orders yet - the game is just beginning!*
"""


def create_shared_game_history_template() -> str:
    """Create shared game history template (classic mode)."""
    return """# Game History

This file tracks the orders and results of the game.
Updated manually by the game master.

## Spring 1901

*No orders yet - the game is just beginning!*
"""


def create_game_state_template(country: str) -> str:
    """Create empty game state template for a country (FoW mode)."""
    return f"""Spring 1901

# Current Game State - {country}

## Permanent Home SC Visibility
## Supply Centers you control marked with an asterisk. Assume provinces do not contain units unless explicitly specified

## Additional visibility from units:
None yet

## Countries You Border (Can Message)
*To be filled in by game master*
"""


def create_shared_game_state_template() -> str:
    """Create shared game state template (classic mode)."""
    return """Spring 1901

# Current Game State

## Supply Centers
*To be filled in by game master*

## Units
*To be filled in by game master*
"""


def main():
    config = load_config()
    fow_enabled = is_fow(config)
    gunboat_enabled = is_gunboat(config)
    countries = get_all_countries(config)

    if gunboat_enabled:
        mode_name = "Gunboat"
    elif fow_enabled:
        mode_name = "Fog of War"
    else:
        mode_name = "Classic"

    print(f"Initializing {mode_name} Diplomacy game...\n")

    data_dir = Path(config['paths']['data_dir'])

    # Create conversations directory (not needed for gunboat)
    if not gunboat_enabled:
        conversations_dir = data_dir / config['paths']['shared_conversations_dir']
        conversations_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {conversations_dir}/")

    # Create per-country directories
    for country in countries:
        country_dir = data_dir / country
        country_dir.mkdir(parents=True, exist_ok=True)

        if fow_enabled:
            # FoW mode: create per-country game_state.md and game_history.md
            game_state_file = country_dir / config['paths']['game_state']
            game_state_file.write_text(create_game_state_template(country))
            game_history_file = country_dir / config['paths']['game_history']
            game_history_file.write_text(create_game_history_template(country))
            print(f"✓ Created {country}/ with game_history.md and game_state.md")
        else:
            print(f"✓ Created {country}/")

    if not fow_enabled:
        # Classic/Gunboat mode: copy beginning_info.md to game_state.md, create game_history.md
        beginning_info = Path('beginning_info.md')
        shared_game_state = data_dir / 'game_state.md'
        if beginning_info.exists():
            shared_game_state.write_text(beginning_info.read_text())
            print(f"✓ Copied beginning_info.md to game_state.md")
        else:
            shared_game_state.write_text(create_shared_game_state_template())
            print(f"✓ Created game_state.md (beginning_info.md not found)")
        shared_game_history = data_dir / 'game_history.md'
        shared_game_history.write_text(create_shared_game_history_template())
        print(f"✓ Created game_history.md")

    print("\n✓ Game initialized!")
    print(f"\nMode: {mode_name}")
    print("\nNext steps:")
    if fow_enabled:
        print("  1. Fill in each country's game_state.md with their starting visibility")
        print("  2. Make sure your .env file has your Gemini API key")
        print("  3. Run: python diplomacy.py status")
        print("  4. Start the game: python diplomacy.py run_season")
    else:
        print("  1. Make sure your .env file has your Gemini API key")
        print("  2. Run: python diplomacy.py status")
        print("  3. Start the game: python diplomacy.py run_season")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Initialize Diplomacy game.
Creates per-country directories with game_history.md templates.
In FoW mode, also creates per-country game_state.md.
In classic mode, creates a single shared game_state.md in root.
"""

from pathlib import Path
from utils import load_config, is_fow, get_all_countries


def create_game_history_template(country: str, fow_enabled: bool) -> str:
    """Create empty game history template for a country."""
    if fow_enabled:
        description = "This file tracks the orders and results you have witnessed.\nUpdated manually by the game master with fog-of-war filtered information."
    else:
        description = "This file tracks the orders and results of the game.\nUpdated manually by the game master."

    return f"""# Game History - {country}

{description}

## Spring 1901

*No orders yet - the game is just beginning!*
"""


def create_game_state_template(country: str) -> str:
    """Create empty game state template for a country (FoW mode)."""
    return f"""# Current Game State - {country}

Season: Spring 1901

## Permanent Home SC Visibility
## Supply Centers you control marked with an asterisk. Assume provinces do not contain units unless explicitly specified

## Additional visibility from units:
None yet

## Countries You Border (Can Message)
*To be filled in by game master*
"""


def create_shared_game_state_template() -> str:
    """Create shared game state template (classic mode)."""
    return """# Current Game State

Season: Spring 1901

## Supply Centers
*To be filled in by game master*

## Units
*To be filled in by game master*
"""


def main():
    config = load_config()
    fow_enabled = is_fow(config)
    countries = get_all_countries(config)
    mode_name = "Fog of War" if fow_enabled else "Classic"

    print(f"Initializing {mode_name} Diplomacy game...\n")

    data_dir = Path(config['paths']['data_dir'])
    conversations_dir = data_dir / config['paths']['shared_conversations_dir']

    # Create conversations directory
    conversations_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {conversations_dir}/")

    # Create per-country directories and files
    for country in countries:
        country_dir = data_dir / country
        country_dir.mkdir(parents=True, exist_ok=True)

        # Create game_history.md (both modes)
        game_history_file = country_dir / config['paths']['game_history']
        game_history_file.write_text(create_game_history_template(country, fow_enabled))

        if fow_enabled:
            # FoW mode: create per-country game_state.md
            game_state_file = country_dir / config['paths']['game_state']
            game_state_file.write_text(create_game_state_template(country))
            print(f"✓ Created {country}/ with game_history.md and game_state.md")
        else:
            print(f"✓ Created {country}/ with game_history.md")

    if not fow_enabled:
        # Classic mode: create single shared game_state.md in root
        shared_game_state = data_dir / 'game_state.md'
        shared_game_state.write_text(create_shared_game_state_template())
        print(f"✓ Created shared game_state.md")

    print("\n✓ Game initialized!")
    print(f"\nMode: {mode_name}")
    print("\nNext steps:")
    if fow_enabled:
        print("  1. Fill in each country's game_state.md with their starting visibility")
    else:
        print("  1. Fill in the shared game_state.md with the starting game state")
    print("  2. Make sure your .env file has your Gemini API key")
    print("  3. Run: python diplomacy.py status")
    print("  4. Start the game: python diplomacy.py austria")


if __name__ == "__main__":
    main()

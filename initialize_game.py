#!/usr/bin/env python3
"""
Initialize Fog of War Diplomacy game.
Creates per-country directories with game_history.md and game_state.md templates.
"""

from pathlib import Path
import yaml

COUNTRIES = [
    "Austria",
    "England",
    "France",
    "Germany",
    "Italy",
    "Russia",
    "Turkey"
]


def create_game_history_template(country: str) -> str:
    """Create empty game history template for a country."""
    return f"""# Game History - {country}

This file tracks the orders and results you have witnessed.
Updated manually by the game master with fog-of-war filtered information.

## Spring 1901

*No orders yet - the game is just beginning!*
"""


def create_game_state_template(country: str) -> str:
    """Create empty game state template for a country."""
    return f"""# Current Game State - {country}

Season: Spring 1901

## Your Units
*To be filled in by game master*

## Visible Territories
*To be filled in by game master*

## Visible Enemy Units
*To be filled in by game master*

## Countries You Border (Can Message)
*To be filled in by game master*
"""


def main():
    print("Initializing Fog of War Diplomacy game...\n")

    # Load config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    data_dir = Path(config['paths']['data_dir'])
    conversations_dir = data_dir / config['paths']['shared_conversations_dir']

    # Create conversations directory
    conversations_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created {conversations_dir}/")

    # Create all bilateral conversation files
    for i, country1 in enumerate(COUNTRIES):
        for country2 in COUNTRIES[i+1:]:
            conv_file = conversations_dir / f"{country1}-{country2}.md"
            if not conv_file.exists():
                conv_file.write_text(f"# Conversation: {country1} - {country2}\n\n")
    print(f"✓ Created {len(COUNTRIES) * (len(COUNTRIES) - 1) // 2} conversation files")

    # Create per-country directories and files
    for country in COUNTRIES:
        country_dir = data_dir / country
        country_dir.mkdir(parents=True, exist_ok=True)

        # Create game_history.md
        game_history_file = country_dir / config['paths']['game_history']
        game_history_file.write_text(create_game_history_template(country))

        # Create game_state.md
        game_state_file = country_dir / config['paths']['game_state']
        game_state_file.write_text(create_game_state_template(country))

        print(f"✓ Created {country}/ with game_history.md and game_state.md")

    print("\n✓ Game initialized!")
    print("\nNext steps:")
    print("  1. Fill in each country's game_state.md with their starting visibility")
    print("  2. Make sure your .env file has your Gemini API key")
    print("  3. Run: python diplomacy.py status")
    print("  4. Start the game: python diplomacy.py austria")


if __name__ == "__main__":
    main()

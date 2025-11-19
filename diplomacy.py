#!/usr/bin/env python3
"""
Diplomacy LLM CLI
Main interface for running the multi-agent Diplomacy game.

Usage:
    python diplomacy.py <country>     # Run a turn for a specific country
    python diplomacy.py orders        # Collect orders from all countries
    python diplomacy.py status        # Show current game status
"""

import sys
import json
from pathlib import Path
from agent import DiplomacyAgent, get_all_countries


def load_gamestate():
    """Load current game state from gamestate.json."""
    gamestate_file = Path("gamestate.json")
    if gamestate_file.exists():
        with open(gamestate_file, 'r') as f:
            return json.load(f)
    return {"season": "Unknown"}


def run_country_turn(country: str):
    """Run a single turn for a country."""
    try:
        agent = DiplomacyAgent(country)

        # Load current season from gamestate.json
        gamestate = load_gamestate()
        season = gamestate.get('season', 'Unknown')

        print(f"\nCurrent Season: {season}")

        print(f"\n{'='*60}")
        print(f"{country}'s Turn")
        print(f"{'='*60}\n")

        # Take turn and get response
        response_text, actions = agent.take_turn(season)

        # Show LLM's response
        print(f"{country} says:")
        print("-" * 60)
        print(response_text)
        print("-" * 60)

        # Execute actions if any were parsed
        has_actions = (actions['messages'] or
                      actions['plans'] is not None or
                      actions['notes'] is not None)

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season)
            print(f"\n✓ Turn complete")
        else:
            print(f"\nNo actions taken this turn.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def collect_orders():
    """Collect orders from all countries."""
    print("\n" + "="*60)
    print("COLLECTING ORDERS FROM ALL COUNTRIES")
    print("="*60 + "\n")

    # Load current season from gamestate.json
    gamestate = load_gamestate()
    season = f"{gamestate.get('season', 'Unknown')} - Orders"

    print(f"Season: {season}\n")

    orders_file = Path("orders.md")
    with open(orders_file, 'w') as f:
        f.write(f"# Orders for {season}\n\n")

        for country in get_all_countries():
            print(f"\nGetting orders from {country}...")
            try:
                agent = DiplomacyAgent(country)
                orders = agent.get_orders()

                f.write(f"## {country}\n\n")
                f.write(orders)
                f.write("\n\n---\n\n")

                print(f"✓ {country}'s orders received")

            except Exception as e:
                print(f"✗ Error getting orders from {country}: {e}")
                f.write(f"## {country}\n\nERROR: {e}\n\n---\n\n")

    print(f"\n✓ All orders saved to {orders_file}")


def show_status():
    """Show current game status."""
    print("\n" + "="*60)
    print("GAME STATUS")
    print("="*60 + "\n")

    # Show current game state
    gamestate = load_gamestate()
    print(f"Current Season: {gamestate.get('season', 'Unknown')}")
    if gamestate.get('notes'):
        print(f"Notes: {gamestate.get('notes')}")
    print()

    # Check conversations directory
    conv_dir = Path("conversations")
    if conv_dir.exists():
        conv_files = list(conv_dir.glob("*.md"))
        print(f"Active Conversations: {len(conv_files)}")
        for conv_file in conv_files:
            # Count messages
            content = conv_file.read_text()
            msg_count = content.count('**')  // 2  # Rough estimate
            print(f"  - {conv_file.stem}: ~{msg_count} messages")
    else:
        print("Active Conversations: 0")

    print()

    for country in get_all_countries():
        country_dir = Path(country)
        print(f"{country}:")

        # Check plans
        plans_file = country_dir / "plans.md"
        if plans_file.exists() and plans_file.stat().st_size > 0:
            print(f"  ✓ Has plans")
        else:
            print(f"  - No plans yet")

        # Check notes
        notes_file = country_dir / "notes.md"
        if notes_file.exists() and notes_file.stat().st_size > 0:
            print(f"  ✓ Has notes")
        else:
            print(f"  - No notes yet")

        print()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python diplomacy.py <country>    # Run a turn for a country")
        print("  python diplomacy.py orders       # Collect orders from all countries")
        print("  python diplomacy.py status       # Show game status")
        print(f"\nCountries: {', '.join(get_all_countries())}")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Special commands
    if command == "orders":
        collect_orders()
    elif command == "status":
        show_status()
    else:
        # Assume it's a country name
        countries = get_all_countries()
        # Find country (case-insensitive)
        country = None
        for c in countries:
            if c.lower() == command:
                country = c
                break

        if country is None:
            print(f"Error: '{command}' is not a recognized command or country")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)

        run_country_turn(country)


if __name__ == "__main__":
    main()

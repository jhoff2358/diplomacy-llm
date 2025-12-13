#!/usr/bin/env python3
"""
Diplomacy LLM CLI
Main interface for running the multi-agent Diplomacy game.
Supports both classic and fog of war modes.

Usage:
    python diplomacy.py <country>         # Run a turn for a specific country
    python diplomacy.py reflect <country> # Strategic reflection session
    python diplomacy.py season            # Run a full season (turns + readiness + orders)
    python diplomacy.py readiness         # Check if countries are ready to submit orders
    python diplomacy.py overseer          # Check for loose ends in all conversations
    python diplomacy.py orders            # Collect orders from all countries
    python diplomacy.py status            # Show current game status
"""

import sys
import random
from pathlib import Path
from agent import DiplomacyAgent
import google.generativeai as genai
from dotenv import load_dotenv
import os

from utils import (
    load_config,
    is_fow,
    get_current_season,
    get_all_countries,
    find_country,
    print_section_header,
)


def run_country_turn(country: str):
    """Run a single turn for a country."""
    try:
        agent = DiplomacyAgent(country)
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"{country}'s Turn")

        # Take turn and get response
        response_text, actions = agent.take_turn(season)

        # Show LLM's response
        print(f"{country} says:")
        print("-" * 60)
        print(response_text)
        print("-" * 60)

        # Execute actions if any were parsed
        has_actions = (actions['messages'] or actions['files'])

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


def run_reflect(country: str):
    """Run a strategic reflection session for a country."""
    try:
        agent = DiplomacyAgent(country)
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"{country}'s Strategic Reflection")

        # Take reflection turn
        response_text, actions = agent.take_reflect_turn()

        # Show LLM's response
        print(f"{country} reflects:")
        print("-" * 60)
        print(response_text)
        print("-" * 60)

        # Execute file actions only (messages during reflection are discouraged but allowed)
        has_actions = (actions['messages'] or actions['files'])

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season)
            print(f"\n✓ Reflection complete")
        else:
            print(f"\nNo file updates during reflection.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def check_readiness():
    """Check if all countries are ready to submit orders."""
    print_section_header("READINESS CHECK")
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)
    cheap_model = config.get('cheap_model', 'gemini-flash-latest')
    print(f"Season: {season}")
    print(f"Checking if countries are ready to submit orders...")
    print(f"Using model: {cheap_model} (cheap model for readiness checks)\n")

    ready_count = 0
    need_discussion = 0

    for country in countries:
        print_section_header(country)
        try:
            agent = DiplomacyAgent(country)
            response = agent.check_readiness()
            print(response)

            # Simple heuristic to count readiness
            if "READY" in response.upper() and "NEED MORE" not in response.upper():
                ready_count += 1
            else:
                need_discussion += 1

        except Exception as e:
            print(f"✗ Error checking {country}: {e}")

    print_section_header("SUMMARY")
    print(f"Ready: {ready_count}/{len(countries)}")
    print(f"Need more discussion: {need_discussion}/{len(countries)}")


def overseer():
    """Analyze all conversations for loose ends and unresolved discussions."""
    print_section_header("OVERSEER ANALYSIS")
    config = load_config()
    season = get_current_season(config)
    cheap_model_name = config.get('cheap_model', 'gemini-flash-latest')

    print(f"Season: {season}")
    print(f"Analyzing all conversations for loose ends...")
    print(f"Using model: {cheap_model_name}\n")

    # Load API key and configure Gemini
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(cheap_model_name)

    # Get all conversation files
    conv_dir = Path("conversations")
    if not conv_dir.exists():
        print("No conversations directory found.")
        return

    conv_files = list(conv_dir.glob("*.md"))
    if not conv_files:
        print("No conversations found.")
        return

    # Read all conversations
    all_conversations = []
    for conv_file in sorted(conv_files):
        content = conv_file.read_text()
        # Get last 100 lines
        lines = content.split('\n')
        last_lines = lines[-100:] if len(lines) > 100 else lines
        snippet = '\n'.join(last_lines)

        all_conversations.append(f"## {conv_file.stem}\n{snippet}\n")

    # Combine all conversations
    combined = '\n'.join(all_conversations)

    # Ask LLM to analyze
    prompt = f"""You are overseeing a Diplomacy game. The current season is: {season}

Below are the last ~100 lines from each conversation between countries:

{combined}

Based on these conversations, please identify:
1. Any loose ends or unresolved discussions
2. Promises or agreements that haven't been addressed
3. Questions that were asked but not answered
4. Any tensions or conflicts that seem to be building
5. Overall readiness for the current phase

Be concise and focus on actionable insights."""

    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)

    print(response.text)
    print()


def collect_orders():
    """Collect orders from all countries."""
    print_section_header("COLLECTING ORDERS FROM ALL COUNTRIES")
    config = load_config()
    season = f"{get_current_season(config)} - Orders"
    countries = get_all_countries(config)

    print(f"Season: {season}\n")

    orders_file = Path("orders.md")
    with open(orders_file, 'w') as f:
        f.write(f"# Orders for {season}\n\n")

        for country in countries:
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


def run_season():
    """Run a full season: turns, readiness check, and orders collection."""
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)
    turn_rounds = config.get('season', {}).get('turn_rounds', 2)

    print_section_header(f"RUNNING SEASON: {season}")
    print(f"Countries: {', '.join(countries)}")
    print(f"Turn rounds before readiness check: {turn_rounds}\n")

    # Run initial turn rounds
    for round_num in range(1, turn_rounds + 1):
        print_section_header(f"TURN ROUND {round_num}/{turn_rounds}")

        # Randomize country order
        shuffled = countries.copy()
        random.shuffle(shuffled)
        print(f"Order: {', '.join(shuffled)}\n")

        for country in shuffled:
            run_country_turn(country)
            print()

    # Check readiness loop
    while True:
        print_section_header("READINESS CHECK")
        ready_countries = []
        not_ready_countries = []

        for country in countries:
            try:
                agent = DiplomacyAgent(country)
                response = agent.check_readiness()
                print(f"{country}: {response[:100]}...")

                if "READY" in response.upper() and "NEED MORE" not in response.upper():
                    ready_countries.append(country)
                else:
                    not_ready_countries.append(country)

            except Exception as e:
                print(f"✗ Error checking {country}: {e}")
                not_ready_countries.append(country)

        print(f"\nReady: {len(ready_countries)}/{len(countries)}")

        if len(ready_countries) == len(countries):
            print("All countries ready! Collecting orders...")
            break
        else:
            print(f"Not ready: {', '.join(not_ready_countries)}")
            print("\nRunning another round of turns...")

            # Run another round with randomized order
            shuffled = countries.copy()
            random.shuffle(shuffled)
            print(f"Order: {', '.join(shuffled)}\n")

            for country in shuffled:
                run_country_turn(country)
                print()

    # Collect orders
    collect_orders()
    print_section_header("SEASON COMPLETE")
    print(f"Season {season} finished. Orders saved to orders.md")


def cleanup():
    """Remove all conversations and country files to reset the game."""
    print_section_header("CLEANUP - RESETTING GAME FILES")
    config = load_config()
    countries = get_all_countries(config)
    data_dir = Path(config['paths']['data_dir'])

    # Clear conversations
    conv_dir = data_dir / config['paths']['shared_conversations_dir']
    if conv_dir.exists():
        count = 0
        for conv_file in conv_dir.glob("*.md"):
            conv_file.unlink()
            count += 1
        print(f"✓ Removed {count} conversation files")
    else:
        print("- No conversations directory")

    # Clear country folders
    for country in countries:
        country_dir = data_dir / country
        if country_dir.exists():
            count = 0
            for md_file in country_dir.glob("*.md"):
                md_file.unlink()
                count += 1
            print(f"✓ Removed {count} files from {country}/")
        else:
            print(f"- No {country}/ directory")

    # Clear shared files in classic mode
    if not is_fow(config):
        for shared_file in ['game_state.md', 'game_history.md']:
            shared_path = data_dir / shared_file
            if shared_path.exists():
                shared_path.unlink()
                print(f"✓ Removed shared {shared_file}")

    print("\n✓ Cleanup complete!")
    print("\nRun 'python initialize_game.py' to set up a fresh game.")


def show_status():
    """Show current game status."""
    config = load_config()
    fow_enabled = is_fow(config)
    countries = get_all_countries(config)
    data_dir = Path(config['paths']['data_dir'])
    mode_name = "Fog of War" if fow_enabled else "Classic"

    print_section_header(f"DIPLOMACY LLM - GAME STATUS ({mode_name} Mode)")

    print(f"Current Season: {get_current_season(config)}")
    if config['game'].get('notes'):
        print(f"Notes: {config['game'].get('notes')}")
    print()

    # In classic mode, check for shared game_state.md
    if not fow_enabled:
        shared_state = data_dir / 'game_state.md'
        if shared_state.exists() and shared_state.stat().st_size > 50:
            print("Shared game_state.md: ✓ exists")
        else:
            print("Shared game_state.md: - needs content")
        print()

    # Check conversations directory
    conv_dir = data_dir / config['paths']['shared_conversations_dir']
    if conv_dir.exists():
        conv_files = list(conv_dir.glob("*.md"))
        print(f"Active Conversations: {len(conv_files)}")
        for conv_file in sorted(conv_files):
            content = conv_file.read_text()
            msg_count = content.count('**') // 2  # Rough estimate
            print(f"  - {conv_file.stem}: ~{msg_count} messages")
    else:
        print("Active Conversations: 0")

    print()

    for country in countries:
        country_dir = data_dir / country
        print(f"{country}:")

        if not country_dir.exists():
            print("  ! Directory not found - run initialize_game.py")
            continue

        # Check game_state (only in FoW mode)
        if fow_enabled:
            game_state_file = country_dir / config['paths']['game_state']
            if game_state_file.exists() and game_state_file.stat().st_size > 100:
                print("  ✓ Has game_state.md")
            else:
                print("  - game_state.md needs content")

        # Check game_history
        game_history_file = country_dir / config['paths']['game_history']
        if game_history_file.exists() and game_history_file.stat().st_size > 100:
            print("  ✓ Has game_history.md")
        else:
            print("  - game_history.md needs content")

        # List other files
        other_files = [f.name for f in country_dir.glob("*.md")
                      if f.name not in {config['paths']['game_state'], config['paths']['game_history']}]
        if other_files:
            print(f"  ✓ Agent files: {', '.join(other_files)}")

        print()


def main():
    config = load_config()
    countries = get_all_countries(config)

    if len(sys.argv) < 2:
        print("Diplomacy LLM CLI")
        print()
        print("Usage:")
        print("  python diplomacy.py <country>         # Run a turn for a country")
        print("  python diplomacy.py reflect <country> # Strategic reflection session")
        print("  python diplomacy.py season            # Run full season (turns + readiness + orders)")
        print("  python diplomacy.py readiness         # Check if countries are ready for orders")
        print("  python diplomacy.py overseer          # Analyze conversations for loose ends")
        print("  python diplomacy.py orders            # Collect orders from all countries")
        print("  python diplomacy.py status            # Show game status")
        print("  python diplomacy.py cleanup           # Remove all game files (reset)")
        print(f"\nCountries: {', '.join(countries)}")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Special commands
    if command == "season":
        run_season()
    elif command == "readiness":
        check_readiness()
    elif command == "overseer":
        overseer()
    elif command == "orders":
        collect_orders()
    elif command == "status":
        show_status()
    elif command == "cleanup":
        cleanup()
    elif command == "reflect":
        if len(sys.argv) < 3:
            print("Usage: python diplomacy.py reflect <country>")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)
        country = find_country(sys.argv[2], countries)
        if country is None:
            print(f"Error: '{sys.argv[2]}' is not a recognized country")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)
        run_reflect(country)
    else:
        # Assume it's a country name
        country = find_country(command, countries)
        if country is None:
            print(f"Error: '{command}' is not a recognized command or country")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)

        run_country_turn(country)


if __name__ == "__main__":
    main()

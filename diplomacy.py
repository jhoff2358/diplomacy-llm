#!/usr/bin/env python3
"""
Fog of War Diplomacy LLM CLI
Main interface for running the multi-agent Diplomacy game with fog of war.

Usage:
    python diplomacy.py <country>         # Run a turn for a specific country
    python diplomacy.py reflect <country> # Strategic reflection session
    python diplomacy.py readiness         # Check if countries are ready to submit orders
    python diplomacy.py overseer          # Check for loose ends in all conversations
    python diplomacy.py orders            # Collect orders from all countries
    python diplomacy.py status            # Show current game status
"""

import sys
import yaml
from pathlib import Path
from agent import DiplomacyAgent, get_all_countries
import google.generativeai as genai
from dotenv import load_dotenv
import os


def load_config(config_path: str = "config.yaml"):
    """Load configuration including current season."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_country_turn(country: str):
    """Run a single turn for a country."""
    try:
        agent = DiplomacyAgent(country)

        # Load current season from config.yaml
        config = load_config()
        season = config['game'].get('current_season', 'Unknown')

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

        # Load current season from config.yaml
        config = load_config()
        season = config['game'].get('current_season', 'Unknown')

        print(f"\nCurrent Season: {season}")

        print(f"\n{'='*60}")
        print(f"{country}'s Strategic Reflection")
        print(f"{'='*60}\n")

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
    print("\n" + "="*60)
    print("READINESS CHECK")
    print("="*60 + "\n")

    # Load current season from config.yaml
    config = load_config()
    season = config['game'].get('current_season', 'Unknown')

    cheap_model = config.get('cheap_model', 'gemini-flash-latest')
    print(f"Season: {season}")
    print(f"Checking if countries are ready to submit orders...")
    print(f"Using model: {cheap_model} (cheap model for readiness checks)\n")

    ready_count = 0
    need_discussion = 0

    for country in get_all_countries():
        print(f"\n{'='*60}")
        print(f"{country}")
        print(f"{'='*60}")
        try:
            agent = DiplomacyAgent(country)
            # check_readiness uses cheap model from config by default
            response = agent.check_readiness()
            print(response)

            # Simple heuristic to count readiness
            if "READY" in response.upper() and "NEED MORE" not in response.upper():
                ready_count += 1
            else:
                need_discussion += 1

        except Exception as e:
            print(f"✗ Error checking {country}: {e}")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Ready: {ready_count}/{len(get_all_countries())}")
    print(f"Need more discussion: {need_discussion}/{len(get_all_countries())}")
    print()


def overseer():
    """Analyze all conversations for loose ends and unresolved discussions."""
    print("\n" + "="*60)
    print("OVERSEER ANALYSIS")
    print("="*60 + "\n")

    # Load current season from config.yaml
    config = load_config()
    season = config['game'].get('current_season', 'Unknown')
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
    print("\n" + "="*60)
    print("COLLECTING ORDERS FROM ALL COUNTRIES")
    print("="*60 + "\n")

    # Load current season from config.yaml
    config = load_config()
    season = f"{config['game'].get('current_season', 'Unknown')} - Orders"

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


def cleanup():
    """Remove all conversations and country files to reset the game."""
    print("\n" + "="*60)
    print("CLEANUP - RESETTING GAME FILES")
    print("="*60 + "\n")

    config = load_config()

    # Clear conversations
    conv_dir = Path("conversations")
    if conv_dir.exists():
        count = 0
        for conv_file in conv_dir.glob("*.md"):
            conv_file.unlink()
            count += 1
        print(f"✓ Removed {count} conversation files")
    else:
        print("- No conversations directory")

    # Clear country folders
    for country in get_all_countries():
        country_dir = Path(country)
        if country_dir.exists():
            count = 0
            for md_file in country_dir.glob("*.md"):
                md_file.unlink()
                count += 1
            print(f"✓ Removed {count} files from {country}/")
        else:
            print(f"- No {country}/ directory")

    print("\n✓ Cleanup complete!")
    print("\nRun 'python initialize_game.py' to set up a fresh game.")


def show_status():
    print("\n" + "="*60)
    print("FOG OF WAR DIPLOMACY - GAME STATUS")
    print("="*60 + "\n")

    # Show current game state from config.yaml
    config = load_config()
    print(f"Current Season: {config['game'].get('current_season', 'Unknown')}")
    if config['game'].get('notes'):
        print(f"Notes: {config['game'].get('notes')}")
    print()

    # Check conversations directory
    conv_dir = Path("conversations")
    if conv_dir.exists():
        conv_files = list(conv_dir.glob("*.md"))
        print(f"Active Conversations: {len(conv_files)}")
        for conv_file in sorted(conv_files):
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

        if not country_dir.exists():
            print(f"  ! Directory not found - run initialize_game.py")
            continue

        # Check game_state
        game_state_file = country_dir / config['paths']['game_state']
        if game_state_file.exists() and game_state_file.stat().st_size > 100:
            print(f"  ✓ Has game_state.md")
        else:
            print(f"  - game_state.md needs content")

        # Check game_history
        game_history_file = country_dir / config['paths']['game_history']
        if game_history_file.exists() and game_history_file.stat().st_size > 100:
            print(f"  ✓ Has game_history.md")
        else:
            print(f"  - game_history.md needs content")

        # List other files
        other_files = [f.name for f in country_dir.glob("*.md")
                      if f.name not in {config['paths']['game_state'], config['paths']['game_history']}]
        if other_files:
            print(f"  ✓ Agent files: {', '.join(other_files)}")

        print()


def main():
    if len(sys.argv) < 2:
        print("Fog of War Diplomacy CLI")
        print()
        print("Usage:")
        print("  python diplomacy.py <country>         # Run a turn for a country")
        print("  python diplomacy.py reflect <country> # Strategic reflection session")
        print("  python diplomacy.py readiness         # Check if countries are ready for orders")
        print("  python diplomacy.py overseer          # Analyze conversations for loose ends")
        print("  python diplomacy.py orders            # Collect orders from all countries")
        print("  python diplomacy.py status            # Show game status")
        print("  python diplomacy.py cleanup           # Remove all game files (reset)")
        print(f"\nCountries: {', '.join(get_all_countries())}")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Special commands
    if command == "readiness":
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
            print(f"Countries: {', '.join(get_all_countries())}")
            sys.exit(1)
        country_name = sys.argv[2]
        # Find country (case-insensitive)
        countries = get_all_countries()
        country = None
        for c in countries:
            if c.lower() == country_name.lower():
                country = c
                break
        if country is None:
            print(f"Error: '{country_name}' is not a recognized country")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)
        run_reflect(country)
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

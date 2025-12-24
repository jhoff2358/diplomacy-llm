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
    python diplomacy.py query <country> <question>  # Ask a country a direct question
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
    is_gunboat,
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


def run_query(country: str, question: str):
    """Ask a country a direct question from the GM."""
    try:
        agent = DiplomacyAgent(country)
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"GM Query to {country}")
        print(f"Question: {question}\n")

        response = agent.query(question)

        print(f"{country} responds:")
        print("-" * 60)
        print(response)
        print("-" * 60)

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


def overseer():
    """Analyze all conversations for loose ends and unresolved discussions."""
    print_section_header("OVERSEER ANALYSIS")
    config = load_config()

    if is_gunboat(config):
        print("Overseer is not available in gunboat mode (no conversations).")
        return

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
    data_dir = Path(config['paths']['data_dir'])
    conv_dir = data_dir / config['paths']['shared_conversations_dir']
    if not conv_dir.exists():
        print(f"No conversations directory found at {conv_dir}")
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


def collect_orders(turn_order: list = None) -> bool:
    """Collect orders from all countries.

    Args:
        turn_order: Optional list of countries in order. If None, uses config order.

    Returns:
        True if all countries submitted orders, False if any passed.
        In gunboat mode, always returns True (no PASS option).
    """
    print_section_header("COLLECTING ORDERS")
    config = load_config()
    season = get_current_season(config)
    countries = turn_order or get_all_countries(config)
    gunboat = is_gunboat(config)

    print(f"Season: {season}")
    if gunboat:
        print("Mode: Gunboat (no PASS option)\n")
    else:
        print()

    orders_file = Path("orders.md")
    passed_countries = []
    all_orders = {}

    for country in countries:
        print(f"\nGetting orders from {country}...")
        try:
            agent = DiplomacyAgent(country)
            orders = agent.get_orders()

            # Check if they passed (only in non-gunboat mode)
            if not gunboat and "PASS" in orders.upper().split('\n')[0]:
                passed_countries.append(country)
                print(f"  {country} PASSED - needs more diplomacy time")
                print(f"  Reason: {orders.strip()}")
            else:
                all_orders[country] = orders
                print(f"✓ {country}'s orders received")

        except Exception as e:
            print(f"✗ Error getting orders from {country}: {e}")
            if not gunboat:
                passed_countries.append(country)

    # Only write orders file if everyone submitted
    if not passed_countries:
        with open(orders_file, 'w') as f:
            f.write(f"# Orders for {season}\n\n")
            for country in countries:
                f.write(f"## {country}\n\n")
                f.write(all_orders.get(country, "ERROR: No orders received"))
                f.write("\n\n---\n\n")
        print(f"\n✓ All orders saved to {orders_file}")
        return True
    else:
        print(f"\n! {len(passed_countries)} country/countries passed: {', '.join(passed_countries)}")
        print("Orders NOT saved. Run another round of turns.")
        return False


def load_turn_order() -> list:
    """Load turn order from turn_order.txt."""
    turn_order_file = Path("turn_order.txt")
    if not turn_order_file.exists():
        return []
    lines = turn_order_file.read_text().strip().split('\n')
    return [line.strip() for line in lines if line.strip()]


def save_turn_order(turn_order: list):
    """Save turn order to turn_order.txt."""
    turn_order_file = Path("turn_order.txt")
    turn_order_file.write_text('\n'.join(turn_order) + '\n')


def randomize_order():
    """Randomize and save turn order to turn_order.txt."""
    config = load_config()
    countries = get_all_countries(config)
    turn_order = countries.copy()
    random.shuffle(turn_order)
    save_turn_order(turn_order)
    print(f"Turn order saved to turn_order.txt:")
    for country in turn_order:
        print(f"  {country}")


def run_all_turns():
    """Run turns for all countries in order from turn_order.txt."""
    turn_order = load_turn_order()
    if not turn_order:
        print("Error: turn_order.txt not found or empty. Run 'randomize' first.")
        return

    print(f"Running turns for: {', '.join(turn_order)}\n")
    for country in turn_order:
        run_country_turn(country)
        print()


def run_season():
    """Run a full season: turns, orders collection (with pass loop).

    In gunboat mode: 1 planning turn, then mandatory orders.
    In classic mode: Multiple turn rounds, then orders with PASS loop.
    """
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)
    gunboat = is_gunboat(config)

    if gunboat:
        # Gunboat: Single turn per country - they include orders in orders.md
        print_section_header(f"RUNNING SEASON: {season}")
        print("Mode: Gunboat")
        print(f"Countries: {', '.join(countries)}\n")

        for country in countries:
            print(f"--- {country} ---")
            run_country_turn(country)
            print()
    else:
        # Classic: Randomize order, multiple rounds, PASS loop
        turn_order = countries.copy()
        random.shuffle(turn_order)
        save_turn_order(turn_order)

        print_section_header(f"RUNNING SEASON: {season}")
        print("Mode: Classic")
        print(f"Turn order: {', '.join(turn_order)}")

        turn_rounds = config.get('season', {}).get('turn_rounds', 2)
        print(f"Turn rounds before orders: {turn_rounds}\n")

        # Run initial turn rounds
        for round_num in range(1, turn_rounds + 1):
            print_section_header(f"TURN ROUND {round_num}/{turn_rounds}")

            for country in turn_order:
                run_country_turn(country)
                print()

        # Orders loop - keep running turns until everyone submits
        while True:
            all_submitted = collect_orders(turn_order)

            if all_submitted:
                break
            else:
                print("\nRunning another round of turns...")
                for country in turn_order:
                    run_country_turn(country)
                    print()

    print_section_header("SEASON COMPLETE")
    if gunboat:
        print(f"Season {season} finished. Orders in each country's orders.md")
    else:
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


def initialize_game(skip_cleanup: bool = False):
    """Initialize the game. Runs cleanup first by default."""
    if not skip_cleanup:
        cleanup()
        print()  # Add spacing between cleanup and init output

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
            print("✓ Copied beginning_info.md to game_state.md")
        else:
            shared_game_state.write_text(create_shared_game_state_template())
            print("✓ Created game_state.md (beginning_info.md not found)")
        shared_game_history = data_dir / 'game_history.md'
        shared_game_history.write_text(create_shared_game_history_template())
        print("✓ Created game_history.md")

    print("\n✓ Game initialized!")
    print(f"\nMode: {mode_name}")
    print("\nNext steps:")
    if fow_enabled:
        print("  1. Fill in each country's game_state.md with their starting visibility")
        print("  2. Make sure your .env file has your Gemini API key")
        print("  3. Run: python diplomacy.py status")
        print("  4. Start the game: python diplomacy.py season")
    else:
        print("  1. Make sure your .env file has your Gemini API key")
        print("  2. Run: python diplomacy.py status")
        print("  3. Start the game: python diplomacy.py season")


def show_status():
    """Show current game status."""
    config = load_config()
    fow_enabled = is_fow(config)
    gunboat_enabled = is_gunboat(config)
    countries = get_all_countries(config)
    data_dir = Path(config['paths']['data_dir'])

    if gunboat_enabled:
        mode_name = "Gunboat"
    elif fow_enabled:
        mode_name = "Fog of War"
    else:
        mode_name = "Classic"

    print_section_header(f"DIPLOMACY LLM - GAME STATUS ({mode_name} Mode)")

    print(f"Current Season: {get_current_season(config)}")
    if config['game'].get('notes'):
        print(f"Notes: {config['game'].get('notes')}")
    print()

    # Check shared game files (used by classic and gunboat modes)
    if not fow_enabled:
        shared_state = data_dir / 'game_state.md'
        if shared_state.exists() and shared_state.stat().st_size > 50:
            print("Shared game_state.md: ✓ exists")
        else:
            print("Shared game_state.md: - needs content")

        shared_history = data_dir / 'game_history.md'
        if shared_history.exists() and shared_history.stat().st_size > 50:
            print("Shared game_history.md: ✓ exists")
        else:
            print("Shared game_history.md: - needs content")
        print()

    # Check conversations directory (not relevant for gunboat)
    if not gunboat_enabled:
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
            print("  ! Directory not found - run 'python diplomacy.py init'")
            continue

        # Check per-country game files (only in FoW mode)
        if fow_enabled:
            game_state_file = country_dir / config['paths']['game_state']
            if game_state_file.exists() and game_state_file.stat().st_size > 100:
                print("  ✓ Has game_state.md")
            else:
                print("  - game_state.md needs content")

            game_history_file = country_dir / config['paths']['game_history']
            if game_history_file.exists() and game_history_file.stat().st_size > 100:
                print("  ✓ Has game_history.md")
            else:
                print("  - game_history.md needs content")

        # List other files (agent's own files)
        other_files = [f.name for f in country_dir.glob("*.md")
                      if f.name not in {config['paths']['game_state'], config['paths']['game_history']}]
        if other_files:
            print(f"  ✓ Agent files: {', '.join(other_files)}")

        print()


def show_help(config: dict):
    """Show help text with available commands."""
    countries = get_all_countries(config)
    gunboat = is_gunboat(config)
    fow = is_fow(config)

    mode = "Gunboat" if gunboat else ("Fog of War" if fow else "Classic")

    print("Diplomacy LLM CLI")
    print(f"Current mode: {mode}")
    print()
    print("Commands:")
    print("  season              Run a full season (planning + orders)")
    print("  orders              Collect orders from all countries")
    print("  randomize           Randomize and save turn order to turn_order.txt")
    print("  all                 Run turns for all countries (from turn_order.txt)")
    print("  <country>           Run a single turn for a country")
    print("  reflect [country]   Strategic reflection (all countries, or one if specified)")
    print("  query <country> \"question\"  Ask a country a direct question")
    if not gunboat:
        print("  overseer            Analyze conversations for loose ends")
    print("  status              Show game status and file info")
    print("  init                Initialize game (runs cleanup first)")
    print("  init --no-cleanup   Initialize without running cleanup")
    print("  cleanup             Remove all game files (reset)")
    print("  help, -h, --help    Show this help message")
    print()
    print(f"Countries: {', '.join(countries)}")
    print()
    if gunboat:
        print("Gunboat mode: No diplomacy - 1 planning turn, then mandatory orders.")
    else:
        print(f"Classic mode: {config.get('season', {}).get('turn_rounds', 2)} turn rounds, then orders (can PASS).")


def main():
    config = load_config()
    countries = get_all_countries(config)

    if len(sys.argv) < 2 or sys.argv[1].lower() in ('help', '-h', '--help'):
        show_help(config)
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    command = sys.argv[1].lower()

    # Special commands
    if command == "randomize":
        randomize_order()
    elif command == "all":
        run_all_turns()
    elif command == "season":
        run_season()
    elif command == "orders":
        collect_orders()
    elif command == "overseer":
        overseer()
    elif command == "status":
        show_status()
    elif command == "cleanup":
        cleanup()
    elif command == "init":
        skip_cleanup = "--no-cleanup" in sys.argv
        initialize_game(skip_cleanup=skip_cleanup)
    elif command == "reflect":
        if len(sys.argv) >= 3:
            # Single country reflection
            country = find_country(sys.argv[2], countries)
            if country is None:
                print(f"Error: '{sys.argv[2]}' is not a recognized country")
                print(f"Countries: {', '.join(countries)}")
                sys.exit(1)
            run_reflect(country)
        else:
            # All countries reflection
            print_section_header("REFLECTION PHASE")
            for country in countries:
                run_reflect(country)
                print()
    elif command == "query":
        if len(sys.argv) < 4:
            print("Usage: python diplomacy.py query <country> <question>")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)
        country = find_country(sys.argv[2], countries)
        if country is None:
            print(f"Error: '{sys.argv[2]}' is not a recognized country")
            print(f"Countries: {', '.join(countries)}")
            sys.exit(1)
        # Join remaining args as the question
        question = ' '.join(sys.argv[3:])
        run_query(country, question)
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

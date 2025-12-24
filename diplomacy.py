#!/usr/bin/env python3
"""
Diplomacy LLM CLI
Main interface for running the multi-agent Diplomacy game.
Supports classic, fog of war, and gunboat modes.

Usage:
    python diplomacy.py <command>
    python diplomacy.py help
"""

import os
import sys
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

from agent import DiplomacyAgent
from game_manager import cleanup, initialize_game, show_status
from orchestrator import (
    collect_orders,
    randomize_order,
    run_all_turns,
    run_country_turn,
    run_season,
)
from utils import (
    load_config,
    is_gunboat,
    get_all_countries,
    get_current_season,
    get_mode_name,
    get_conversations_dir,
    find_country,
    print_section_header,
    print_divider,
    handle_error,
    OVERSEER_LINE_LIMIT,
)


# =============================================================================
# Turn Functions (kept here as they're thin wrappers around agent)
# =============================================================================

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
        print_divider()
        print(response)
        print_divider()

    except Exception as e:
        handle_error(e, f"query to {country}")


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
        print_divider()
        print(response_text)
        print_divider()

        # Execute file actions only (messages during reflection are discouraged but allowed)
        has_actions = (actions['messages'] or actions['files'])

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season)
            print(f"\n✓ Reflection complete")
        else:
            print(f"\nNo file updates during reflection.")

    except Exception as e:
        handle_error(e, f"{country}'s reflection")


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
    conv_dir = get_conversations_dir(config)
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
        # Get last N lines
        lines = content.split('\n')
        last_lines = lines[-OVERSEER_LINE_LIMIT:] if len(lines) > OVERSEER_LINE_LIMIT else lines
        snippet = '\n'.join(last_lines)

        all_conversations.append(f"## {conv_file.stem}\n{snippet}\n")

    # Combine all conversations
    combined = '\n'.join(all_conversations)

    # Ask LLM to analyze
    prompt = f"""You are overseeing a Diplomacy game. The current season is: {season}

Below are the last ~{OVERSEER_LINE_LIMIT} lines from each conversation between countries:

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


# =============================================================================
# Help
# =============================================================================

def show_help(config: dict):
    """Show help text with available commands."""
    countries = get_all_countries(config)
    gunboat = is_gunboat(config)
    mode = get_mode_name(config)

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


# =============================================================================
# CLI Dispatcher
# =============================================================================

# Command dispatch table for simple commands
COMMANDS = {
    'randomize': randomize_order,
    'all': run_all_turns,
    'season': run_season,
    'orders': collect_orders,
    'overseer': overseer,
    'status': show_status,
    'cleanup': cleanup,
}


def main():
    config = load_config()
    countries = get_all_countries(config)

    if len(sys.argv) < 2 or sys.argv[1].lower() in ('help', '-h', '--help'):
        show_help(config)
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    command = sys.argv[1].lower()

    # Check dispatch table first
    if command in COMMANDS:
        COMMANDS[command]()
        return

    # Commands with special handling
    if command == "init":
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

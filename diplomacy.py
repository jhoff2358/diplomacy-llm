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

from src.agent import DiplomacyAgent
from src.game_manager import cleanup, initialize_game, show_status
from src.orchestrator import (
    randomize_order,
    run_all_turns,
    run_country_turn,
    run_country_reflect,
    run_all_reflects,
    run_country_plan,
    run_all_plans,
    run_season,
)
from src.utils import (
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


def run_reflect(country: str, wipe_void: bool = False):
    """Run a strategic reflection session for a country.

    Thin wrapper around run_country_reflect for backwards compatibility.
    """
    run_country_reflect(country, wipe_void=wipe_void)


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
# Setup
# =============================================================================

def setup():
    """Install dependencies and configure environment."""
    import subprocess
    import shutil

    print("Diplomacy LLM Setup")
    print("===================\n")

    # Install dependencies
    print("Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=False
    )

    if result.returncode != 0:
        print("\n✗ Failed to install dependencies")
        return

    print("\n✓ Dependencies installed")

    # Check/create .env
    env_path = Path(".env")
    if not env_path.exists():
        example_path = Path(".env.example")
        if example_path.exists():
            shutil.copy(example_path, env_path)
            print("✓ Created .env from template")
            print("  → Please add your GEMINI_API_KEY to .env")
        else:
            env_path.write_text("GEMINI_API_KEY=your_api_key_here\n")
            print("✓ Created .env file")
            print("  → Please add your GEMINI_API_KEY to .env")
    else:
        print("✓ .env file exists")

    print("\nSetup complete! Next steps:")
    print("  1. Add your GEMINI_API_KEY to .env (if not already done)")
    print("  2. Run: python diplomacy.py init")
    print("  3. Run: python diplomacy.py status")


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
    print("  season              Run a full season (plan + turns + reflect)")
    print("  randomize           Randomize and save turn order to turn_order.txt")
    print("  all                 Run turns for all countries (from turn_order.txt)")
    print("  <country>           Run a single turn for a country")
    print("  reflect [country] [--all] [--wipe-void]  Strategic reflection")
    print("  plan [country]      Consider options before diplomacy")
    print("  query <country> \"question\"  Ask a country a direct question")
    if not gunboat:
        print("  overseer            Analyze conversations for loose ends")
    print("  status              Show game status and file info")
    print("  init                Initialize game (runs cleanup first)")
    print("  init --no-cleanup   Initialize without running cleanup")
    print("  cleanup             Remove all game files (reset)")
    print("  setup               Install dependencies and configure environment")
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
    'overseer': overseer,
    'status': show_status,
    'cleanup': cleanup,
    'setup': setup,
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
        # Parse flags
        wipe_void = "--wipe-void" in sys.argv
        run_all_from = "--all" in sys.argv

        # Get non-flag args
        args = [a for a in sys.argv[2:] if not a.startswith('--')]

        if args:
            country_arg = args[0]
            country = find_country(country_arg, countries)
            if country is None:
                print(f"Error: '{country_arg}' is not a recognized country")
                print(f"Countries: {', '.join(countries)}")
                sys.exit(1)

            if run_all_from:
                # Start from this country and continue through the rest
                print_section_header("REFLECTION PHASE")
                if wipe_void:
                    print("(void.md will be cleared after each reflect)\n")
                start_index = countries.index(country)
                for c in countries[start_index:]:
                    run_reflect(c, wipe_void=wipe_void)
                    print()
            else:
                # Single country reflection
                run_reflect(country, wipe_void=wipe_void)
        else:
            # All countries reflection
            run_all_reflects(wipe_void=wipe_void)

    elif command == "plan":
        # Get non-flag args
        args = [a for a in sys.argv[2:] if not a.startswith('--')]

        if args:
            country_arg = args[0]
            country = find_country(country_arg, countries)
            if country is None:
                print(f"Error: '{country_arg}' is not a recognized country")
                print(f"Countries: {', '.join(countries)}")
                sys.exit(1)
            run_country_plan(country)
        else:
            # All countries plan
            run_all_plans()

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

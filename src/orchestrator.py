"""
Game orchestration for Diplomacy LLM.
Handles season execution, turn order management, and order collection.
"""

import random
from pathlib import Path

from .agent import DiplomacyAgent
from .utils import (
    load_config,
    is_gunboat,
    get_all_countries,
    get_current_season,
    print_section_header,
    handle_error,
    print_divider,
)


# =============================================================================
# Season Header Management
# =============================================================================

def add_season_headers():
    """Add season headers to all conversation and void files.

    Called at the start of each season to add a single header for the season,
    rather than prepending to each message.
    """
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)

    header = f"\n## {season}\n"

    # Add headers to all conversation files
    from .utils import get_conversations_dir
    conversations_dir = get_conversations_dir(config)
    if conversations_dir.exists():
        for conv_file in conversations_dir.glob("*.md"):
            with open(conv_file, 'a') as f:
                f.write(header)

    # Add headers to all void files
    from .utils import get_country_dir
    for country in countries:
        void_path = get_country_dir(config, country) / 'void.md'
        with open(void_path, 'a') as f:
            f.write(header)

    print(f"✓ Added season headers ({season}) to conversations and void files")


# =============================================================================
# Turn Order Management
# =============================================================================

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


# =============================================================================
# Individual Turn Execution
# =============================================================================

def run_country_turn(country: str, use_cheap_model: bool = True):
    """Run a single turn for a country (classic mode - messaging + void.md only)."""
    try:
        agent = DiplomacyAgent(country, use_cheap_model=use_cheap_model)
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"{country}'s Turn")

        # Take turn and get response
        response_text, actions = agent.take_turn(season)

        # Show LLM's response
        print(f"{country} says:")
        print_divider()
        print(response_text)
        print_divider()

        # Execute actions if any were parsed (void.md only, append-only)
        has_actions = (actions['messages'] or actions['files'])

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season,
                                  restrict_files=['void.md'],
                                  append_only_files=['void.md'])
            print(f"\n✓ Turn complete")
        else:
            print(f"\nNo actions taken this turn.")

    except Exception as e:
        handle_error(e, f"{country}'s turn")


def run_country_react(country: str):
    """Run a react phase for a country (gunboat mode - void.md + orders)."""
    try:
        agent = DiplomacyAgent(country, use_cheap_model=True)
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"{country}'s React")

        # Take react turn
        response_text, actions = agent.take_react_turn()

        # Show LLM's response
        print(f"{country} says:")
        print_divider()
        print(response_text)
        print_divider()

        # Execute actions (void.md append-only, orders.md full access)
        has_actions = (actions['messages'] or actions['files'])

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season,
                                  restrict_files=['void.md', 'orders.md'],
                                  append_only_files=['void.md'])
            print(f"\n✓ React complete")
        else:
            print(f"\nNo actions taken this phase.")

    except Exception as e:
        handle_error(e, f"{country}'s react")


def run_country_reflect(country: str, wipe_void: bool = False):
    """Run a reflect phase for a country."""
    try:
        agent = DiplomacyAgent(country, use_cheap_model=False)  # Use main model
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"{country}'s Reflect")

        # Take reflect turn
        response_text, actions = agent.take_reflect_turn(wipe_void=wipe_void)

        # Show LLM's response
        print(f"{country} says:")
        print_divider()
        print(response_text)
        print_divider()

        # Execute actions (full file access during reflect)
        has_actions = actions['files']

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season)  # No file restrictions
            print(f"\n✓ Reflect complete")
        else:
            print(f"\nNo file operations this phase.")

        # Wipe void.md if requested
        if wipe_void:
            from .utils import get_country_dir
            void_path = get_country_dir(config, country) / 'void.md'
            if void_path.exists():
                void_path.unlink()
                print(f"  ✓ Cleared void.md")

    except Exception as e:
        handle_error(e, f"{country}'s reflect")


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


# =============================================================================
# Season Execution
# =============================================================================

def run_gunboat_season():
    """Run a season in gunboat mode: plan then react phase.

    Flow:
    1. PLAN (all countries) - cheap_model, consider options
    2. REACT (all countries) - cheap_model, void.md + orders.md
    """
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)

    print_section_header(f"RUNNING SEASON: {season}")
    print("Mode: Gunboat")
    print(f"Countries: {', '.join(countries)}\n")

    # Add season headers to void files (no conversations in gunboat mode)
    add_season_headers()

    # Plan phase - consider options before diplomacy
    print_section_header("PLAN PHASE")
    for country in countries:
        run_country_plan(country)
        print()

    # React phase - each country submits orders
    print_section_header("REACT PHASE")
    for country in countries:
        run_country_react(country)
        print()

    print_section_header("SEASON COMPLETE")
    print(f"Season {season} finished. Orders in each country's orders.md")


def run_classic_season():
    """Run a season in classic mode: plan, turn rounds, then reflect with orders.

    Flow:
    1. PLAN (all countries) - cheap_model, consider options
    2. TURN ROUNDS (turn_rounds × all countries) - cheap_model, messages + void.md
    3. REFLECT (all countries) - main model, full file access + orders.md
    """
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)

    # Randomize order for the season
    turn_order = countries.copy()
    random.shuffle(turn_order)
    save_turn_order(turn_order)

    print_section_header(f"RUNNING SEASON: {season}")
    print("Mode: Classic")
    print(f"Turn order: {', '.join(turn_order)}")

    turn_rounds = config.get('season', {}).get('turn_rounds', 2)
    print(f"Turn rounds: {turn_rounds}\n")

    # Add season headers to conversations and void files
    add_season_headers()

    # Plan phase - consider options before diplomacy
    print_section_header("PLAN PHASE")
    for country in turn_order:
        run_country_plan(country)
        print()

    # Run turn rounds (messaging + void.md only)
    for round_num in range(1, turn_rounds + 1):
        print_section_header(f"TURN ROUND {round_num}/{turn_rounds}")

        for country in turn_order:
            run_country_turn(country)
            print()

    # Reflect phase - all countries reflect and submit orders
    print_section_header("REFLECT PHASE")
    for country in turn_order:
        run_country_reflect(country)
        print()

    print_section_header("SEASON COMPLETE")
    print(f"Season {season} finished. Orders in each country's orders.md")


def run_season():
    """Run a full season based on the current game mode."""
    config = load_config()
    if is_gunboat(config):
        run_gunboat_season()
    else:
        run_classic_season()


def run_all_reflects(wipe_void: bool = False):
    """Run reflect for all countries.

    Args:
        wipe_void: If True, clear each country's void.md after reflect
    """
    config = load_config()
    countries = get_all_countries(config)
    season = get_current_season(config)

    print_section_header(f"REFLECT PHASE: {season}")
    if wipe_void:
        print("(void.md will be cleared after each reflect)\n")

    for country in countries:
        run_country_reflect(country, wipe_void=wipe_void)
        print()


# =============================================================================
# Plan Phase (Consider Options Before Diplomacy)
# =============================================================================

def run_country_plan(country: str):
    """Run a plan phase for a country to consider options before diplomacy."""
    try:
        agent = DiplomacyAgent(country, use_cheap_model=True)  # Use cheap model
        config = load_config()
        season = get_current_season(config)

        print(f"\nCurrent Season: {season}")
        print_section_header(f"{country}'s Plan")

        # Take plan turn
        response_text, actions = agent.take_plan_turn()

        # Show LLM's response
        print(f"{country} says:")
        print_divider()
        print(response_text)
        print_divider()

        # Execute actions (any file, no restrictions)
        has_actions = actions['files']

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season)
            print(f"\n✓ Plan complete")
        else:
            print(f"\nNo actions this phase.")

    except Exception as e:
        handle_error(e, f"{country}'s plan")


def run_all_plans():
    """Run plan phase for all countries to consider options."""
    config = load_config()
    countries = get_all_countries(config)
    season = get_current_season(config)

    print_section_header(f"PLAN PHASE: {season}")
    print("Considering options before diplomacy...\n")

    for country in countries:
        run_country_plan(country)
        print()

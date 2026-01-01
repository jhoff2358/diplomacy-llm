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

        # Execute actions if any were parsed (void.md only for files)
        has_actions = (actions['messages'] or actions['files'])

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season, restrict_files=['void.md'])
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

        # Execute actions (void.md + orders.md only)
        has_actions = (actions['messages'] or actions['files'])

        if has_actions:
            print(f"\nExecuting actions:")
            agent.execute_actions(actions, season, restrict_files=['void.md', 'orders.md'])
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
# Order Collection
# =============================================================================

def _is_build_or_retreat_phase(season: str) -> bool:
    """Check if the season is a winter build or retreat phase.

    TODO: This is a temporary workaround. Countries PASS in these phases because
    they have no builds/retreats available, not because they need more diplomacy
    time. We should properly detect which countries have actions available and
    only collect orders from them, rather than always storing orders.
    """
    season_lower = season.lower()
    return 'winter' in season_lower or 'retreat' in season_lower


def collect_orders(turn_order: list = None) -> bool:
    """Collect orders from all countries.

    Args:
        turn_order: Optional list of countries in order. If None, uses config order.

    Returns:
        True if all countries submitted orders, False if any passed.
        In gunboat mode, always returns True (no PASS option).
        In winter/retreat phases, always returns True (countries may PASS if no builds/retreats).
    """
    print_section_header("COLLECTING ORDERS")
    config = load_config()
    season = get_current_season(config)
    countries = turn_order or get_all_countries(config)
    gunboat = is_gunboat(config)
    build_or_retreat = _is_build_or_retreat_phase(season)

    print(f"Season: {season}")
    if gunboat:
        print("Mode: Gunboat (no PASS option)\n")
    elif build_or_retreat:
        print("Mode: Build/Retreat phase (PASS allowed, orders always saved)\n")
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
                if build_or_retreat:
                    # In build/retreat, PASS means no actions available - still record it
                    all_orders[country] = orders
                    print(f"  {country} PASSED (no builds/retreats)")
                else:
                    print(f"  {country} PASSED - needs more diplomacy time")
                    print(f"  Reason: {orders.strip()}")
            else:
                all_orders[country] = orders
                print(f"✓ {country}'s orders received")

        except Exception as e:
            print(f"✗ Error getting orders from {country}: {e}")
            if not gunboat and not build_or_retreat:
                passed_countries.append(country)

    # Write orders file if everyone submitted OR if it's a build/retreat phase
    if not passed_countries or build_or_retreat:
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


# =============================================================================
# Season Execution
# =============================================================================

def run_gunboat_season():
    """Run a season in gunboat mode: react phase for all countries.

    Flow:
    1. REACT (all countries) - cheap_model, void.md + orders.md
    """
    config = load_config()
    season = get_current_season(config)
    countries = get_all_countries(config)

    print_section_header(f"RUNNING SEASON: {season}")
    print("Mode: Gunboat")
    print(f"Countries: {', '.join(countries)}\n")

    # React phase - each country reacts and submits orders
    print_section_header("REACT PHASE")
    for country in countries:
        run_country_react(country)
        print()

    print_section_header("SEASON COMPLETE")
    print(f"Season {season} finished. Orders in each country's orders.md")


def run_classic_season():
    """Run a season in classic mode: turn rounds + reflect with orders.

    Flow:
    1. TURN ROUNDS (turn_rounds × all countries) - cheap_model, messages + void.md
    2. REFLECT (all countries) - main model, full file access + orders.md
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

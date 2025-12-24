"""
Game state management for Diplomacy LLM.
Handles initialization, cleanup, status display, and templates.
"""

from pathlib import Path

from .utils import (
    load_config,
    is_fow,
    is_gunboat,
    get_all_countries,
    get_current_season,
    get_mode_name,
    get_data_dir,
    get_conversations_dir,
    get_country_dir,
    print_section_header,
    MIN_FILE_SIZE,
)


# =============================================================================
# Templates
# =============================================================================

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


# =============================================================================
# Cleanup
# =============================================================================

def cleanup():
    """Remove all conversations and country files to reset the game."""
    print_section_header("CLEANUP - RESETTING GAME FILES")
    config = load_config()
    countries = get_all_countries(config)
    data_dir = get_data_dir(config)

    # Clear conversations
    conv_dir = get_conversations_dir(config)
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
        country_dir = get_country_dir(config, country)
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


# =============================================================================
# Initialization
# =============================================================================

def initialize_game(skip_cleanup: bool = False):
    """Initialize the game. Runs cleanup first by default."""
    if not skip_cleanup:
        cleanup()
        print()  # Add spacing between cleanup and init output

    config = load_config()
    fow_enabled = is_fow(config)
    gunboat_enabled = is_gunboat(config)
    countries = get_all_countries(config)
    mode_name = get_mode_name(config)

    print(f"Initializing {mode_name} Diplomacy game...\n")

    data_dir = get_data_dir(config)

    # Create conversations directory (not needed for gunboat)
    if not gunboat_enabled:
        conversations_dir = get_conversations_dir(config)
        conversations_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {conversations_dir}/")

    # Create per-country directories
    for country in countries:
        country_dir = get_country_dir(config, country)
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


# =============================================================================
# Status Display
# =============================================================================

def show_status():
    """Show current game status."""
    config = load_config()
    fow_enabled = is_fow(config)
    gunboat_enabled = is_gunboat(config)
    countries = get_all_countries(config)
    data_dir = get_data_dir(config)
    mode_name = get_mode_name(config)

    print_section_header(f"DIPLOMACY LLM - GAME STATUS ({mode_name} Mode)")

    print(f"Current Season: {get_current_season(config)}")
    if config['game'].get('notes'):
        print(f"Notes: {config['game'].get('notes')}")
    print()

    # Check shared game files (used by classic and gunboat modes)
    if not fow_enabled:
        shared_state = data_dir / 'game_state.md'
        if shared_state.exists() and shared_state.stat().st_size > MIN_FILE_SIZE:
            print("Shared game_state.md: ✓ exists")
        else:
            print("Shared game_state.md: - needs content")

        shared_history = data_dir / 'game_history.md'
        if shared_history.exists() and shared_history.stat().st_size > MIN_FILE_SIZE:
            print("Shared game_history.md: ✓ exists")
        else:
            print("Shared game_history.md: - needs content")
        print()

    # Check conversations directory (not relevant for gunboat)
    if not gunboat_enabled:
        conv_dir = get_conversations_dir(config)
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
        country_dir = get_country_dir(config, country)
        print(f"{country}:")

        if not country_dir.exists():
            print("  ! Directory not found - run 'python diplomacy.py init'")
            continue

        # Check per-country game files (only in FoW mode)
        if fow_enabled:
            game_state_file = country_dir / config['paths']['game_state']
            if game_state_file.exists() and game_state_file.stat().st_size > MIN_FILE_SIZE:
                print("  ✓ Has game_state.md")
            else:
                print("  - game_state.md needs content")

            game_history_file = country_dir / config['paths']['game_history']
            if game_history_file.exists() and game_history_file.stat().st_size > MIN_FILE_SIZE:
                print("  ✓ Has game_history.md")
            else:
                print("  - game_history.md needs content")

        # List other files (agent's own files)
        other_files = [f.name for f in country_dir.glob("*.md")
                      if f.name not in {config['paths']['game_state'], config['paths']['game_history']}]
        if other_files:
            print(f"  ✓ Agent files: {', '.join(other_files)}")

        print()

"""
Shared utility functions for Diplomacy LLM.
Centralizes common patterns used across modules.
"""

import traceback
from pathlib import Path
from typing import Optional, List
import yaml


# =============================================================================
# Constants
# =============================================================================

DIVIDER_WIDTH = 60
OVERSEER_LINE_LIMIT = 100
MIN_FILE_SIZE = 100


# =============================================================================
# Configuration
# =============================================================================

def load_config(config_path: str = "config.yaml") -> dict:
    """Load and return the game configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def is_fow(config: dict) -> bool:
    """Check if fog of war mode is enabled."""
    return config.get('features', {}).get('fog_of_war', False)


def is_gunboat(config: dict) -> bool:
    """Check if gunboat mode is enabled (no diplomacy)."""
    return config.get('features', {}).get('gunboat', False)


def get_current_season(config: dict) -> str:
    """Get the current season from game_state.md.

    Reads the first line of game_state.md (or shared game_state.md in classic mode).
    Expected format: 'Season: Spring 1901' or just 'Spring 1901'
    """
    data_dir = Path(config['paths']['data_dir'])

    # FoW uses per-country files; Classic/Gunboat use shared root file
    if is_fow(config):
        # Use first country's game_state
        countries = config.get('countries', [])
        if countries:
            game_state_path = data_dir / countries[0] / config['paths']['game_state']
        else:
            return 'Unknown'
    else:
        game_state_path = data_dir / 'game_state.md'

    if not game_state_path.exists():
        return 'Unknown'

    first_line = game_state_path.read_text().split('\n')[0].strip()

    # Handle "Season: Spring 1901" or just "Spring 1901"
    if first_line.lower().startswith('season:'):
        return first_line.split(':', 1)[1].strip()
    return first_line if first_line else 'Unknown'


def get_all_countries(config: dict) -> List[str]:
    """Get list of all countries from config."""
    return config.get('countries', [])


def find_country(name: str, countries: List[str]) -> Optional[str]:
    """Find a country by name (case-insensitive).

    Returns the properly-cased country name if found, None otherwise.
    """
    name_lower = name.lower()
    for country in countries:
        if country.lower() == name_lower:
            return country
    return None


def print_section_header(title: str, width: int = DIVIDER_WIDTH):
    """Print a formatted section header."""
    print(f"\n{'='*width}")
    print(title)
    print(f"{'='*width}\n")


def print_divider():
    """Print a horizontal divider line."""
    print("-" * DIVIDER_WIDTH)


# =============================================================================
# Mode Helpers
# =============================================================================

def get_mode_name(config: dict) -> str:
    """Get the display name for the current game mode."""
    if is_gunboat(config):
        return "Gunboat"
    elif is_fow(config):
        return "Fog of War"
    else:
        return "Classic"


# =============================================================================
# Path Helpers
# =============================================================================

def get_data_dir(config: dict) -> Path:
    """Get the data directory path."""
    return Path(config['paths']['data_dir'])


def get_conversations_dir(config: dict) -> Path:
    """Get the shared conversations directory path."""
    return get_data_dir(config) / config['paths']['shared_conversations_dir']


def get_country_dir(config: dict, country: str) -> Path:
    """Get a country's data directory path."""
    return get_data_dir(config) / country


# =============================================================================
# Error Handling
# =============================================================================

def handle_error(e: Exception, context: str = ""):
    """Print error with traceback in a consistent format."""
    if context:
        print(f"Error in {context}: {e}")
    else:
        print(f"Error: {e}")
    traceback.print_exc()

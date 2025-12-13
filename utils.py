"""
Shared utility functions for Diplomacy LLM.
Centralizes common patterns used across modules.
"""

from pathlib import Path
from typing import Optional, List
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    """Load and return the game configuration."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def is_fow(config: dict) -> bool:
    """Check if fog of war mode is enabled."""
    return config.get('features', {}).get('fog_of_war', False)


def get_current_season(config: dict) -> str:
    """Get the current season from game_state.md.

    Reads the first line of game_state.md (or shared game_state.md in classic mode).
    Expected format: 'Season: Spring 1901' or just 'Spring 1901'
    """
    data_dir = Path(config['paths']['data_dir'])

    # In classic mode, read from root; in FoW mode, pick any country's file
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


def print_section_header(title: str, width: int = 60):
    """Print a formatted section header."""
    print(f"\n{'='*width}")
    print(title)
    print(f"{'='*width}\n")

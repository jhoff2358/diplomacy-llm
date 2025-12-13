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
    """Get the current season from config."""
    return config['game'].get('current_season', 'Unknown')


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

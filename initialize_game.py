#!/usr/bin/env python3
"""
Initialize shared game_history.md with standard Diplomacy starting positions.
"""

from pathlib import Path

# Standard Diplomacy starting positions
STARTING_POSITIONS = {
    "Austria": {
        "centers": ["Vienna", "Budapest", "Trieste"],
        "units": ["A Vienna", "A Budapest", "F Trieste"]
    },
    "England": {
        "centers": ["London", "Liverpool", "Edinburgh"],
        "units": ["F London", "F Edinburgh", "A Liverpool"]
    },
    "France": {
        "centers": ["Paris", "Marseilles", "Brest"],
        "units": ["A Paris", "A Marseilles", "F Brest"]
    },
    "Germany": {
        "centers": ["Berlin", "Munich", "Kiel"],
        "units": ["A Berlin", "A Munich", "F Kiel"]
    },
    "Italy": {
        "centers": ["Rome", "Venice", "Naples"],
        "units": ["A Rome", "A Venice", "F Naples"]
    },
    "Russia": {
        "centers": ["Moscow", "Warsaw", "Sevastopol", "St Petersburg"],
        "units": ["A Moscow", "A Warsaw", "F Sevastopol", "F St Petersburg (sc)"]
    },
    "Turkey": {
        "centers": ["Constantinople", "Ankara", "Smyrna"],
        "units": ["A Constantinople", "A Smyrna", "F Ankara"]
    }
}


def create_shared_game_history() -> str:
    """Create initial shared game history."""

    # Create the markdown content
    content = """# Game History

This file tracks the state of the Diplomacy game visible to all countries.

## Spring 1901

### Game Status
- **Season:** Spring 1901
- **Phase:** Diplomacy & Movement
- **Year:** 1901

### Current Board State

"""

    # Add all countries' positions
    for country, info in sorted(STARTING_POSITIONS.items()):
        content += f"""**{country}** ({len(info['centers'])} centers, {len(info['units'])} units)
- Supply Centers: {', '.join(info['centers'])}
- Units: {', '.join(info['units'])}

"""

    content += """### Last Turn Results
No previous turn - the game is just beginning! All countries start in their home positions.

---

*To update this file after each turn:*
1. *Add a new section for the season (e.g., ## Fall 1901)*
2. *Include orders given and adjudication results*
3. *Update the Current Board State*
4. *Note any significant events (eliminations, stalemate lines, etc.)*

"""

    return content


def main():
    print("Initializing shared game_history.md with standard Diplomacy starting positions...\n")

    game_history_file = Path("game_history.md")
    content = create_shared_game_history()
    game_history_file.write_text(content)

    print(f"✓ Created {game_history_file}")
    print("\n✓ Game history initialized!")
    print("\nNext steps:")
    print("  1. Make sure your .env file has your Gemini API key")
    print("  2. Run: python diplomacy.py status")
    print("  3. Start the game: python diplomacy.py france")


if __name__ == "__main__":
    main()

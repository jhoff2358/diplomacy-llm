"""
Context loader for Diplomacy agents.
Loads and formats all context needed for a country to make decisions.
"""

from pathlib import Path
from typing import Dict, List
import yaml


class ContextLoader:
    """Loads context for a specific country from their files."""

    def __init__(self, country: str, config_path: str = "config.yaml"):
        self.country = country

        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Set up paths
        self.country_dir = Path(self.config['paths']['data_dir']) / country
        self.conversations_dir = Path(self.config['paths']['data_dir']) / self.config['paths']['shared_conversations_dir']  # Shared folder
        self.game_history_file = Path(self.config['paths']['data_dir']) / self.config['paths']['shared_game_history']  # Shared file
        self.plans_file = self.country_dir / self.config['paths']['plans_file']
        self.notes_file = self.country_dir / self.config['paths']['notes_file']

    def load_game_history(self) -> str:
        """Load the game history file."""
        if self.game_history_file.exists():
            return self.game_history_file.read_text()
        return "# Game History\n\nNo game history yet. The game is just beginning!"

    def load_plans(self) -> str:
        """Load the plans file."""
        if self.plans_file.exists():
            content = self.plans_file.read_text().strip()
            return content if content else "No plans yet."
        return "No plans yet."

    def load_notes(self) -> str:
        """Load the notes file."""
        if self.notes_file.exists():
            content = self.notes_file.read_text().strip()
            return content if content else "No notes yet."
        return "No notes yet."

    def load_conversations(self) -> Dict[str, str]:
        """Load all conversation files where this country is a participant."""
        conversations = {}

        if not self.conversations_dir.exists():
            return conversations

        # Load any conversation file that contains this country's name
        for conv_file in self.conversations_dir.glob("*.md"):
            # Parse filename like "Austria-France.md" or "England-France-Germany.md"
            participants = conv_file.stem.split('-')

            # Only load if this country is a participant
            if self.country in participants:
                # Use the full participant list as the key (minus this country)
                other_participants = [p for p in participants if p != self.country]
                if other_participants:
                    label = '-'.join(other_participants)
                    conversations[label] = conv_file.read_text()

        return conversations

    def format_context(self) -> str:
        """Format all context into a single prompt for the LLM."""

        game_history = self.load_game_history()
        plans = self.load_plans()
        notes = self.load_notes()
        conversations = self.load_conversations()

        # Build the context prompt with new format
        context = f"""Welcome to the Game of Diplomacy! Make friends and foes as you lie and scheme your way to victory!

You are playing as {self.country}.

Attached is your current **conversation history** and **game history**, along with your **notes** and **plans**.

# GAME HISTORY
{game_history}

# YOUR PLANS
{plans}

# YOUR NOTES
{notes}

# CONVERSATION HISTORY
"""

        if conversations:
            for participants, conv_text in sorted(conversations.items()):
                context += f"\n## Conversation with {participants}\n{conv_text}\n"
        else:
            context += "\nNo conversations yet. You may want to reach out to other countries!\n"

        return context

    def get_conversation_filename(self, participants: List[str]) -> str:
        """Generate standardized conversation filename from participant list."""
        # Include self.country in the list and sort alphabetically
        all_participants = sorted(set(participants + [self.country]))
        return '-'.join(all_participants) + '.md'

    def get_conversation_file(self, participants: List[str]) -> Path:
        """Get the path to a conversation file."""
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        filename = self.get_conversation_filename(participants)
        return self.conversations_dir / filename

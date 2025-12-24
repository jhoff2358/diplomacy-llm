"""
Context loader for Diplomacy agents.
Loads and formats all context needed for a country to make decisions.
Supports both classic and fog of war modes.
"""

from pathlib import Path
from typing import Dict, List
import yaml

from utils import is_fow, is_gunboat, get_data_dir, get_country_dir, get_conversations_dir


class ContextLoader:
    """Loads context for a specific country from their files."""

    def __init__(self, country: str, config_path: str = "config.yaml"):
        self.country = country

        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Get conversation line limit from config (0 or negative = no limit)
        limit = self.config.get('context', {}).get('conversation_line_limit', 0)
        self.conversation_line_limit = limit if limit > 0 else None

        # Set up paths using utils
        self.data_dir = get_data_dir(self.config)
        self.country_dir = get_country_dir(self.config, country)
        self.conversations_dir = get_conversations_dir(self.config)

        # Per-country files
        self.game_history_file = self.country_dir / self.config['paths']['game_history']
        self.game_state_file = self.country_dir / self.config['paths']['game_state']

    def load_game_history(self) -> str:
        """Load game history. FoW uses per-country files; classic/gunboat use shared."""
        if is_fow(self.config):
            path = self.game_history_file  # Per-country file
        else:
            path = self.data_dir / self.config['paths']['game_history']  # Shared file

        if path.exists():
            return path.read_text()
        return "# Game History\n\nNo game history yet. The game is just beginning!"

    def load_game_state(self) -> str:
        """Load game state. FoW uses per-country files; classic/gunboat use shared."""
        if is_fow(self.config):
            path = self.game_state_file  # Per-country file
        else:
            path = self.data_dir / self.config['paths']['game_state']  # Shared file

        if path.exists():
            return path.read_text()
        return "# Game State\n\nNo game state yet."

    def load_country_files(self) -> Dict[str, str]:
        """Load all .md files from the country directory except game_history and game_state."""
        files = {}

        if not self.country_dir.exists():
            return files

        reserved_files = {
            self.config['paths']['game_history'],
            self.config['paths']['game_state']
        }

        for md_file in self.country_dir.glob("*.md"):
            if md_file.name not in reserved_files:
                content = md_file.read_text().strip()
                if content:  # Only include non-empty files
                    files[md_file.name] = content

        return files

    def load_conversations(self) -> Dict[str, str]:
        """Load all conversation files where this country is a participant."""
        conversations = {}

        # No conversations in gunboat mode
        if is_gunboat(self.config):
            return conversations

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
                    content = conv_file.read_text()

                    # Apply line limit if set (take last N lines)
                    if self.conversation_line_limit is not None:
                        lines = content.split('\n')
                        if len(lines) > self.conversation_line_limit:
                            content = f"[... earlier messages truncated ...]\n\n" + '\n'.join(lines[-self.conversation_line_limit:])

                    conversations[label] = content

        return conversations

    def format_context(self) -> str:
        """Format all context into a single prompt for the LLM."""

        game_state = self.load_game_state()
        game_history = self.load_game_history()
        country_files = self.load_country_files()
        conversations = self.load_conversations()

        # Build intro and rules based on mode
        if is_gunboat(self.config):
            intro = f"You are playing as {self.country} in a game of GUNBOAT Diplomacy."
            rules_section = """
**GUNBOAT RULES:**
- No communication with other countries is allowed
- You can only analyze the board and submit orders
- Use your files to track your strategic thinking
"""
        elif is_fow(self.config):
            intro = f"You are playing as {self.country} in a game of Fog of War Diplomacy."
            rules_section = """
**FOG OF WAR RULES:**
- You can only see territories adjacent to your HOME supply centers and units
- Your game_state shows what you currently see
- Your game_history shows orders/results you witnessed
- You can only MESSAGE countries listed in your game_state
- You can READ all conversation history

**IMPORTANT:** If a territory is listed in your game_state without a unit, it is CONFIRMED EMPTY. You have full visibility there - no need to speculate about hidden units.
"""
        else:
            intro = f"You are playing as {self.country} in a game of Diplomacy."
            rules_section = ""

        # Build the context prompt
        context = f"""{intro}
{rules_section}
**FILE MANAGEMENT:**
You can create and manage your own files to organize your thoughts however you like.
<FILE name="filename.md" mode="append|edit|delete">content</FILE>

- mode="append" (default): Add to end of file, or create new file
- mode="edit": Replace entire file contents
- mode="delete": Remove file

Recommended: Use append during the season, edit/delete during reflect phase to reorganize.
"""

        # Only show messaging instructions if not gunboat
        if not is_gunboat(self.config):
            context += """
**MESSAGING:**
<MESSAGE to="Country">Your message</MESSAGE>
"""

        context += f"""
---

# YOUR CURRENT STATE
{game_state}

---

# YOUR GAME HISTORY
{game_history}

---

# YOUR FILES
"""

        if country_files:
            for filename, content in sorted(country_files.items()):
                context += f"\n## {filename}\n{content}\n"
        else:
            context += "\nNo files yet. Create some to organize your thoughts!\n"

        # Only show conversation section if not gunboat
        if not is_gunboat(self.config):
            context += "\n---\n\n# CONVERSATION HISTORY\n"

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
        """Get the path to a conversation file. Not used in gunboat mode."""
        if not is_gunboat(self.config):
            self.conversations_dir.mkdir(parents=True, exist_ok=True)
        filename = self.get_conversation_filename(participants)
        return self.conversations_dir / filename

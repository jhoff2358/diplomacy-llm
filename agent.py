"""
Agent manager for Diplomacy countries.
Manages Gemini chat sessions and handles country actions.
Supports both classic and fog of war modes.
"""

import os
import re
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, TypeVar
import google.generativeai as genai
from dotenv import load_dotenv
import yaml

from context import ContextLoader

T = TypeVar('T')


# Files that cannot be modified by the agent
RESERVED_FILES = {'game_history.md', 'game_state.md'}


class DiplomacyAgent:
    """Manages a single country's LLM session and actions."""

    def __init__(self, country: str, config_path: str = "config.yaml"):
        self.country = country

        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Load API key
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config['model'])
        self.chat = None  # Will be initialized when needed

        # Context loader
        self.context_loader = ContextLoader(country, config_path)

        # Country directory
        self.country_dir = Path(self.config['paths']['data_dir']) / country

        # Retry settings
        self.max_retries = self.config.get('api', {}).get('max_retries', 2)

    def _retry(self, fn: Callable[[], T], description: str = "API call") -> T:
        """Retry a function up to max_retries times on failure."""
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return fn()
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                    print(f"  ! {description} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    print(f"    Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        raise last_error

    def is_fow(self) -> bool:
        """Check if fog of war mode is enabled."""
        return self.config.get('features', {}).get('fog_of_war', False)

    def sync_shared_files(self):
        """In classic mode, copy root game_state.md and game_history.md to country folder."""
        if self.is_fow():
            return  # FoW mode uses per-country files directly

        self.country_dir.mkdir(parents=True, exist_ok=True)
        data_dir = Path(self.config['paths']['data_dir'])

        # Copy shared game_state.md
        shared_state = data_dir / 'game_state.md'
        if shared_state.exists():
            country_state = self.country_dir / self.config['paths']['game_state']
            shutil.copy(shared_state, country_state)

        # Copy shared game_history.md
        shared_history = data_dir / 'game_history.md'
        if shared_history.exists():
            country_history = self.country_dir / self.config['paths']['game_history']
            shutil.copy(shared_history, country_history)

    def initialize_session(self):
        """Initialize or reset the chat session with current context."""
        context = self.context_loader.format_context()

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        # Send initial context as system-like message
        initial_prompt = f"""{context}

---

What would you like to do this turn? You may send messages, update your notes, or both.

If you have nothing to add right now, simply respond with **PASS** - there's no need to act on every turn."""

        return initial_prompt

    def initialize_reflect_session(self):
        """Initialize a reflection session focused on strategic thinking."""
        context = self.context_loader.format_context()

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        initial_prompt = f"""You are playing as {self.country}. This is a STRATEGIC REFLECTION session.

A year has passed. This is your opportunity to step back and think about the big picture before the next year begins.

**PURPOSE:**
- Review what happened this past year
- Analyze your current position and trajectory
- Evaluate which alliances are serving you and which are not
- Plan your approach for the coming year
- Clean up and reorganize your notes and files

**FILE MANAGEMENT:**
Use this time to consolidate your thinking. You can create new files or manage existing ones:
- Append new insights (or create a new file)
- Edit files to restructure or condense them
- Delete files that are no longer relevant

<FILE name="filename.md" mode="append|edit|delete">content</FILE>

**NO MESSAGING:** This is private reflection time. Messages cannot be sent during this session.

---

{context}

---

Reflect on the past year and prepare for the next:"""

        return initial_prompt

    def parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse XML-style tags from LLM response.

        Extracts MESSAGE and FILE tags from the response text.

        MESSAGE format: <MESSAGE to="Country1, Country2">content</MESSAGE>
        FILE format: <FILE name="filename.md" mode="append|edit|delete">content</FILE>

        Returns:
            Dict with 'messages' and 'files' lists containing parsed actions.
        """
        actions = {
            'messages': [],
            'files': []
        }

        # Parse MESSAGE tags
        message_pattern = r'<MESSAGE\s+to="([^"]+)"\s*>(.*?)</MESSAGE>'
        for match in re.finditer(message_pattern, response_text, re.DOTALL | re.IGNORECASE):
            recipients = match.group(1)
            message_content = match.group(2).strip()

            # Parse recipient list
            recipient_list = [r.strip() for r in recipients.split(',')]

            actions['messages'].append({
                'to': recipient_list,
                'content': message_content
            })

        # Parse FILE tags
        # Supports: <FILE name="x.md">, <FILE name="x.md" mode="append">, etc.
        file_pattern = r'<FILE\s+name="([^"]+)"(?:\s+mode="([^"]+)")?\s*>(.*?)</FILE>'
        for match in re.finditer(file_pattern, response_text, re.DOTALL | re.IGNORECASE):
            filename = match.group(1)
            mode = match.group(2) or 'append'  # Default to append
            content = match.group(3).strip()

            actions['files'].append({
                'name': filename,
                'mode': mode.lower(),
                'content': content
            })

        return actions

    def execute_actions(self, actions: Dict[str, Any], season: str = None):
        """Execute parsed actions."""
        # Send messages
        for msg in actions['messages']:
            self.send_message(msg['to'], msg['content'], season)

        # Handle file operations
        for file_op in actions['files']:
            self.write_file(file_op['name'], file_op['content'], file_op['mode'])

    def take_turn(self, season: str = None) -> Tuple[str, Dict[str, Any]]:
        """Take a turn: show context and get LLM response."""
        self.sync_shared_files()  # Copy shared files in classic mode
        prompt = self.initialize_session()

        # Get response from LLM with retry
        response = self._retry(
            lambda: self.chat.send_message(prompt),
            f"{self.country} turn"
        )
        response_text = response.text

        # Parse actions
        actions = self.parse_response(response_text)

        return response_text, actions

    def take_reflect_turn(self) -> Tuple[str, Dict[str, Any]]:
        """Take a reflection turn focused on strategic thinking."""
        self.sync_shared_files()  # Copy shared files in classic mode
        prompt = self.initialize_reflect_session()

        # Get response from LLM with retry
        response = self._retry(
            lambda: self.chat.send_message(prompt),
            f"{self.country} reflect"
        )
        response_text = response.text

        # Parse actions but filter out messages (reflection is private)
        actions = self.parse_response(response_text)
        actions['messages'] = []  # No messaging during reflection

        return response_text, actions

    def send_message(self, recipients: List[str], message: str, season: str = None):
        """Send a message to one or more countries."""
        # Get conversation file for these participants
        conv_file = self.context_loader.get_conversation_file(recipients)

        # Format the message with season header if needed
        season_header = f"\n## {season}\n" if season else "\n"

        # Format the message
        message_text = f"{season_header}**{self.country}:** {message}\n\n"

        # Append to conversation file
        with open(conv_file, 'a') as f:
            f.write(message_text)

        # Format recipients for display
        recipients_str = ', '.join(recipients)
        print(f"  ✓ Message sent to {recipients_str}")

    def write_file(self, filename: str, content: str, mode: str):
        """Write/append/delete a file in the country directory."""

        # Validate filename
        if not filename.endswith('.md'):
            print(f"  ✗ Invalid filename '{filename}' - must end with .md")
            return

        if filename in RESERVED_FILES:
            print(f"  ✗ Cannot modify reserved file '{filename}'")
            return

        file_path = self.country_dir / filename

        if mode == 'delete':
            if file_path.exists():
                file_path.unlink()
                print(f"  ✓ Deleted {filename}")
            else:
                print(f"  ! File {filename} does not exist")

        elif mode == 'edit':
            file_path.write_text(content)
            print(f"  ✓ Replaced {filename}")

        elif mode == 'append':
            # Append with newlines
            if file_path.exists():
                existing = file_path.read_text()
                if existing and not existing.endswith('\n'):
                    existing += '\n'
                file_path.write_text(existing + content + '\n')
            else:
                file_path.write_text(content + '\n')
            print(f"  ✓ Appended to {filename}")

        else:
            print(f"  ✗ Unknown mode '{mode}' - use append, edit, or delete")

    def check_readiness(self, model_override: str = None) -> str:
        """Ask the agent if they're ready to submit orders or need more discussion.

        Args:
            model_override: Optional model name to use instead of config default.
                          Defaults to cheap_model from config to save costs.
        """
        self.sync_shared_files()  # Copy shared files in classic mode
        context = self.context_loader.format_context()

        # Use override model if provided, otherwise use cheap model from config
        if model_override:
            model = genai.GenerativeModel(model_override)
        else:
            model = genai.GenerativeModel(self.config['cheap_model'])

        # Create a fresh chat for readiness check
        chat = model.start_chat(history=[])

        prompt = f"""{context}

---

**READINESS CHECK**

Before we collect orders, I need to check if you're ready. Consider:

1. Are there any unanswered questions in your conversations that could affect your strategy?
2. Are there pending negotiations or proposals you're waiting on?
3. Do you have enough information to confidently submit orders?

It's perfectly fine to request more discussion time. Don't just say READY to be agreeable - if there's genuine uncertainty or an important conversation that hasn't concluded, say so.

Respond with:
- **READY** - if you have enough clarity to submit orders
- **NEED MORE DISCUSSION** - if there are unresolved questions or pending negotiations

Then briefly explain why (1-2 sentences).

Do not use XML tags. Just answer directly."""

        response = self._retry(
            lambda: chat.send_message(prompt),
            f"{self.country} readiness check"
        )
        return response.text.strip()

    def get_orders(self) -> str:
        """Ask the agent for their orders for this phase.
        Uses cheap model from config to save costs.
        """
        self.sync_shared_files()  # Copy shared files in classic mode
        context = self.context_loader.format_context()

        # Create a fresh chat for orders using cheap model
        cheap_model = genai.GenerativeModel(self.config['cheap_model'])
        chat = cheap_model.start_chat(history=[])

        prompt = f"""{context}

---

**ORDERS PHASE**

It is time to submit your orders for this phase. Output ONLY your orders, one per line, using standard Diplomacy notation.

Examples:
- A Par - Bur (Army Paris moves to Burgundy)
- F Lon - NTH (Fleet London moves to North Sea)
- A Mun S A Par - Bur (Army Munich supports Army Paris to Burgundy)
- F NTH C A Lon - Bel (Fleet North Sea convoys Army London to Belgium)
- A Vie H (Army Vienna holds)

Do NOT include any messages, file operations, or other commentary. Output only your orders."""

        response = self._retry(
            lambda: chat.send_message(prompt),
            f"{self.country} orders"
        )
        return response.text

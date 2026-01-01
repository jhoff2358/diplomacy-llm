"""
Agent manager for Diplomacy countries.
Manages Gemini chat sessions and handles country actions.
Supports classic, fog of war, gunboat modes (and combinations).
"""

import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, TypeVar
import google.generativeai as genai
from dotenv import load_dotenv
import yaml

from .context import ContextLoader
from .mode_loader import ModeLoader
from .utils import get_country_dir

T = TypeVar('T')


# Files that cannot be modified by the agent
RESERVED_FILES = {'game_history.md', 'game_state.md'}


class DiplomacyAgent:
    """Manages a single country's LLM session and actions."""

    def __init__(self, country: str, config_path: str = "config.yaml", use_cheap_model: bool = False):
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
        model_name = self.config.get('cheap_model', self.config['model']) if use_cheap_model else self.config['model']
        self.model = genai.GenerativeModel(model_name)
        self.chat = None  # Will be initialized when needed

        # Context loader
        self.context_loader = ContextLoader(country, config_path)

        # Country directory - create on init
        self.country_dir = get_country_dir(self.config, country)
        self.country_dir.mkdir(parents=True, exist_ok=True)

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

    def initialize_session(self):
        """Initialize or reset the chat session with current context."""
        context = self.context_loader.format_context()
        mode_loader = ModeLoader(self.config)

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        # Load turn prompt from mode templates
        return mode_loader.get_prompt("turn", {
            "context": context,
            "country": self.country
        })

    def initialize_reflect_session(self, wipe_void: bool = False):
        """Initialize a reflection session focused on strategic thinking."""
        context = self.context_loader.format_context()
        mode_loader = ModeLoader(self.config)

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        # Load reflect prompt from mode templates
        return mode_loader.get_prompt("reflect", {
            "context": context,
            "country": self.country,
            "wipe_void": wipe_void
        })

    def initialize_react_session(self):
        """Initialize a react session for quick reactions to board state."""
        context = self.context_loader.format_context()
        mode_loader = ModeLoader(self.config)

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        # Load react prompt from mode templates
        return mode_loader.get_prompt("react", {
            "context": context,
            "country": self.country
        })

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

        # Parse MESSAGE tags (skip if messaging disabled)
        mode_loader = ModeLoader(self.config)
        if mode_loader.is_feature_enabled("messaging_instructions"):
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

    def execute_actions(self, actions: Dict[str, Any], season: str = None,
                        restrict_files: list = None, append_only_files: list = None):
        """Execute parsed actions.

        Args:
            actions: Parsed actions dict with 'messages' and 'files' lists
            season: Current season for message headers
            restrict_files: If provided, only allow writes to these files (e.g., ['void.md', 'orders.md'])
            append_only_files: If provided, force append mode for these files (e.g., ['void.md'])
        """
        # Send messages
        for msg in actions['messages']:
            self.send_message(msg['to'], msg['content'], season)

        # Handle file operations
        for file_op in actions['files']:
            filename = file_op['name']
            mode = file_op['mode']

            # Normalize filename for comparison
            normalized = filename.lower()
            if not normalized.endswith('.md'):
                normalized += '.md'

            # Enforce file restriction if specified
            if restrict_files is not None:
                allowed = [f.lower() for f in restrict_files]
                if normalized not in allowed:
                    print(f"  ! Skipped {filename} (only {', '.join(restrict_files)} allowed in this phase)")
                    continue

            # Enforce append-only for specified files
            if append_only_files is not None:
                append_only = [f.lower() for f in append_only_files]
                if normalized in append_only and mode != 'append':
                    print(f"  ! Forcing append mode for {filename} (append-only in this phase)")
                    mode = 'append'

            self.write_file(filename, file_op['content'], mode)

    def take_turn(self, season: str = None) -> Tuple[str, Dict[str, Any]]:
        """Take a turn: show context and get LLM response."""
        prompt = self.initialize_session()

        # Get response from LLM with retry (includes .text access which can also fail)
        def get_response():
            response = self.chat.send_message(prompt)
            return response.text

        response_text = self._retry(get_response, f"{self.country} turn")

        # Parse actions
        actions = self.parse_response(response_text)

        return response_text, actions

    def take_reflect_turn(self, wipe_void: bool = False) -> Tuple[str, Dict[str, Any]]:
        """Take a reflection turn focused on strategic thinking.

        Args:
            wipe_void: If True, tell agent their void.md will be cleared after response
        """
        prompt = self.initialize_reflect_session(wipe_void=wipe_void)

        # Get response from LLM with retry (includes .text access which can also fail)
        def get_response():
            response = self.chat.send_message(prompt)
            return response.text

        response_text = self._retry(get_response, f"{self.country} reflect")

        # Parse actions but filter out messages (reflection is private)
        actions = self.parse_response(response_text)
        actions['messages'] = []  # No messaging during reflection

        return response_text, actions

    def take_react_turn(self) -> Tuple[str, Dict[str, Any]]:
        """Take a react turn for quick reactions to board state.

        React turns can only write to void.md and send messages.
        """
        prompt = self.initialize_react_session()

        # Get response from LLM with retry
        def get_response():
            response = self.chat.send_message(prompt)
            return response.text

        response_text = self._retry(get_response, f"{self.country} react")

        # Parse actions
        actions = self.parse_response(response_text)

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

        # Auto-fix filename extension if not .md
        if not filename.endswith('.md'):
            original = filename
            # Replace existing extension or add .md
            if '.' in filename:
                filename = filename.rsplit('.', 1)[0] + '.md'
            else:
                filename = filename + '.md'
            print(f"  ! Renamed '{original}' -> '{filename}'")

        # Redirect reserved filenames to country-specific versions
        if filename in RESERVED_FILES:
            base = filename.rsplit('.', 1)[0]  # e.g., "game_history"
            filename = f"{base}_{self.country.lower()}.md"
            print(f"  ! Reserved filename, redirecting to {filename}")

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

    def get_orders(self) -> str:
        """Ask the agent for their orders for this phase.

        With messaging enabled: Returns orders or "PASS" if more diplomacy time is needed.
        Without messaging: Orders are mandatory, no PASS option.
        Also processes any file operations in the response.
        """
        context = self.context_loader.format_context()
        mode_loader = ModeLoader(self.config)

        chat = self.model.start_chat(history=[])

        # Load orders prompt from mode templates
        prompt = mode_loader.get_prompt("orders", {
            "context": context,
            "country": self.country
        })

        def get_response():
            response = chat.send_message(prompt)
            return response.text

        response_text = self._retry(get_response, f"{self.country} orders")

        # Parse and execute any file operations (but not messages during orders phase)
        actions = self.parse_response(response_text)
        for file_op in actions['files']:
            self.write_file(file_op['name'], file_op['content'], file_op['mode'])

        return response_text

    def query(self, question: str) -> str:
        """Ask the agent a direct question (meta-communication from GM).

        No messages or file operations - just a direct response.
        """
        context = self.context_loader.format_context()

        chat = self.model.start_chat(history=[])

        prompt = f"""{context}

---

**GM QUERY**

The Game Master has a question for you. This is meta-communication - do not send any messages or update any files. Just respond directly.

Question: {question}"""

        def get_response():
            response = chat.send_message(prompt)
            return response.text

        return self._retry(get_response, f"{self.country} query")

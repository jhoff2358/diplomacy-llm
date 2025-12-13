"""
Agent manager for Fog of War Diplomacy countries.
Manages Gemini chat sessions and handles country actions.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import google.generativeai as genai
from dotenv import load_dotenv
import yaml

from context import ContextLoader


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

    def initialize_session(self):
        """Initialize or reset the chat session with current context."""
        context = self.context_loader.format_context()

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        # Send initial context as system-like message
        initial_prompt = f"""{context}

---

What would you like to do this turn?"""

        return initial_prompt

    def initialize_reflect_session(self):
        """Initialize a reflection session focused on strategic thinking."""
        context = self.context_loader.format_context()

        # Start new chat with full context
        self.chat = self.model.start_chat(history=[])

        initial_prompt = f"""You are playing as {self.country}. This is a STRATEGIC REFLECTION session.

Take time to:
1. Analyze your current position and trajectory
2. Evaluate your alliances and diplomatic relationships
3. Plan your next 2-3 seasons
4. Reorganize your files if needed (use mode="edit" or mode="delete")

This is a time for thinking and planning, not diplomacy.

---

{context}

---

Reflect on your strategy:"""

        return initial_prompt

    def parse_response(self, response_text: str) -> Dict[str, any]:
        """Parse XML-style tags from LLM response."""
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

    def execute_actions(self, actions: Dict[str, any], season: str = None):
        """Execute parsed actions."""
        # Send messages
        for msg in actions['messages']:
            self.send_message(msg['to'], msg['content'], season)

        # Handle file operations
        for file_op in actions['files']:
            self.write_file(file_op['name'], file_op['content'], file_op['mode'])

    def take_turn(self, season: str = None) -> Tuple[str, Dict[str, any]]:
        """Take a turn: show context and get LLM response."""
        prompt = self.initialize_session()

        # Get response from LLM
        response = self.chat.send_message(prompt)
        response_text = response.text

        # Parse actions
        actions = self.parse_response(response_text)

        return response_text, actions

    def take_reflect_turn(self) -> Tuple[str, Dict[str, any]]:
        """Take a reflection turn focused on strategic thinking."""
        prompt = self.initialize_reflect_session()

        # Get response from LLM
        response = self.chat.send_message(prompt)
        response_text = response.text

        # Parse actions (only file operations expected, but parse all)
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
        context = self.context_loader.format_context()

        # Use override model if provided, otherwise use cheap model from config
        if model_override:
            model = genai.GenerativeModel(model_override)
        else:
            model = genai.GenerativeModel(self.config['cheap_model'])

        # Create a fresh chat for readiness check
        chat = model.start_chat(history=[])

        prompt = f"""{context}

Before we collect orders, I want to check: Are you ready to submit orders for this phase, or do you feel there is more diplomatic discussion needed first?

Please respond briefly with:
1. Your readiness status (READY or NEED MORE DISCUSSION)
2. A short 1-2 sentence explanation

Do not use XML tags for this response, just answer directly."""

        response = chat.send_message(prompt)
        return response.text.strip()

    def get_orders(self) -> str:
        """Ask the agent for their orders for this phase.
        Uses cheap model from config to save costs.
        """
        context = self.context_loader.format_context()

        # Create a fresh chat for orders using cheap model
        cheap_model = genai.GenerativeModel(self.config['cheap_model'])
        chat = cheap_model.start_chat(history=[])

        prompt = f"""{context}

It is time to submit your orders for this phase.

Please provide your orders for all your units. Be specific and clear about what each unit should do.

Your orders:"""

        response = chat.send_message(prompt)
        return response.text


def get_all_countries(config_path: str = "config.yaml") -> List[str]:
    """Get list of all countries from config."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['countries']

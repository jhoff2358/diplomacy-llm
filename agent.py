"""
Agent manager for Diplomacy countries.
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

Each turn, you may:
- Send a message to one or more countries
- Update your notes and/or plans

To send a message, use this format:
<MESSAGE to="Country">
Your message here
</MESSAGE>

For group messages, separate countries with commas:
<MESSAGE to="Austria,Germany">
Your group message here
</MESSAGE>

To update your plans, use:
<PLANS>
Your complete updated plans here (this will replace the entire file)
</PLANS>

To update your notes, use:
<NOTES>
Your complete updated notes here (this will replace the entire file)
</NOTES>

You can include multiple messages and update both plans and notes in a single turn.
If you don't want to take any action this turn, just say so without using any tags.

What would you like to do this turn?"""

        return initial_prompt

    def parse_response(self, response_text: str) -> Dict[str, any]:
        """Parse XML-style tags from LLM response."""
        actions = {
            'messages': [],
            'plans': None,
            'notes': None
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

        # Parse PLANS tag
        plans_pattern = r'<PLANS\s*>(.*?)</PLANS>'
        plans_match = re.search(plans_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if plans_match:
            actions['plans'] = plans_match.group(1).strip()

        # Parse NOTES tag
        notes_pattern = r'<NOTES\s*>(.*?)</NOTES>'
        notes_match = re.search(notes_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if notes_match:
            actions['notes'] = notes_match.group(1).strip()

        return actions

    def execute_actions(self, actions: Dict[str, any], season: str = None):
        """Execute parsed actions."""
        # Send messages
        for msg in actions['messages']:
            self.send_message(msg['to'], msg['content'], season)

        # Update plans
        if actions['plans'] is not None:
            self.update_plans(actions['plans'])

        # Update notes
        if actions['notes'] is not None:
            self.update_notes(actions['notes'])

    def take_turn(self, season: str = None) -> Tuple[str, Dict[str, any]]:
        """Take a turn: show context and get LLM response."""
        prompt = self.initialize_session()

        # Get response from LLM
        response = self.chat.send_message(prompt)
        response_text = response.text

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

    def update_plans(self, new_plans: str):
        """Update the plans file."""
        plans_file = self.country_dir / self.config['paths']['plans_file']
        plans_file.write_text(new_plans)
        print(f"  ✓ Plans updated")

    def update_notes(self, new_notes: str):
        """Update the notes file."""
        notes_file = self.country_dir / self.config['paths']['notes_file']
        notes_file.write_text(new_notes)
        print(f"  ✓ Notes updated")

    def check_readiness(self, model_override: str = None) -> str:
        """Ask the agent if they're ready to submit orders or need more discussion.

        Args:
            model_override: Optional model name to use instead of config default.
                          Use a cheaper model like 'gemini-flash-latest' to save costs.
        """
        context = self.context_loader.format_context()

        # Use override model if provided, otherwise use default
        if model_override:
            model = genai.GenerativeModel(model_override)
        else:
            model = self.model

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
        """Ask the agent for their orders for this phase."""
        context = self.context_loader.format_context()

        # Create a fresh chat for orders
        chat = self.model.start_chat(history=[])

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

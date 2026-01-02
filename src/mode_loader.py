"""
Mode-specific prompt loader for Diplomacy LLM.
Loads and combines prompts from modes/ folder based on active feature flags.
Supports stacking modes (e.g., gunboat + fog_of_war).

Hybrid approach:
- Reusable blocks (concatenate): rules, file_management, order_format
- Complete templates (override): turn, reflect, orders, context_header
- Templates can reference blocks via {block:name} syntax
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class ModeLoader:
    """Loads and combines mode-specific prompts from external files."""

    MODES_DIR = Path(__file__).parent.parent / "modes"

    # Prompts that should concatenate (show all active) vs override (last wins)
    CONCAT_PROMPTS = {"rules", "file_management", "order_format"}

    # Map block reference names to prompt file names
    BLOCK_MAPPING = {
        "rules": "rules",
        "file_management": "file_management",
        "order_format": "order_format",
        "messaging": "messaging_instructions",
    }

    def __init__(self, config: dict):
        self.config = config
        self._cache: Dict[str, str] = {}
        self._active_modes = self._determine_active_modes()

    def _determine_active_modes(self) -> List[str]:
        """Determine which modes are active, in priority order.

        Order matters for override behavior: later modes override earlier ones.
        Base is always first, then modes in a defined order.
        """
        modes = ["base"]  # Always load base first

        features = self.config.get('features', {})

        # Add modes in priority order (later = higher priority for overrides)
        if features.get('fog_of_war', False):
            modes.append("fow")
        if features.get('gunboat', False):
            modes.append("gunboat")
        if features.get('imperial', False):
            modes.append("imperial")
        if features.get('chess', False):
            modes.append("chess")

        return modes

    def _load_prompt(self, mode_name: str, prompt_name: str) -> Optional[str]:
        """Load a single prompt file from a mode folder.

        Returns None if the file doesn't exist.
        Returns empty string if a .disable file exists.
        """
        mode_dir = self.MODES_DIR / mode_name

        # Check for .disable file (signals this prompt should be suppressed)
        disable_file = mode_dir / f"{prompt_name}.md.disable"
        if disable_file.exists():
            return ""  # Explicitly disabled

        # Try .md then .txt
        for ext in [".md", ".txt"]:
            prompt_file = mode_dir / f"{prompt_name}{ext}"
            if prompt_file.exists():
                return prompt_file.read_text().strip()

        return None  # File doesn't exist

    def get_prompt(self, prompt_name: str, variables: Optional[Dict[str, str]] = None) -> str:
        """Load a prompt by name, combining active mode overlays.

        Args:
            prompt_name: Name of the prompt (e.g., "turn", "rules", "reflect")
            variables: Optional dict of template variables (e.g., {"country": "France"})

        Returns:
            The combined prompt text with blocks resolved and variables substituted.
        """
        cache_key = prompt_name

        if cache_key not in self._cache:
            if prompt_name in self.CONCAT_PROMPTS:
                content = self._load_concatenated(prompt_name)
            else:
                content = self._load_override(prompt_name)
            self._cache[cache_key] = content

        result = self._cache[cache_key]

        # Resolve block references: {block:name}
        result = self._resolve_blocks(result)

        # Inject filename variables from config (always available)
        if variables is None:
            variables = {}
        variables.setdefault('scratchpad_file', self.config['paths']['scratchpad'])
        variables.setdefault('orders_file', self.config['paths']['orders'])
        variables.setdefault('lessons_file', self.config['paths']['lessons'])

        # Process conditionals: {if:var}...{endif}
        result = self._process_conditionals(result, variables)

        # Substitute variables
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result

    def _process_conditionals(self, content: str, variables: Dict[str, str]) -> str:
        """Process {if:var}...{endif} conditional blocks.

        If var is truthy, include the content. Otherwise, remove the block entirely.
        """
        pattern = r'\{if:(\w+)\}(.*?)\{endif\}'

        def replacer(match):
            var_name = match.group(1)
            block_content = match.group(2)
            # Check if variable is truthy
            if variables.get(var_name):
                return block_content.strip()
            return ""

        return re.sub(pattern, replacer, content, flags=re.DOTALL)

    def _resolve_blocks(self, content: str) -> str:
        """Replace {block:name} references with loaded block content."""
        pattern = r'\{block:(\w+)\}'

        def replacer(match):
            block_name = match.group(1)
            prompt_name = self.BLOCK_MAPPING.get(block_name, block_name)

            # Check if feature is disabled
            if not self.is_feature_enabled(prompt_name):
                return ""

            # Load the block (bypass cache to avoid recursion issues)
            if prompt_name in self.CONCAT_PROMPTS:
                return self._load_concatenated(prompt_name)
            else:
                return self._load_override(prompt_name)

        return re.sub(pattern, replacer, content)

    def _load_override(self, prompt_name: str) -> str:
        """Load prompt with override behavior (last active mode wins)."""
        content = ""

        for mode in self._active_modes:
            loaded = self._load_prompt(mode, prompt_name)
            if loaded is not None:
                content = loaded  # Override with this mode's version

        return content

    def _load_concatenated(self, prompt_name: str) -> str:
        """Load prompt with concatenation behavior (all active modes combined)."""
        parts = []

        for mode in self._active_modes:
            loaded = self._load_prompt(mode, prompt_name)
            if loaded:  # Skip None and empty strings
                parts.append(loaded)

        return "\n\n".join(parts)

    def is_feature_enabled(self, prompt_name: str) -> bool:
        """Check if a prompt/feature is enabled (not disabled by any active mode).

        Useful for conditional logic like showing/hiding message sections.
        """
        for mode in reversed(self._active_modes):
            mode_dir = self.MODES_DIR / mode

            # Check for .disable marker
            if (mode_dir / f"{prompt_name}.md.disable").exists():
                return False

            # Check if prompt exists (enabled)
            if (mode_dir / f"{prompt_name}.md").exists() or \
               (mode_dir / f"{prompt_name}.txt").exists():
                return True

        return False

    def get_active_modes(self) -> List[str]:
        """Return list of active mode names."""
        return self._active_modes.copy()

    def clear_cache(self):
        """Clear the prompt cache. Useful for development/testing."""
        self._cache.clear()

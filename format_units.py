#!/usr/bin/env python3
"""
Format copy-pasted unit data from the browser into a clean list.

Usage:
    python format_units.py < raw_input.txt
    python format_units.py input.txt
"""

import sys
import re

COUNTRIES = {'Austria', 'England', 'France', 'Germany', 'Italy', 'Russia', 'Turkey'}


def format_units(text: str) -> str:
    """Parse raw copy-pasted unit data and format it nicely."""
    lines = [line.strip() for line in text.split('\n')]

    result = []
    current_country = None
    units = []

    for line in lines:
        if not line:
            continue

        # Check if this is a country name
        if line in COUNTRIES:
            # Save previous country's units
            if current_country and units:
                result.append(current_country)
                for unit in units:
                    result.append(f"- {unit}")
                result.append("")

            current_country = line
            units = []
        elif re.match(r'^[AF]\s+\w', line):
            # This is a unit (A xxx or F xxx)
            units.append(line)

    # Don't forget the last country
    if current_country and units:
        result.append(current_country)
        for unit in units:
            result.append(f"- {unit}")

    return '\n'.join(result)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    print(format_units(text))


if __name__ == "__main__":
    main()

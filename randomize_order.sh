#!/bin/bash
# Randomize and save the turn order for the current season

# Get all countries and shuffle them
countries=("Austria" "England" "France" "Germany" "Italy" "Russia" "Turkey")

# Shuffle using shuf (if available) or fall back to sort -R
if command -v shuf &> /dev/null; then
    shuffled=($(printf '%s\n' "${countries[@]}" | shuf))
else
    shuffled=($(printf '%s\n' "${countries[@]}" | sort -R))
fi

# Save to turn_order.txt
printf '%s\n' "${shuffled[@]}" > turn_order.txt

echo "=========================================="
echo "TURN ORDER RANDOMIZED"
echo "=========================================="
echo ""
echo "New turn order saved to turn_order.txt:"
echo ""
printf '%s\n' "${shuffled[@]}"
echo ""
echo "This order will be used by ./run_all_turns.sh"
echo "until you randomize again."
echo "=========================================="

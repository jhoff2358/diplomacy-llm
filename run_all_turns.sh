#!/bin/bash
# Run all 7 countries in randomized order, sequentially

# Activate venv
source venv/bin/activate

# Get all countries and shuffle them
countries=("Austria" "England" "France" "Germany" "Italy" "Russia" "Turkey")

# Shuffle using shuf (if available) or fall back to sort -R
if command -v shuf &> /dev/null; then
    shuffled=($(printf '%s\n' "${countries[@]}" | shuf))
else
    shuffled=($(printf '%s\n' "${countries[@]}" | sort -R))
fi

echo "=========================================="
echo "Running all countries in random order:"
echo "=========================================="
printf '%s\n' "${shuffled[@]}"
echo "=========================================="
echo ""

# Run each country sequentially
for country in "${shuffled[@]}"; do
    echo ""
    echo "######################################"
    echo "# Running: $country"
    echo "######################################"
    echo ""

    python3 diplomacy.py "$country"

    echo ""
    echo "✓ $country's turn complete"
    echo ""
done

echo ""
echo "=========================================="
echo "ALL TURNS COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  - Review conversations in conversations/"
echo "  - Check status: python3 diplomacy.py status"
echo "  - Collect orders: python3 diplomacy.py orders"

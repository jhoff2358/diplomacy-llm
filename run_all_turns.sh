#!/bin/bash
# Run all 7 countries in the saved turn order, sequentially

# Activate venv
source venv/bin/activate

# Check if turn_order.txt exists
if [ ! -f "turn_order.txt" ]; then
    echo "ERROR: turn_order.txt not found!"
    echo ""
    echo "Please run ./randomize_order.sh first to set the turn order."
    echo ""
    exit 1
fi

# Read turn order from file
mapfile -t turn_order < turn_order.txt

echo "=========================================="
echo "Running all countries in saved turn order:"
echo "=========================================="
printf '%s\n' "${turn_order[@]}"
echo "=========================================="
echo ""

# Run each country sequentially
for country in "${turn_order[@]}"; do
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

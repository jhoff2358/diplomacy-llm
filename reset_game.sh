#!/bin/bash
# Reset game: clear all conversations, plans, and notes
# Keeps: game_history.md, gamestate.json, config files

echo "=========================================="
echo "RESET GAME"
echo "=========================================="
echo ""
echo "This will DELETE:"
echo "  - All conversation files (conversations/*.md)"
echo "  - All country plans (*/plans.md)"
echo "  - All country notes (*/notes.md)"
echo ""
echo "This will KEEP:"
echo "  - gamestate.json"
echo "  - game_history.md"
echo "  - All config files"
echo ""
read -p "Are you sure you want to reset? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Reset cancelled."
    exit 0
fi

echo ""
echo "Resetting game..."
echo ""

# Clear conversations
if [ -d "conversations" ]; then
    rm -f conversations/*.md
    echo "✓ Cleared conversations/"
fi

# Clear plans and notes for each country
countries=("Austria" "England" "France" "Germany" "Italy" "Russia" "Turkey")

for country in "${countries[@]}"; do
    if [ -d "$country" ]; then
        rm -f "$country/plans.md"
        rm -f "$country/notes.md"
        echo "✓ Cleared $country/ (plans and notes)"
    fi
done

echo ""
echo "=========================================="
echo "RESET COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Update gamestate.json with new season"
echo "  2. Update game_history.md with starting positions"
echo "  3. Start playing: ./run_all_turns.sh"

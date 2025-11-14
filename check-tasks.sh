#!/bin/bash
# Check if tasks were saved

cd ~/Downloads/devdash

echo "🔍 Checking for saved tasks..."
echo ""

if [ -f .devdash_tasks.json ]; then
    echo "✅ Tasks file found!"
    echo ""
    echo "📄 Contents:"
    cat .devdash_tasks.json
    echo ""
else
    echo "ℹ️  No tasks file yet (add some tasks first)"
fi

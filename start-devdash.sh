#!/bin/bash
# Quick script to start DevDash

cd ~/Downloads/devdash
source venv/bin/activate
echo "🚀 Starting DevDash..."
echo ""
echo "📖 Quick Tips:"
echo "   ? - Show help"
echo "   q - Quit"
echo "   a - Add task"
echo "   f - Start focus timer"
echo ""
echo "Press any key to start..."
read -n 1
devdash

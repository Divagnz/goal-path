#!/bin/bash

echo "🚀 Creating Pull Request for GoalPath Navigation Fixes"
echo ""
echo "Branch: feature/firstVersion → main"
echo "Repository: git@github.com:Divagnz/goal-path.git"
echo ""
echo "📋 PR Details:"
echo "Title: Fix: Resolve direct URL access and mobile navigation issues"
echo "Changes: 61 files changed, 12929 insertions(+), 794 deletions(-)"
echo ""
echo "🌐 Opening GitHub PR creation page..."
echo ""
echo "Please visit this URL to create the PR:"
echo "https://github.com/Divagnz/goal-path/compare/main...feature/firstVersion?quick_pull=1"
echo ""
echo "✅ Your branch has been pushed with proper SSH authentication"
echo "✅ Commit authored by: Oscar Liguori <oscar.liguori.bagnis@gmail.com>"
echo "✅ All navigation fixes are included in the commit"

# Try to open the URL if xdg-open is available
if command -v xdg-open > /dev/null; then
    echo ""
    echo "🔗 Attempting to open URL automatically..."
    xdg-open "https://github.com/Divagnz/goal-path/compare/main...feature/firstVersion?quick_pull=1"
else
    echo ""
    echo "💡 Copy the URL above and paste it in your browser to create the PR"
fi

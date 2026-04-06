#!/bin/bash
# View recent reports

cd "$(dirname "$0")"

echo "📋 RECENT REPORTS"
echo "=================================================="

echo "📅 DAILY REPORTS:"
find reports/ -name "*.md" -type f | sort -r | head -10 | while read file; do
    filename=$(basename "$file")
    date=$(echo "$filename" | cut -d'.' -f1)
    size=$(stat -c %s "$file")
    lines=$(wc -l < "$file")
    echo "  📄 $date: $lines lines, $(($size/1024))KB"
done

echo ""
echo "📖 STRATEGY DOCUMENTATION:"
if [ -f "reports/strategy_details.md" ]; then
    echo "  ✅ Available: reports/strategy_details.md"
    echo "     $(wc -l < reports/strategy_details.md) lines of strategy explanations"
else
    echo "  ❌ Missing: Strategy documentation"
fi

echo ""
echo "🔍 VIEW OPTIONS:"
echo "  1. View latest report: cat reports/\$(ls -1t reports/*.md | head -1)"
echo "  2. View specific date: cat reports/YYYY-MM-DD.md"
echo "  3. View strategy docs: cat reports/strategy_details.md"

echo ""
echo "📊 LATEST REPORT PREVIEW:"
latest=$(ls -1t reports/*.md | head -1)
if [ -n "$latest" ]; then
    echo "----------------------------------------"
    head -20 "$latest"
    echo "..."
    echo "----------------------------------------"
    echo "Full report: $latest"
else
    echo "No reports found."
fi

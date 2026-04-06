#!/bin/bash
# Archive reports older than 7 days

cd "$(dirname "$0")"

echo "🗄️  ARCHIVING OLD REPORTS"
echo "=================================================="

mkdir -p reports/archive

# Move reports older than 7 days to archive
find reports/ -name "*.md" -type f -mtime +7 | while read file; do
    if [ "$file" != "reports/strategy_details.md" ]; then
        mv "$file" reports/archive/
        echo "  📦 Archived: $(basename "$file")"
    fi
done

echo ""
echo "📁 CURRENT REPORTS:"
find reports/ -name "*.md" -type f | grep -v archive | while read file; do
    echo "  📄 $(basename "$file")"
done

echo ""
echo "📦 ARCHIVE CONTENTS:"
find reports/archive/ -name "*.md" -type f | wc -l | xargs echo "  Total archived reports:"

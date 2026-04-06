#!/bin/bash
# Manual report generation

cd "$(dirname "$0")"

echo "📊 GENERATING MANUAL REPORT"
echo "=================================================="

python3 generate_report.py

echo ""
echo "📁 REPORT LOCATION:"
find reports/ -name "*.md" -type f | sort -r | head -5 | while read file; do
    echo "  - $file (created: $(stat -c %y "$file" | cut -d' ' -f1-2))"
done

echo ""
echo "🌐 DASHBOARDS:"
echo "  - Multi-Strategy: http://100.92.200.109:8502"
echo "  - Original: http://100.92.200.109:8501"
echo "  - WordPress: http://100.92.200.109:8080/paper-trading-dashboard/"

echo ""
echo "🔧 SYSTEM STATUS:"
./status_paper_trading_v2.sh | head -30

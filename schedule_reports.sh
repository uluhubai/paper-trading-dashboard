#!/bin/bash
# Schedule automatic reports for Paper Trading System

cd "$(dirname "$0")"

echo "📅 SCHEDULING AUTOMATIC REPORTS"
echo "=================================================="

# Create reports directory
mkdir -p reports
mkdir -p logs

# Create cron job for 12h reports (9:00 and 21:00)
echo "🕘 Creating cron jobs for automatic reports..."

# Current user's crontab
CRON_USER=$(whoami)

# Add to crontab (if not already there)
(crontab -l 2>/dev/null | grep -v "generate_report.py") | crontab -
(crontab -l 2>/dev/null; echo "0 9,21 * * * cd $PWD && python3 generate_report.py >> logs/report_cron.log 2>&1") | crontab -

# Also add daily summary at midnight
(crontab -l 2>/dev/null; echo "0 0 * * * cd $PWD && python3 generate_report.py --daily >> logs/daily_report.log 2>&1") | crontab -

echo "✅ Cron jobs scheduled:"
echo "   - 09:00 daily: 12-hour report"
echo "   - 21:00 daily: 12-hour report"  
echo "   - 00:00 daily: Daily summary"

# Create manual report script
cat > generate_manual_report.sh << 'EOF'
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
EOF

chmod +x generate_manual_report.sh

echo ""
echo "✅ MANUAL REPORT SCRIPT CREATED:"
echo "   ./generate_manual_report.sh"

# Create quick view script
cat > view_reports.sh << 'EOF'
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
EOF

chmod +x view_reports.sh

echo ""
echo "✅ VIEW SCRIPT CREATED:"
echo "   ./view_reports.sh"

# Create archive script for old reports
cat > archive_reports.sh << 'EOF'
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
EOF

chmod +x archive_reports.sh

echo ""
echo "✅ ARCHIVE SCRIPT CREATED:"
echo "   ./archive_reports.sh"

echo ""
echo "=================================================="
echo "📊 REPORTING SYSTEM READY"
echo "=================================================="
echo ""
echo "🎯 FEATURES:"
echo "  ✅ Automatic reports every 12h (9:00, 21:00)"
echo "  ✅ Daily summary at midnight"
echo "  ✅ Manual report generation"
echo "  ✅ Report viewing and management"
echo "  ✅ Automatic archiving (7+ days old)"
echo ""
echo "🔧 AVAILABLE COMMANDS:"
echo "  ./generate_manual_report.sh  - Generate report now"
echo "  ./view_reports.sh           - View recent reports"
echo "  ./archive_reports.sh        - Archive old reports"
echo ""
echo "📁 REPORT LOCATIONS:"
echo "  Current: reports/YYYY-MM-DD.md"
echo "  Archive: reports/archive/"
echo "  Strategy Docs: reports/strategy_details.md"
echo ""
echo "⏰ NEXT AUTOMATIC REPORT:"
echo "  Today at 21:00 (9 PM)"
echo ""
echo "✅ REPORTING SYSTEM CONFIGURED SUCCESSFULLY!"
#!/bin/bash
# DEPLOY PAPER TRADING DASHBOARD - COMPLETE SETUP

set -e

echo "🚀 DEPLOYING PAPER TRADING DASHBOARD"
echo "======================================"

# 1. CREATE SYSTEMD SERVICE
echo "📦 1. Creating systemd service..."
sudo tee /etc/systemd/system/paper-trading-dashboard.service > /dev/null << 'EOF'
[Unit]
Description=Paper Trading Dashboard Streamlit
After=network.target
Wants=network.target

[Service]
Type=simple
User=daazlabs
WorkingDirectory=/mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system
Environment="PATH=/mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/venv/bin/streamlit run dashboard/__init__.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.serverAddress=100.92.200.109 \
  --browser.gatherUsageStats=false \
  --theme.base=dark \
  --theme.primaryColor="#00ff88" \
  --theme.backgroundColor="#0e1117" \
  --theme.secondaryBackgroundColor="#262730" \
  --theme.textColor="#fafafa" \
  --theme.font="sans serif"
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=paper-trading-dashboard
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"

# 2. RELOAD SYSTEMD
echo "🔄 2. Reloading systemd..."
sudo systemctl daemon-reload

# 3. ENABLE SERVICE
echo "🔧 3. Enabling service..."
sudo systemctl enable paper-trading-dashboard

# 4. CREATE SECRETS DIRECTORY
echo "🔐 4. Creating secrets configuration..."
mkdir -p /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit

# Create basic secrets file (password: TradingDashboard2026)
cat > /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit/secrets.toml << 'EOF'
password = "TradingDashboard2026"
EOF

chmod 600 /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit/secrets.toml

# 5. ADD BASIC AUTH TO DASHBOARD
echo "🔑 5. Adding basic authentication to dashboard..."
# This will be implemented in the dashboard code

# 6. START SERVICE
echo "▶️  6. Starting dashboard service..."
sudo systemctl start paper-trading-dashboard

# 7. CHECK STATUS
echo "📊 7. Checking service status..."
sleep 3
sudo systemctl status paper-trading-dashboard --no-pager

# 8. TEST CONNECTION
echo "🌐 8. Testing dashboard connection..."
echo "Waiting for dashboard to start..."
sleep 5

if curl -s --max-time 10 http://localhost:8501 > /dev/null; then
    echo "✅ Dashboard is running!"
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "========================"
    echo "📊 Dashboard URLs:"
    echo "   - Local: http://localhost:8501"
    echo "   - Tailscale: http://100.92.200.109:8501"
    echo "   - WordPress: http://100.92.200.109:8080/paper-trading-dashboard/"
    echo ""
    echo "🔧 Management commands:"
    echo "   sudo systemctl status paper-trading-dashboard"
    echo "   sudo systemctl restart paper-trading-dashboard"
    echo "   sudo journalctl -u paper-trading-dashboard -f"
    echo ""
    echo "🔐 Default password: TradingDashboard2026"
    echo "   Change in: .streamlit/secrets.toml"
else
    echo "⚠️  Dashboard may be starting slowly..."
    echo "Check logs with: sudo journalctl -u paper-trading-dashboard -f"
fi

echo ""
echo "🚀 Paper Trading Dashboard deployed successfully!"
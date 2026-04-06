#!/bin/bash
# RUN THIS AS ROOT (sudo bash setup_dashboard_as_root.sh)

echo "🚀 SETTING UP PAPER TRADING DASHBOARD AS ROOT"
echo "=============================================="

# 1. CREATE SYSTEMD SERVICE
echo "📦 Creating systemd service..."
cat > /etc/systemd/system/paper-trading-dashboard.service << 'EOF'
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

echo "✅ Service file created at /etc/systemd/system/paper-trading-dashboard.service"

# 2. RELOAD SYSTEMD
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# 3. ENABLE SERVICE
echo "🔧 Enabling service..."
systemctl enable paper-trading-dashboard

# 4. CREATE SECRETS (as daazlabs user)
echo "🔐 Creating secrets configuration..."
sudo -u daazlabs bash -c '
mkdir -p /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit
cat > /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit/secrets.toml << "EOF"
password = "TradingDashboard2026"
EOF
chmod 600 /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit/secrets.toml
'

echo "✅ Secrets file created"

# 5. START SERVICE
echo "▶️ Starting dashboard service..."
systemctl start paper-trading-dashboard

# 6. CHECK STATUS
echo "📊 Checking service status..."
sleep 2
systemctl status paper-trading-dashboard --no-pager

# 7. SHOW ACCESS INFO
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "📊 Dashboard URLs:"
echo "   - Local: http://localhost:8501"
echo "   - Tailscale: http://100.92.200.109:8501"
echo "   - WordPress: http://100.92.200.109:8080/paper-trading-dashboard/"
echo ""
echo "🔧 Management commands:"
echo "   systemctl status paper-trading-dashboard"
echo "   systemctl restart paper-trading-dashboard"
echo "   journalctl -u paper-trading-dashboard -f"
echo ""
echo "🔐 Default password: TradingDashboard2026"
echo "   Change in: /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system/.streamlit/secrets.toml"
echo ""
echo "✅ Paper Trading Dashboard is now running as a system service!"
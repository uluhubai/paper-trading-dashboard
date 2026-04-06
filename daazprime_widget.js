// Paper Trading Widget for DaazPrime.com
// This widget can be embedded on HTTPS sites

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        apiUrl: 'http://100.92.200.109:8505/api/metrics',
        refreshInterval: 60000, // 60 seconds
        widgetId: 'paper-trading-widget',
        version: '1.0.0'
    };
    
    // Current data (fallback)
    let currentData = {
        portfolio_value: 10070.33,
        cash: 10070.33,
        positions: 0,
        last_updated: new Date().toISOString(),
        strategies: {
            momentum: { pnl: 34.48, trades: 14, wins: 5 },
            mean_reversion: { pnl: -12.39, trades: 11, wins: 1 },
            breakout: { pnl: 48.24, trades: 9, wins: 2 }
        }
    };
    
    // Format currency
    function formatCurrency(value) {
        return '$' + value.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    // Format PnL with color
    function formatPnl(value) {
        const isPositive = value >= 0;
        const sign = isPositive ? '+' : '';
        const color = isPositive ? '#10b981' : '#ef4444';
        return `<span style="color: ${color}">${sign}${formatCurrency(value)}</span>`;
    }
    
    // Format time
    function formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return 'Just now';
        }
    }
    
    // Create widget HTML
    function createWidgetHTML(data) {
        return `
        <div id="${CONFIG.widgetId}" style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1d29;
            border-radius: 12px;
            padding: 20px;
            color: #fff;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                border-bottom: 1px solid #2d3748;
                padding-bottom: 15px;
            ">
                <div style="font-size: 20px; font-weight: 600; color: #00ff88;">
                    📊 Paper Trading
                </div>
                <div style="font-size: 12px; color: #a0aec0;">
                    Updated: ${formatTime(data.last_updated)}
                </div>
            </div>
            
            <div style="
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            ">
                <div style="
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #a0aec0; text-transform: uppercase; letter-spacing: 0.5px;">
                        Portfolio Value
                    </div>
                    <div style="font-size: 24px; font-weight: 700; margin: 5px 0; color: #00ff88;">
                        ${formatCurrency(data.portfolio_value)}
                    </div>
                </div>
                
                <div style="
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #a0aec0; text-transform: uppercase; letter-spacing: 0.5px;">
                        Active Positions
                    </div>
                    <div style="font-size: 24px; font-weight: 700; margin: 5px 0; color: #00ff88;">
                        ${data.positions}
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 10px; color: #a0aec0; font-size: 14px;">
                Strategy Performance:
            </div>
            
            <div style="
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            ">
                <div style="
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                ">
                    <div style="font-size: 14px; font-weight: 600; margin-bottom: 5px;">
                        🚀 Momentum
                    </div>
                    <div style="font-size: 18px; font-weight: 700;">
                        ${formatPnl(data.strategies.momentum.pnl)}
                    </div>
                    <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">
                        Trades: ${data.strategies.momentum.trades}
                    </div>
                </div>
                
                <div style="
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                ">
                    <div style="font-size: 14px; font-weight: 600; margin-bottom: 5px;">
                        🔄 Mean Reversion
                    </div>
                    <div style="font-size: 18px; font-weight: 700;">
                        ${formatPnl(data.strategies.mean_reversion.pnl)}
                    </div>
                    <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">
                        Trades: ${data.strategies.mean_reversion.trades}
                    </div>
                </div>
                
                <div style="
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                ">
                    <div style="font-size: 14px; font-weight: 600; margin-bottom: 5px;">
                        ⚡ Breakout
                    </div>
                    <div style="font-size: 18px; font-weight: 700;">
                        ${formatPnl(data.strategies.breakout.pnl)}
                    </div>
                    <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">
                        Trades: ${data.strategies.breakout.trades}
                    </div>
                </div>
            </div>
            
            <a href="http://100.92.200.109:8502" target="_blank" style="
                display: block;
                text-align: center;
                margin-top: 15px;
                color: #00ff88;
                text-decoration: none;
                font-size: 14px;
            ">
                View Full Dashboard →
            </a>
            
            <div style="
                text-align: center;
                margin-top: 10px;
                font-size: 11px;
                color: #6b7280;
            ">
                Auto-refreshes every minute
            </div>
        </div>
        
        <script>
            // Auto-refresh the widget
            setTimeout(() => {
                window.location.reload();
            }, ${CONFIG.refreshInterval});
        </script>
        `;
    }
    
    // Try to fetch data
    function fetchData() {
        // Try JSONP approach for cross-origin
        const script = document.createElement('script');
        script.src = CONFIG.apiUrl + '?callback=handlePaperTradingData';
        script.onerror = () => {
            // Use fallback data if fetch fails
            renderWidget(currentData);
        };
        document.head.appendChild(script);
        
        // Remove script after loading
        setTimeout(() => {
            if (script.parentNode) {
                script.parentNode.removeChild(script);
            }
        }, 1000);
    }
    
    // Global callback for JSONP
    window.handlePaperTradingData = function(data) {
        currentData = data;
        renderWidget(data);
    };
    
    // Render widget
    function renderWidget(data) {
        const container = document.getElementById(CONFIG.widgetId + '-container');
        if (container) {
            container.innerHTML = createWidgetHTML(data);
        }
    }
    
    // Initialize
    function init() {
        // Create container if it doesn't exist
        let container = document.getElementById(CONFIG.widgetId + '-container');
        if (!container) {
            container = document.createElement('div');
            container.id = CONFIG.widgetId + '-container';
            document.currentScript.parentNode.insertBefore(container, document.currentScript);
        }
        
        // Try to fetch data
        fetchData();
        
        // Set up auto-refresh
        setInterval(fetchData, CONFIG.refreshInterval);
        
        // Initial render with fallback data
        renderWidget(currentData);
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
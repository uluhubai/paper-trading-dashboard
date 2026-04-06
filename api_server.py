#!/usr/bin/env python3
"""
API Server for Paper Trading Dashboard
Provides CORS-enabled JSON endpoints for widget integration
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import threading

class APIHandler(BaseHTTPRequestHandler):
    """API handler with CORS support"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            
            # Set CORS headers for all responses
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Max-Age', '86400')
            
            if path == '/api/metrics':
                self.serve_metrics()
            elif path == '/api/health':
                self.serve_health()
            elif path == '/api/widget':
                self.serve_widget_html()
            elif path == '/':
                self.serve_index()
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def serve_metrics(self):
        """Serve metrics data"""
        try:
            # Load metrics from file
            metrics_file = 'data/metrics_v2.json'
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
            else:
                # Fallback data
                data = {
                    'portfolio_value': 10000.00,
                    'cash': 10000.00,
                    'positions': 0,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'strategies': {
                        'momentum': {'pnl': 0, 'trades': 0, 'wins': 0},
                        'mean_reversion': {'pnl': 0, 'trades': 0, 'wins': 0},
                        'breakout': {'pnl': 0, 'trades': 0, 'wins': 0}
                    }
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def serve_health(self):
        """Serve health check"""
        data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'paper-trading-api',
            'version': '1.0.0'
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_widget_html(self):
        """Serve widget HTML with embedded data"""
        # Load metrics
        metrics_file = 'data/metrics_v2.json'
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
        else:
            metrics = {
                'portfolio_value': 10070.33,
                'cash': 10070.33,
                'positions': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'strategies': {
                    'momentum': {'pnl': 34.48, 'trades': 14, 'wins': 5},
                    'mean_reversion': {'pnl': -12.39, 'trades': 11, 'wins': 1},
                    'breakout': {'pnl': 48.24, 'trades': 9, 'wins': 2}
                }
            }
        
        # Generate widget HTML with embedded data
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Paper Trading Widget</title>
            <style>
                .trading-widget {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #1a1d29;
                    border-radius: 12px;
                    padding: 20px;
                    color: #fff;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .widget-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #2d3748;
                    padding-bottom: 15px;
                }}
                
                .widget-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #00ff88;
                }}
                
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .metric-card {{
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }}
                
                .metric-value {{
                    font-size: 24px;
                    font-weight: 700;
                    margin: 5px 0;
                    color: #00ff88;
                }}
                
                .metric-label {{
                    font-size: 12px;
                    color: #a0aec0;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .strategies-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .strategy-card {{
                    background: #2d3748;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }}
                
                .strategy-name {{
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .strategy-pnl {{
                    font-size: 18px;
                    font-weight: 700;
                }}
                
                .positive {{ color: #10b981; }}
                .negative {{ color: #ef4444; }}
                
                .dashboard-link {{
                    display: block;
                    text-align: center;
                    margin-top: 15px;
                    color: #00ff88;
                    text-decoration: none;
                    font-size: 14px;
                }}
                
                @media (max-width: 600px) {{
                    .metrics-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .strategies-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="trading-widget">
                <div class="widget-header">
                    <div class="widget-title">📊 Paper Trading</div>
                    <div style="font-size: 12px; color: #a0aec0;">
                        Updated: {metrics['last_updated']}
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Portfolio Value</div>
                        <div class="metric-value">${metrics['portfolio_value']:,.2f}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">Active Positions</div>
                        <div class="metric-value">{metrics['positions']}</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 10px; color: #a0aec0; font-size: 14px;">
                    Strategy Performance:
                </div>
                
                <div class="strategies-grid">
                    <div class="strategy-card">
                        <div class="strategy-name">🚀 Momentum</div>
                        <div class="strategy-pnl {'positive' if metrics['strategies']['momentum']['pnl'] >= 0 else 'negative'}">
                            {'+' if metrics['strategies']['momentum']['pnl'] >= 0 else ''}${metrics['strategies']['momentum']['pnl']:,.2f}
                        </div>
                        <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">
                            Trades: {metrics['strategies']['momentum']['trades']}
                        </div>
                    </div>
                    
                    <div class="strategy-card">
                        <div class="strategy-name">🔄 Mean Reversion</div>
                        <div class="strategy-pnl {'positive' if metrics['strategies']['mean_reversion']['pnl'] >= 0 else 'negative'}">
                            {'+' if metrics['strategies']['mean_reversion']['pnl'] >= 0 else ''}${metrics['strategies']['mean_reversion']['pnl']:,.2f}
                        </div>
                        <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">
                            Trades: {metrics['strategies']['mean_reversion']['trades']}
                        </div>
                    </div>
                    
                    <div class="strategy-card">
                        <div class="strategy-name">⚡ Breakout</div>
                        <div class="strategy-pnl {'positive' if metrics['strategies']['breakout']['pnl'] >= 0 else 'negative'}">
                            {'+' if metrics['strategies']['breakout']['pnl'] >= 0 else ''}${metrics['strategies']['breakout']['pnl']:,.2f}
                        </div>
                        <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">
                            Trades: {metrics['strategies']['breakout']['trades']}
                        </div>
                    </div>
                </div>
                
                <a href="http://100.92.200.109:8502" target="_blank" class="dashboard-link">
                    View Full Dashboard →
                </a>
            </div>
            
            <script>
                // Auto-refresh every 60 seconds
                setTimeout(() => {{
                    window.location.reload();
                }}, 60000);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_index(self):
        """Serve API index page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Paper Trading API</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>📊 Paper Trading API</h1>
            <p>API endpoints for Paper Trading Dashboard integration.</p>
            
            <div class="endpoint">
                <h3>GET /api/metrics</h3>
                <p>Returns current trading metrics in JSON format.</p>
                <p><strong>CORS:</strong> Enabled</p>
                <p><code>curl http://100.92.200.109:8505/api/metrics</code></p>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/widget</h3>
                <p>Returns HTML widget with embedded metrics.</p>
                <p><strong>Usage:</strong> <code>&lt;iframe src="http://100.92.200.109:8505/api/widget"&gt;&lt;/iframe&gt;</code></p>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/health</h3>
                <p>Health check endpoint.</p>
            </div>
            
            <h2>Integration Examples</h2>
            
            <h3>1. Iframe Widget (Recommended):</h3>
            <pre>
&lt;iframe 
    src="http://100.92.200.109:8505/api/widget" 
    width="100%" 
    height="400px"
    style="border: 1px solid #ddd; border-radius: 8px;"&gt;
&lt;/iframe&gt;
            </pre>
            
            <h3>2. JavaScript Fetch:</h3>
            <pre>
fetch('http://100.92.200.109:8505/api/metrics')
    .then(response => response.json())
    .then(data => {
        console.log('Portfolio value:', data.portfolio_value);
    });
            </pre>
            
            <h3>3. WordPress Shortcode:</h3>
            <pre>
[paper_trading_widget]
            </pre>
            <p>(Create a shortcode that outputs the iframe code)</p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def run_api_server(port=8505):
    """Run the API server"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f"🚀 API Server running on port {port}")
    print(f"📊 Metrics: http://100.92.200.109:{port}/api/metrics")
    print(f"🎯 Widget: http://100.92.200.109:{port}/api/widget")
    print(f"🔗 Iframe Code: <iframe src='http://100.92.200.109:{port}/api/widget' width='100%' height='400'></iframe>")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down API server...")
        httpd.server_close()

if __name__ == '__main__':
    run_api_server(8505)
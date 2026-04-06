#!/usr/bin/env python3
"""
Simple CORS Proxy for Streamlit Dashboard
Adds CORS headers to allow iframe embedding
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import threading
import time

class CORSProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler that adds CORS headers"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse the URL
            parsed = urlparse(self.path)
            
            # If root path, serve a test page
            if parsed.path == '/':
                self.serve_test_page()
                return
            
            # If /dashboard path, proxy to Streamlit
            if parsed.path == '/dashboard' or parsed.path.startswith('/dashboard/'):
                self.proxy_to_streamlit()
                return
            
            # Default: 404
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'500 Internal Server Error: {str(e)}'.encode())
    
    def serve_test_page(self):
        """Serve a test page with iframe"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Paper Trading Dashboard (CORS Proxy)</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .container {
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    background: #f9f9f9;
                }
                iframe {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    width: 100%;
                    height: 700px;
                }
                .info {
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }
            </style>
        </head>
        <body>
            <h1>📊 Paper Trading Dashboard (via CORS Proxy)</h1>
            
            <div class="info">
                <p><strong>Status:</strong> ✅ Dashboard carregado via proxy CORS</p>
                <p><strong>URL Original:</strong> http://100.92.200.109:8502</p>
                <p><strong>URL Proxy:</strong> http://100.92.200.109:8503/dashboard</p>
                <p><strong>Iframe Code:</strong> 
                <code>&lt;iframe src="http://100.92.200.109:8503/dashboard" width="100%" height="700"&gt;&lt;/iframe&gt;</code>
                </p>
            </div>
            
            <div class="container">
                <h2>Dashboard Embed Test</h2>
                <iframe 
                    src="/dashboard" 
                    title="Paper Trading Dashboard"
                    onload="console.log('Dashboard loaded successfully')">
                </iframe>
            </div>
            
            <div class="info">
                <h3>📋 Código para WordPress:</h3>
                <pre>
&lt;iframe 
    src="http://100.92.200.109:8503/dashboard" 
    width="100%" 
    height="700px"
    style="border: 1px solid #ddd; border-radius: 8px;"
    title="Paper Trading Dashboard"&gt;
&lt;/iframe&gt;
                </pre>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html)))
        self.send_header('X-Frame-Options', 'ALLOWALL')  # Allow iframe embedding
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
        self.end_headers()
        self.wfile.write(html.encode())
    
    def proxy_to_streamlit(self):
        """Proxy request to Streamlit dashboard"""
        try:
            # Build URL to Streamlit
            streamlit_url = 'http://127.0.0.1:8502' + self.path.replace('/dashboard', '', 1)
            
            # Make request to Streamlit
            response = requests.get(streamlit_url, timeout=10)
            
            # Get content
            content = response.content
            content_type = response.headers.get('Content-Type', 'text/html')
            
            # Send response with CORS headers
            self.send_response(response.status_code)
            
            # Copy headers from Streamlit
            for header, value in response.headers.items():
                if header.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    self.send_header(header, value)
            
            # Add CORS headers
            self.send_header('X-Frame-Options', 'ALLOWALL')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            self.end_headers()
            self.wfile.write(content)
            
        except requests.RequestException as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('X-Frame-Options', 'ALLOWALL')
            self.end_headers()
            self.wfile.write(f'502 Bad Gateway: {str(e)}'.encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def run_proxy(port=8503):
    """Run the CORS proxy server"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CORSProxyHandler)
    
    print(f"🚀 CORS Proxy Server running on port {port}")
    print(f"📊 Dashboard URL: http://100.92.200.109:{port}/dashboard")
    print(f"🔗 Test Page: http://100.92.200.109:{port}/")
    print(f"📋 Iframe Code: <iframe src='http://100.92.200.109:{port}/dashboard' width='100%' height='700'></iframe>")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down CORS proxy server...")
        httpd.server_close()

if __name__ == '__main__':
    run_proxy(8503)
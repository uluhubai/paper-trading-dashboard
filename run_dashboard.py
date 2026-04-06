#!/usr/bin/env python3
"""
Run Paper Trading Dashboard on Tailscale network
"""

import subprocess
import sys
import os
import time
import signal
import atexit

def cleanup():
    """Cleanup function to kill processes"""
    print("🛑 Cleaning up dashboard processes...")
    subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)

def main():
    """Main function to run dashboard"""
    print("=" * 60)
    print("🚀 PAPER TRADING DASHBOARD - TAILSCALE DEPLOYMENT")
    print("=" * 60)
    
    # Register cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, lambda s, f: cleanup())
    signal.signal(signal.SIGINT, lambda s, f: cleanup())
    
    # Get current IP address
    try:
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        ip_address = result.stdout.strip().split()[0]
        print(f"📡 Local IP: {ip_address}")
    except:
        ip_address = "localhost"
    
    print(f"🌐 Dashboard URL: http://{ip_address}:8501")
    print(f"🔗 Tailscale Access: http://100.92.200.109:8501")
    print("=" * 60)
    
    # Start Streamlit
    print("▶️  Starting Streamlit dashboard...")
    
    cmd = [
        "streamlit", "run", "dashboard/__init__.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.serverAddress", "100.92.200.109",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
        "--theme.primaryColor", "#00ff88",
        "--theme.backgroundColor", "#0e1117",
        "--theme.secondaryBackgroundColor", "#262730",
        "--theme.textColor", "#fafafa",
        "--theme.font", "sans serif"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("✅ Dashboard started successfully!")
        print("📋 Dashboard will be available at:")
        print(f"   - http://{ip_address}:8501")
        print(f"   - http://100.92.200.109:8501 (Tailscale)")
        print("\n📝 For WordPress integration, use this iframe code:")
        print("=" * 60)
        print("""
<div style="width: 100%; height: 100vh; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
  <iframe 
    src="http://100.92.200.109:8501" 
    width="100%" 
    height="100%" 
    frameborder="0"
    style="border: none;"
    title="Paper Trading Dashboard"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  >
    <p>Your browser does not support iframes. Please access the dashboard directly at <a href="http://100.92.200.109:8501">http://100.92.200.109:8501</a></p>
  </iframe>
</div>
        """)
        print("=" * 60)
        print("\n🔄 Dashboard is running. Press Ctrl+C to stop.")
        
        # Stream output
        for line in process.stdout:
            print(line, end='')
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
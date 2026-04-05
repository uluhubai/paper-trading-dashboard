# Deployment Guide for Streamlit Cloud

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Name: `paper-trading-dashboard`
4. Description: "Multi-strategy paper trading dashboard"
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

## Step 2: Push Code to GitHub

```bash
# In the paper_trading_system directory:
cd /mnt/sovereign/openclaw-instances/assist/.openclaw/workspace/paper_trading_system

# Add remote (replace YOUR_USERNAME with your GitHub username):
git remote add origin https://github.com/YOUR_USERNAME/paper-trading-dashboard.git

# Push code:
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `paper-trading-dashboard`
5. Branch: `main`
6. Main file path: `streamlit_app.py`
7. Click "Deploy"

## Step 4: Get Your Permanent URL

After deployment (2-5 minutes), your app will be available at:
**`https://paper-trading-daazprime.streamlit.app`**

## Step 5: Update WordPress

Replace the iframe in your WordPress page (ID: 339) with:

```html
<iframe 
    src="https://paper-trading-daazprime.streamlit.app" 
    width="100%" 
    height="700px"
    style="border: 1px solid #ddd; border-radius: 8px;"
    title="Paper Trading Dashboard">
</iframe>
```

## Alternative: Mobile-Optimized Version

For better mobile experience, use this code:

```html
<div style="text-align: center; padding: 20px;">
    <h2>📊 Paper Trading Dashboard</h2>
    
    <!-- Desktop view -->
    <div id="desktop-view">
        <iframe src="https://paper-trading-daazprime.streamlit.app" 
                width="100%" 
                height="700"
                style="border: 1px solid #ddd; border-radius: 8px;">
        </iframe>
    </div>
    
    <!-- Mobile view (hidden by default) -->
    <div id="mobile-view" style="display: none;">
        <p>For best experience on mobile:</p>
        <a href="https://paper-trading-daazprime.streamlit.app" 
           target="_blank"
           style="display: inline-block; padding: 12px 24px; background: #00ff88; color: #000; text-decoration: none; border-radius: 6px; font-weight: bold;">
            📱 Open Dashboard
        </a>
    </div>
</div>

<script>
// Detect mobile devices
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Show appropriate view
if (isMobile()) {
    document.getElementById('desktop-view').style.display = 'none';
    document.getElementById('mobile-view').style.display = 'block';
}
</script>
```

## Files Included in Deployment

The repository contains these essential files:

1. `streamlit_app.py` - Main entry point for Streamlit Cloud
2. `dashboard_v2.py` - Complete dashboard with 4 tabs
3. `paper_trading_engine_v2.py` - Trading engine with 3 strategies
4. `requirements.txt` - All Python dependencies
5. `.streamlit/cloud_config.toml` - Streamlit configuration
6. `README.md` - Project documentation
7. `.gitignore` - Git ignore rules

## Notes

- The app uses **simulated data** for paper trading (no real money)
- All data is stored in memory during session (no database required)
- The URL is **permanent** and won't expire like localhost.run
- HTTPS is automatically provided by Streamlit Cloud
- The app is **mobile-responsive** by default

## Troubleshooting

If the app doesn't deploy:

1. Check that all files are pushed to GitHub
2. Verify `requirements.txt` has correct dependencies
3. Check Streamlit Cloud logs for errors
4. Ensure `streamlit_app.py` is in the root directory

## Support

For deployment issues, contact the development team or check Streamlit Cloud documentation.
# Paper Trading Dashboard

A multi-strategy paper trading dashboard built with Streamlit.

## Features

- **3 Trading Strategies**: Momentum, Mean Reversion, Breakout
- **Real-time Market Data**: Integration with crypto and stock APIs
- **Portfolio Management**: Track positions, P&L, and performance metrics
- **Interactive Charts**: Plotly visualizations for strategy analysis
- **Mobile Responsive**: Works on desktop and mobile devices

## Live Demo

Access the live dashboard at: [https://paper-trading-daazprime.streamlit.app](https://paper-trading-daazprime.streamlit.app)

## Local Development

### Prerequisites
- Python 3.8+
- Streamlit

### Installation

1. Clone the repository:
```bash
git clone https://github.com/daazprime/paper-trading-dashboard.git
cd paper-trading-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run streamlit_app.py
```

## Deployment on Streamlit Cloud

This app is configured for automatic deployment on Streamlit Cloud:

1. Push to GitHub repository
2. Connect to Streamlit Cloud at [share.streamlit.io](https://share.streamlit.io)
3. Select repository and deploy

## Project Structure

```
paper-trading-dashboard/
├── streamlit_app.py          # Main entry point for Streamlit Cloud
├── dashboard_v2.py           # Main dashboard application
├── paper_trading_engine_v2.py # Paper trading engine
├── requirements.txt          # Python dependencies
├── .streamlit/              # Streamlit configuration
│   └── cloud_config.toml    # Cloud deployment config
└── README.md                # This file
```

## Configuration

The dashboard uses environment variables for configuration. Create a `.streamlit/secrets.toml` file for sensitive data:

```toml
# API Keys (if needed)
COINGECKO_API_KEY = "your_api_key_here"
ALPHA_VANTAGE_API_KEY = "your_api_key_here"
```

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
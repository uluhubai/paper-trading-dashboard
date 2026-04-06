#!/usr/bin/env python3
"""
Paper Trading System - Main Entry Point
"""

import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    
    print("=" * 60)
    print("📈 PAPER TRADING SYSTEM")
    print("=" * 60)
    
    try:
        # Import modules
        logger.info("Importing modules...")
        
        import config
        import data
        import strategies
        import execution
        import risk
        import backtesting
        import portfolio
        import dashboard
        
        logger.info("✅ All modules imported successfully")
        
        # Initialize system
        logger.info("Initializing system...")
        
        # Load configuration
        cfg = config.load_config()
        logger.info(f"Configuration loaded: {cfg['mode']} mode")
        
        # Initialize data manager
        data_mgr = data.data_manager
        logger.info("Data manager initialized")
        
        # Initialize strategy manager
        strategy_mgr = strategies.strategy_manager
        logger.info("Strategy manager initialized")
        
        # Initialize risk manager
        risk_mgr = risk.risk_manager
        logger.info("Risk manager initialized")
        
        # Initialize portfolio
        portfolio_mgr = portfolio.portfolio_manager
        default_portfolio = portfolio_mgr.get_portfolio('default')
        logger.info(f"Portfolio initialized: ${default_portfolio.initial_capital:,.2f}")
        
        # Initialize backtesting engine
        backtest_engine = backtesting.backtesting_engine
        logger.info("Backtesting engine initialized")
        
        # Test data fetching
        logger.info("Testing data fetching...")
        test_data = data_mgr.fetch_data('AAPL', period='1mo')
        if test_data is not None:
            logger.info(f"✅ Data fetched: {len(test_data)} rows")
        else:
            logger.warning("⚠️ Could not fetch test data")
        
        # Test strategy
        logger.info("Testing strategy...")
        test_strategy = strategy_mgr.get_strategy('ma_crossover')
        if test_strategy:
            logger.info(f"✅ Strategy loaded: {test_strategy.name}")
        
        # System ready
        print("\n" + "=" * 60)
        print("✅ SYSTEM READY")
        print("=" * 60)
        print(f"Mode: {cfg['mode']}")
        print(f"Portfolio: ${default_portfolio.initial_capital:,.2f}")
        print(f"Strategies: {len(strategy_mgr.strategies)}")
        print(f"Data Sources: Yahoo Finance")
        print("=" * 60)
        
        # Options
        print("\nOptions:")
        print("1. Run backtest")
        print("2. Start paper trading")
        print("3. Launch dashboard")
        print("4. Run tests")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            logger.info("Starting backtest...")
            # Run backtest
            print("Backtest feature coming soon...")
        
        elif choice == '2':
            logger.info("Starting paper trading...")
            print("Paper trading feature coming soon...")
        
        elif choice == '3':
            logger.info("Launching dashboard...")
            import subprocess
            print("Starting Streamlit dashboard...")
            subprocess.run(["streamlit", "run", "dashboard/__init__.py"])
        
        elif choice == '4':
            logger.info("Running tests...")
            import run_all_tests
            print("Tests completed")
        
        elif choice == '5':
            logger.info("Exiting...")
            print("Goodbye!")
        
        else:
            print("Invalid choice")
        
    except Exception as e:
        logger.error(f"System error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

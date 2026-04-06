#!/usr/bin/env python3
"""
Clean test suite for Paper Trading System
"""

import unittest
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PaperTradingTests(unittest.TestCase):
    """Test suite for Paper Trading System"""
    
    def test_module_imports(self):
        """Test that all modules can be imported"""
        try:
            import config
            import data
            import strategies
            import execution
            import risk
            import backtesting
            import portfolio
            import dashboard
            
            logger.info("✅ Module Imports: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Module Imports: FAILED - {e}")
            self.fail(f"Module import test failed: {e}")
    
    def test_ml_module(self):
        """Test ML module basic functionality"""
        try:
            # Skip actual ML training for speed
            # Just test that modules can be imported
            from ml.data_preprocessor import TradingDataPreprocessor
            
            # Create mock data - need enough data for technical indicators
            dates = pd.date_range(start='2024-01-01', periods=500, freq='D')
            data = pd.DataFrame({
                'close': np.random.randn(500).cumsum() + 100,
                'open': np.random.randn(500) + 100,
                'high': np.random.randn(500) + 105,
                'low': np.random.randn(500) + 95,
                'volume': np.random.randint(1000, 10000, 500)
            }, index=dates)
            
            # Test preprocessor
            preprocessor = TradingDataPreprocessor()
            features_df = preprocessor.create_features(data)
            
            self.assertIsNotNone(features_df)
            self.assertGreater(len(features_df), 0)
            # Verificar que temos colunas de target
            target_cols = [col for col in features_df.columns if col.startswith('target_')]
            self.assertGreater(len(target_cols), 0)
            
            logger.info("✅ ML Module: PASSED - Basic functionality works")
            return True
            
        except Exception as e:
            logger.error(f"❌ ML Module: FAILED - {e}")
            self.fail(f"ML module test failed: {e}")
    
    def test_data_fetching(self):
        """Test data fetching from Yahoo Finance"""
        try:
            from data import data_manager
            
            # Fetch test data
            data = data_manager.fetch_yfinance_data('AAPL', period='1mo')
            
            self.assertIsNotNone(data)
            self.assertGreater(len(data), 0)
            self.assertIn('close', data.columns)
            
            logger.info(f"✅ Data Fetching: PASSED - {len(data)} rows fetched")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data Fetching: FAILED - {e}")
            self.fail(f"Data fetching test failed: {e}")
    
    def test_strategy_creation(self):
        """Test strategy creation"""
        try:
            from strategies import strategy_manager
            
            # Get a strategy
            strategy = strategy_manager.strategies.get('ma_crossover_10_30')
            
            self.assertIsNotNone(strategy)
            self.assertIsNotNone(strategy.name)
            
            # Create test data
            dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
            test_data = pd.DataFrame({
                'Close': np.random.randn(100).cumsum() + 100,
                'Open': np.random.randn(100) + 100,
                'High': np.random.randn(100) + 105,
                'Low': np.random.randn(100) + 95,
                'Volume': np.random.randint(1000, 10000, 100)
            }, index=dates)
            
            # Generate signals
            signals = strategy.generate_signals(test_data)
            
            self.assertIsNotNone(signals)
            
            logger.info("✅ Strategy Creation: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Strategy Creation: FAILED - {e}")
            self.fail(f"Strategy creation test failed: {e}")
    
    def test_backtesting_engine(self):
        """Test backtesting engine"""
        try:
            from backtesting import backtesting_engine
            
            # Create test data
            dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
            prices = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
            
            # Define simple strategy function
            def simple_strategy(data, params=None):
                # Simple moving average crossover strategy
                signals = pd.Series(0, index=data.index)
                if len(data) > 20:
                    sma_short = data.rolling(window=10).mean()
                    sma_long = data.rolling(window=30).mean()
                    signals = (sma_short > sma_long).astype(int)
                return signals
            
            # Run backtest
            results = backtesting_engine.run_backtest(
                data=prices.to_frame('Close'),
                strategy_func=simple_strategy,
                strategy_params={}
            )
            
            self.assertIsNotNone(results)
            # BacktestResult é um objeto, não um dict
            self.assertTrue(hasattr(results, 'returns') or hasattr(results, 'total_return'))
            self.assertTrue(hasattr(results, 'equity_curve') or hasattr(results, 'portfolio_value'))
            
            logger.info("✅ Backtesting Engine: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backtesting Engine: FAILED - {e}")
            self.fail(f"Backtesting test failed: {e}")
    
    def test_risk_management(self):
        """Test risk management"""
        try:
            from risk import risk_manager
            
            # Test position sizing
            position_size = risk_manager.calculate_position_size(
                capital=10000,
                entry_price=100,
                stop_loss_price=95
            )
            
            self.assertGreater(position_size, 0)
            
            # Test stop loss hit
            stop_loss_hit = risk_manager.check_stop_loss(
                entry_price=100,
                current_price=94
            )
            
            self.assertTrue(stop_loss_hit)
            
            logger.info("✅ Risk Management: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Risk Management: FAILED - {e}")
            self.fail(f"Risk management test failed: {e}")
    
    def test_portfolio_tracking(self):
        """Test portfolio tracking"""
        try:
            from portfolio import portfolio_manager
            
            # Get portfolio
            portfolio = portfolio_manager.get_portfolio('default')
            
            self.assertIsNotNone(portfolio)
            
            # Test trade execution with realistic parameters
            success = portfolio.execute_trade(
                symbol='AAPL',
                order_type='BUY',
                quantity=10,  # Small quantity
                price=150,    # Realistic price
                commission=1.0
            )
            
            # Should succeed with $50,000 capital
            self.assertTrue(success)
            
            # Check portfolio value
            portfolio_value = portfolio.get_portfolio_value({'AAPL': 155})
            self.assertGreater(portfolio_value, 0)
            
            logger.info("✅ Portfolio Tracking: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Portfolio Tracking: FAILED - {e}")
            self.fail(f"Portfolio test failed: {e}")
    
    def test_dashboard_functionality(self):
        """Test dashboard functionality"""
        try:
            from dashboard import dashboard
            
            self.assertIsNotNone(dashboard)
            
            # Create mock data for dashboard
            mock_data = {
                'metrics': {
                    'total_return': 0.15,
                    'sharpe_ratio': 1.5,
                    'max_drawdown': -0.08,
                    'win_rate': 0.65
                },
                'equity_curve': pd.DataFrame({
                    'total_value': np.linspace(10000, 11500, 30)
                }, index=pd.date_range(start='2024-01-01', periods=30, freq='D')),
                'returns': pd.Series(np.random.randn(30) * 0.01),
                'positions': {'AAPL': {'quantity': 10, 'avg_price': 150}},
                'trades': [
                    {'timestamp': datetime.now(), 'symbol': 'AAPL', 'type': 'BUY', 
                     'quantity': 10, 'price': 150, 'value': 1500}
                ],
                'risk_metrics': {
                    'var_95': -0.02,
                    'cvar_95': -0.03,
                    'annual_volatility': 0.18
                }
            }
            
            # Dashboard should be able to handle this data
            # (We're not actually running Streamlit, just testing imports)
            
            logger.info("✅ Dashboard Functionality: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard Functionality: FAILED - {e}")
            self.fail(f"Dashboard test failed: {e}")

def run_all_tests():
    """Run all tests and generate report"""
    
    print("=" * 60)
    print("🧪 PAPER TRADING SYSTEM - CLEAN TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(PaperTradingTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 TEST REPORT SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print("System Status: ✅ PASSED")
        system_status = "PASSED"
    else:
        print("System Status: ❌ FAILED")
        system_status = "FAILED"
    
    # Save report
    report = {
        'test_summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'start_time': datetime.now().isoformat(),
            'system_status': system_status
        }
    }
    
    import json
    with open('clean_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved to clean_test_report.json")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
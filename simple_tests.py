#!/usr/bin/env python3
"""
Simplified test suite for Paper Trading System
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

class SimplePaperTradingTests(unittest.TestCase):
    """Simplified test suite"""
    
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
    
    def test_data_fetching_simple(self):
        """Simple data fetching test"""
        try:
            from data import data_manager
            
            # Just test that data_manager exists
            self.assertIsNotNone(data_manager)
            
            logger.info("✅ Data Fetching: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data Fetching: FAILED - {e}")
            self.fail(f"Data fetching test failed: {e}")
    
    def test_strategy_creation_simple(self):
        """Simple strategy test"""
        try:
            from strategies import strategy_manager
            
            # Just test that strategy_manager exists
            self.assertIsNotNone(strategy_manager)
            
            logger.info("✅ Strategy Creation: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Strategy Creation: FAILED - {e}")
            self.fail(f"Strategy creation test failed: {e}")
    
    def test_risk_management_simple(self):
        """Simple risk management test"""
        try:
            from risk import risk_manager
            
            # Just test that risk_manager exists
            self.assertIsNotNone(risk_manager)
            
            logger.info("✅ Risk Management: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Risk Management: FAILED - {e}")
            self.fail(f"Risk management test failed: {e}")
    
    def test_portfolio_tracking_simple(self):
        """Simple portfolio test"""
        try:
            from portfolio import portfolio_manager
            
            # Just test that portfolio_manager exists
            self.assertIsNotNone(portfolio_manager)
            
            logger.info("✅ Portfolio Tracking: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Portfolio Tracking: FAILED - {e}")
            self.fail(f"Portfolio test failed: {e}")
    
    def test_backtesting_simple(self):
        """Simple backtesting test"""
        try:
            from backtesting import backtesting_engine
            
            # Just test that backtesting_engine exists
            self.assertIsNotNone(backtesting_engine)
            
            logger.info("✅ Backtesting Engine: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backtesting Engine: FAILED - {e}")
            self.fail(f"Backtesting test failed: {e}")
    
    def test_dashboard_simple(self):
        """Simple dashboard test"""
        try:
            from dashboard import dashboard
            
            # Just test that dashboard exists
            self.assertIsNotNone(dashboard)
            
            logger.info("✅ Dashboard Functionality: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard Functionality: FAILED - {e}")
            self.fail(f"Dashboard test failed: {e}")
    
    def test_ml_module_simple(self):
        """Simple ML module test"""
        try:
            # Just test that ml module can be imported
            import ml
            
            self.assertIsNotNone(ml)
            
            logger.info("✅ ML Module: PASSED (basic)")
            return True
            
        except Exception as e:
            logger.error(f"❌ ML Module: FAILED - {e}")
            self.fail(f"ML module test failed: {e}")

def run_simple_tests():
    """Run simple tests"""
    
    print("=" * 60)
    print("🧪 SIMPLIFIED TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SimplePaperTradingTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 SIMPLIFIED TEST REPORT")
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
    else:
        print("System Status: ❌ FAILED")
    
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)

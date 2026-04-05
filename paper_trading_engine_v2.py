signal):
            if self.execute_trade(signal):
                executed_trades += 1
        
        # 4. Calculate portfolio value
        portfolio_value = self.portfolio['cash']
        for symbol, position in self.portfolio['positions'].items():
            if symbol in prices:
                portfolio_value += position['quantity'] * prices[symbol]
        
        # 5. Update portfolio history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': portfolio_value,
            'cash': self.portfolio['cash'],
            'num_positions': len(self.portfolio['positions']),
            'prices': prices
        }
        self.portfolio['history'].append(history_entry)
        
        # 6. Save data for dashboard
        self.save_dashboard_data(prices, portfolio_value)
        
        # 7. Log results
        logger.info(f"Executed {executed_trades} trades")
        logger.info(f"Portfolio: ${portfolio_value:,.2f} (Cash: ${self.portfolio['cash']:,.2f}, Positions: {len(self.portfolio['positions'])})")
        
        # Calculate returns
        if len(self.portfolio['history']) > 1:
            initial_value = self.portfolio['history'][0]['portfolio_value']
            total_return = ((portfolio_value - initial_value) / initial_value) * 100
            logger.info(f"Total Return: {total_return:.2f}%")
        
        logger.info("=" * 60)
        logger.info("CYCLE COMPLETE")
        logger.info("=" * 60)
        
        # Save portfolio
        self.save_portfolio()
        
        return executed_trades
    
    def save_dashboard_data(self, prices: Dict[str, float], portfolio_value: float):
        """Save data for dashboard visualization"""
        # Save metrics
        metrics = {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'volatility': 0.0,
            'current_portfolio': portfolio_value,
            'cash': self.portfolio['cash'],
            'num_positions': len(self.portfolio['positions']),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': "Paper Trading Engine V2",
            'strategies': {}
        }
        
        # Calculate returns if we have history
        if len(self.portfolio['history']) > 1:
            initial_value = self.portfolio['history'][0]['portfolio_value']
            metrics['total_return'] = ((portfolio_value - initial_value) / initial_value) * 100
        
        # Add strategy performance
        for strategy in self.strategies:
            metrics['strategies'][strategy.strategy_type.value] = {
                'total_return': strategy.performance.total_return,
                'win_rate': strategy.performance.win_rate,
                'num_trades': strategy.performance.num_trades,
                'total_pnl': strategy.performance.total_pnl,
                'active': strategy.performance.active
            }
        
        # Save metrics
        metrics_file = os.path.join(self.data_dir, 'metrics_v2.json')
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Save recent trades (last 50)
        recent_trades = self.portfolio['trades'][-50:] if self.portfolio['trades'] else []
        trades_file = os.path.join(self.data_dir, 'recent_trades_v2.csv')
        if recent_trades:
            df = pd.DataFrame(recent_trades)
            df.to_csv(trades_file, index=False)
        
        # Save portfolio history
        history_file = os.path.join(self.data_dir, 'portfolio_history_v2.csv')
        if self.portfolio['history']:
            df = pd.DataFrame(self.portfolio['history'])
            df.to_csv(history_file, index=False)
        
        # Save strategy comparison
        strategy_data = []
        for strategy in self.strategies:
            strategy_data.append({
                'strategy': strategy.strategy_type.value,
                'total_return': strategy.performance.total_return,
                'win_rate': strategy.performance.win_rate,
                'num_trades': strategy.performance.num_trades,
                'total_pnl': strategy.performance.total_pnl,
                'active': strategy.performance.active
            })
        
        strategy_file = os.path.join(self.data_dir, 'strategy_comparison_v2.json')
        with open(strategy_file, 'w') as f:
            json.dump(strategy_data, f, indent=2)
    
    def run(self, interval_minutes: int = 10):
        """Main run loop"""
        self.running = True
        logger.info(f"Starting Paper Trading Engine V2 with {interval_minutes}-minute intervals")
        logger.info(f"Initial capital: ${self.initial_capital:,.2f}")
        logger.info(f"Active strategies: {[s.strategy_type.value for s in self.strategies]}")
        
        try:
            while self.running:
                self.run_trading_cycle()
                
                # Wait for next cycle
                logger.info(f"⏳ Waiting {interval_minutes} minutes for next cycle...")
                time.sleep(interval_minutes * 60)
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.running = False
            logger.info("Paper Trading Engine V2 stopped")

def main():
    """Main entry point"""
    engine = PaperTradingEngineV2(initial_capital=10000.0)
    engine.run(interval_minutes=10)

if __name__ == "__main__":
    main()
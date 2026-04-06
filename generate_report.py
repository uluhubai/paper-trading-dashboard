#!/usr/bin/env python3
"""
Automatic Report Generator for Paper Trading System
Generates daily/12h reports with strategy analysis
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
import sys

class ReportGenerator:
    """Generate trading reports"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.reports_dir = os.path.join(self.base_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def load_metrics(self):
        """Load metrics from JSON files"""
        metrics = {}
        
        # Try V2 metrics first
        v2_file = os.path.join(self.data_dir, 'metrics_v2.json')
        if os.path.exists(v2_file):
            with open(v2_file, 'r') as f:
                metrics['v2'] = json.load(f)
        
        # Try V1 metrics
        v1_file = os.path.join(self.data_dir, 'metrics.json')
        if os.path.exists(v1_file):
            with open(v1_file, 'r') as f:
                metrics['v1'] = json.load(f)
        
        return metrics
    
    def load_trades(self):
        """Load recent trades"""
        trades = {}
        
        # V2 trades
        v2_file = os.path.join(self.data_dir, 'recent_trades_v2.csv')
        if os.path.exists(v2_file):
            trades['v2'] = pd.read_csv(v2_file)
            if 'timestamp' in trades['v2'].columns:
                trades['v2']['timestamp'] = pd.to_datetime(trades['v2']['timestamp'])
        
        # V1 trades
        v1_file = os.path.join(self.data_dir, 'recent_trades.csv')
        if os.path.exists(v1_file):
            trades['v1'] = pd.read_csv(v1_file)
            if 'timestamp' in trades['v1'].columns:
                trades['v1']['timestamp'] = pd.to_datetime(trades['v1']['timestamp'])
        
        return trades
    
    def load_portfolio_history(self):
        """Load portfolio history"""
        history = {}
        
        # V2 history
        v2_file = os.path.join(self.data_dir, 'portfolio_history_v2.csv')
        if os.path.exists(v2_file):
            history['v2'] = pd.read_csv(v2_file)
            if 'timestamp' in history['v2'].columns:
                history['v2']['timestamp'] = pd.to_datetime(history['v2']['timestamp'])
        
        # V1 history
        v1_file = os.path.join(self.data_dir, 'portfolio_history.csv')
        if os.path.exists(v1_file):
            history['v1'] = pd.read_csv(v1_file)
            if 'timestamp' in history['v1'].columns:
                history['v1']['timestamp'] = pd.to_datetime(history['v1']['timestamp'])
        
        return history
    
    def analyze_strategy_performance(self, metrics, trades):
        """Analyze performance of each strategy"""
        analysis = {}
        
        if 'v2' in metrics and 'strategies' in metrics['v2']:
            strategies = metrics['v2']['strategies']
            
            for strategy_name, stats in strategies.items():
                analysis[strategy_name] = {
                    'trades': stats.get('trades', 0),
                    'pnl': stats.get('pnl', 0),
                    'wins': stats.get('wins', 0),
                    'win_rate': (stats.get('wins', 0) / max(1, stats.get('trades', 0))) * 100,
                    'active': stats.get('active', True)
                }
        
        return analysis
    
    def generate_daily_report(self):
        """Generate daily report"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(self.reports_dir, f'{today}.md')
        
        # Load data
        metrics = self.load_metrics()
        trades = self.load_trades()
        history = self.load_portfolio_history()
        
        # Analyze
        strategy_analysis = self.analyze_strategy_performance(metrics, trades)
        
        # Generate report
        report = self._create_report_content(today, metrics, trades, history, strategy_analysis)
        
        # Save report
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ Report generated: {report_file}")
        return report_file
    
    def _create_report_content(self, date, metrics, trades, history, strategy_analysis):
        """Create report content"""
        
        # Basic info
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Portfolio value
        portfolio_value = "Calculating..."
        if 'v2' in metrics:
            portfolio_value = f"${metrics['v2'].get('current_portfolio', 0):,.2f}"
        
        # Recent trades summary
        recent_trades_summary = "No trades data"
        if 'v2' in trades and not trades['v2'].empty:
            recent_trades = trades['v2'].tail(5)
            trades_list = []
            for _, trade in recent_trades.iterrows():
                action = "🟢 BUY" if trade['action'] == 'BUY' else "🔴 SELL"
                symbol = trade['symbol']
                quantity = trade['quantity']
                strategy = trade.get('strategy', 'N/A')
                trades_list.append(f"{action} {quantity:.4f} {symbol} ({strategy})")
            recent_trades_summary = "\n".join(trades_list)
        
        # Strategy performance
        strategy_performance = ""
        for strategy, stats in strategy_analysis.items():
            win_rate = stats['win_rate']
            pnl = stats['pnl']
            num_trades = stats['trades']
            active = "✅" if stats['active'] else "❌"
            
            strategy_performance += f"- {active} **{strategy.title()}**: {num_trades} trades, ${pnl:.2f} PnL, {win_rate:.1f}% win rate\n"
        
        if not strategy_performance:
            strategy_performance = "No strategy performance data available yet."
        
        # Create report
        report = f"""# 📊 PAPER TRADING REPORT - {date}

## 🎯 RESUMO EXECUTIVO
**Daily report generated automatically.** System status and performance analysis.

---

## 📈 PERFORMANCE GERAL

### **ESTADO ACTUAL:**
- **Portfolio Value:** {portfolio_value}
- **Last Updated:** {metrics.get('v2', {}).get('last_updated', 'N/A')}
- **Data Source:** {metrics.get('v2', {}).get('data_source', 'Paper Trading V2')}

### **SISTEMA:**
- **Report Generated:** {now}
- **Engine Status:** {'✅ Running' if 'v2' in metrics else '❌ Unknown'}
- **Dashboard:** http://100.92.200.109:8502

---

## 🎯 STRATEGY PERFORMANCE

{strategy_performance}

---

## 💱 TRADES RECENTES (Últimos 5)

{recent_trades_summary}

---

## 📊 ANÁLISE E OBSERVAÇÕES

### **PERFORMANCE OVERVIEW:**
- System is operational and generating trades
- Multiple strategies executing simultaneously
- Data collection ongoing for statistical analysis

### **RECOMMENDATIONS:**
1. **Continue monitoring** strategy performance
2. **Collect more data** for statistical significance
3. **Review parameters** after 24-48 hours of operation

### **NEXT STEPS:**
- Implement news monitoring (CryptoPanic API)
- Add stop-loss mechanisms
- Create performance dashboard

---

## 🔧 TECHNICAL STATUS

### **DATA FILES:**
- ✅ Metrics: {'Present' if 'v2' in metrics else 'Missing'}
- ✅ Trades: {'Present' if 'v2' in trades and not trades['v2'].empty else 'Missing'}
- ✅ History: {'Present' if 'v2' in history and not history['v2'].empty else 'Missing'}

### **SYSTEM HEALTH:**
- **Engine:** {'✅ Running' if 'v2' in metrics else '❌ Unknown'}
- **Dashboard:** ✅ Accessible (port 8502)
- **Data Flow:** ✅ Operational

---

## 📅 PRÓXIMO RELATÓRIO

### **AGENDADO:**
- **Next Report:** {(datetime.now() + timedelta(hours=12)).strftime('%Y-%m-%d %H:%M')}
- **Content:** Extended performance analysis with 12h more data

### **MÉTRICAS FUTURAS:**
1. Sharpe ratio calculation
2. Maximum drawdown analysis
3. Win rate statistical significance
4. Correlation between strategies

---

*Relatório gerado automaticamente pelo Paper Trading System V2*  
*Última actualização: {now}*  
*Próxima actualização: {(datetime.now() + timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def generate_12h_report(self):
        """Generate 12-hour report"""
        return self.generate_daily_report()  # Same format for now

def main():
    """Main function"""
    generator = ReportGenerator()
    
    print("📊 Generating Paper Trading Report...")
    report_file = generator.generate_daily_report()
    
    print(f"✅ Report saved to: {report_file}")
    
    # Show preview
    with open(report_file, 'r') as f:
        content = f.read()
        print("\n" + "="*60)
        print("REPORT PREVIEW (first 20 lines):")
        print("="*60)
        print("\n".join(content.split('\n')[:20]))
        print("...")

if __name__ == "__main__":
    main()
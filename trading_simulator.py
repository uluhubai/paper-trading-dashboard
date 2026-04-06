"""
TRADING SIMULATOR - GERA DADOS DINÂMICOS REAIS
"""
import json
import random
import math
from datetime import datetime, timedelta
import os

class TradingSimulator:
    def __init__(self):
        self.state_file = 'trading_state.json'
        self.state = self.load_state()
        self.assets = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'XRP']
        self.strategies = ['Momentum', 'Mean Reversion', 'Breakout']
        
        # Preços base por asset
        self.base_prices = {
            'BTC': 45000,
            'ETH': 3150,
            'ADA': 1.22,
            'SOL': 85,
            'DOT': 6.5,
            'XRP': 0.52
        }
        
        # Inicializar se necessário
        if 'portfolio_value' not in self.state:
            self.state = {
                'portfolio_value': 10000.0,
                'cash': 10000.0,
                'positions': {},
                'trades': [],
                'metrics': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'total_pnl': 0.0,
                    'daily_pnl': 0.0
                },
                'last_update': datetime.now().isoformat()
            }
            self.save_state()
    
    def load_state(self):
        """Carrega estado anterior ou cria novo"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Converter timestamps de volta para datetime
                    for trade in data.get('trades', []):
                        if 'timestamp' in trade:
                            trade['timestamp'] = datetime.fromisoformat(trade['timestamp'])
                    return data
        except Exception as e:
            print(f"Erro a carregar estado: {e}")
        
        return {}
    
    def save_state(self):
        """Guarda estado actual"""
        try:
            # Converter datetime para string para JSON
            state_to_save = self.state.copy()
            state_to_save['trades'] = [
                {**trade, 'timestamp': trade['timestamp'].isoformat() if isinstance(trade['timestamp'], datetime) else trade['timestamp']}
                for trade in state_to_save.get('trades', [])
            ]
            state_to_save['last_update'] = datetime.now().isoformat()
            
            with open(self.state_file, 'w') as f:
                json.dump(state_to_save, f, indent=2)
        except Exception as e:
            print(f"Erro a guardar estado: {e}")
    
    def calculate_current_price(self, asset):
        """Calcula preço actual baseado em hora + random"""
        base = self.base_prices[asset]
        now = datetime.now()
        
        # Variação baseada em hora do dia (padrão sinusoidal)
        hour_factor = math.sin(now.hour / 24 * 2 * math.pi) * 0.05  # ±5%
        
        # Variação baseada em minuto (mais rápida)
        minute_factor = math.sin(now.minute / 60 * 2 * math.pi) * 0.02  # ±2%
        
        # Random factor pequeno
        random_factor = random.uniform(-0.01, 0.01)
        
        current_price = base * (1 + hour_factor + minute_factor + random_factor)
        return round(current_price, 2)
    
    def should_generate_trade(self):
        """Decide se deve gerar nova trade (a cada 2-5 minutos)"""
        if not self.state.get('trades'):
            return True
        
        last_trade_time = None
        for trade in reversed(self.state['trades']):
            if isinstance(trade['timestamp'], datetime):
                last_trade_time = trade['timestamp']
                break
            elif isinstance(trade['timestamp'], str):
                last_trade_time = datetime.fromisoformat(trade['timestamp'])
                break
        
        if not last_trade_time:
            return True
        
        time_since_last = (datetime.now() - last_trade_time).seconds
        # Gera trade a cada 2-5 minutos
        return time_since_last > random.randint(120, 300)
    
    def generate_trade(self):
        """Gera uma nova trade realista"""
        asset = random.choice(self.assets)
        current_price = self.calculate_current_price(asset)
        
        # Decidir acção baseado em performance recente
        recent_trades = [t for t in self.state.get('trades', [])[-5:] if t.get('asset') == asset]
        if recent_trades:
            recent_pnl = sum(t.get('pnl', 0) for t in recent_trades)
            action = 'SELL' if recent_pnl > 0 else 'BUY'
        else:
            action = random.choice(['BUY', 'SELL'])
        
        # Quantidade baseada em preço
        if asset == 'BTC':
            quantity = round(random.uniform(0.01, 0.1), 4)
        elif asset == 'ETH':
            quantity = round(random.uniform(0.1, 0.5), 3)
        else:
            quantity = round(random.uniform(10, 100), 2)
        
        # Calcular PnL (simulado)
        entry_price = current_price * random.uniform(0.95, 1.05)  # ±5% do preço actual
        pnl = 0
        if action == 'SELL':
            pnl = (current_price - entry_price) * quantity
        else:
            pnl = 0  # Ainda não realizado
        
        trade = {
            'id': len(self.state.get('trades', [])) + 1,
            'timestamp': datetime.now(),
            'asset': asset,
            'action': action,
            'quantity': quantity,
            'entry_price': round(entry_price, 2),
            'current_price': current_price,
            'pnl': round(pnl, 2),
            'strategy': random.choice(self.strategies),
            'status': 'EXECUTED'
        }
        
        # Actualizar estado
        self.state.setdefault('trades', []).append(trade)
        
        # Actualizar portfolio
        trade_value = current_price * quantity
        if action == 'BUY':
            self.state['cash'] -= trade_value
            self.state.setdefault('positions', {})[asset] = self.state.get('positions', {}).get(asset, 0) + quantity
        else:
            self.state['cash'] += trade_value
            if asset in self.state.get('positions', {}):
                self.state['positions'][asset] -= quantity
                if self.state['positions'][asset] <= 0:
                    del self.state['positions'][asset]
        
        # Actualizar métricas
        self.state.setdefault('metrics', {})
        self.state['metrics']['total_trades'] = len(self.state['trades'])
        if pnl > 0:
            self.state['metrics']['winning_trades'] = self.state['metrics'].get('winning_trades', 0) + 1
        self.state['metrics']['total_pnl'] = self.state['metrics'].get('total_pnl', 0) + pnl
        
        # Calcular portfolio value
        self.calculate_portfolio_value()
        
        self.save_state()
        return trade
    
    def calculate_portfolio_value(self):
        """Calcula valor total do portfolio"""
        cash = self.state.get('cash', 10000.0)
        positions_value = 0.0
        
        for asset, quantity in self.state.get('positions', {}).items():
            if quantity > 0:
                current_price = self.calculate_current_price(asset)
                positions_value += current_price * quantity
        
        self.state['portfolio_value'] = round(cash + positions_value, 2)
        return self.state['portfolio_value']
    
    def get_current_data(self):
        """Retorna dados actuais para o dashboard"""
        # Gerar trade se necessário
        if self.should_generate_trade():
            self.generate_trade()
        
        # Calcular valores actuais
        portfolio_value = self.calculate_portfolio_value()
        cash = self.state.get('cash', 10000.0)
        
        # Calcular performance por asset
        asset_performance = {}
        for asset in self.assets:
            current_price = self.calculate_current_price(asset)
            base_price = self.base_prices[asset]
            change_pct = ((current_price - base_price) / base_price) * 100
            asset_performance[asset] = {
                'price': current_price,
                'change_pct': round(change_pct, 2),
                'quantity': self.state.get('positions', {}).get(asset, 0),
                'value': round(current_price * self.state.get('positions', {}).get(asset, 0), 2)
            }
        
        # Trades de hoje
        today = datetime.now().date()
        today_trades = [
            t for t in self.state.get('trades', [])
            if isinstance(t.get('timestamp'), (datetime, str)) and 
            (t.get('timestamp').date() if isinstance(t.get('timestamp'), datetime) 
             else datetime.fromisoformat(t.get('timestamp')).date()) == today
        ]
        
        # Trades recentes (últimas 10)
        recent_trades = self.state.get('trades', [])[-10:]
        
        return {
            'portfolio_value': portfolio_value,
            'cash': cash,
            'active_positions': len(self.state.get('positions', {})),
            'today_trades_count': len(today_trades),
            'today_pnl': sum(t.get('pnl', 0) for t in today_trades),
            'total_trades': self.state.get('metrics', {}).get('total_trades', 0),
            'win_rate': (self.state.get('metrics', {}).get('winning_trades', 0) / 
                        max(1, self.state.get('metrics', {}).get('total_trades', 1))) * 100,
            'total_pnl': self.state.get('metrics', {}).get('total_pnl', 0),
            'asset_performance': asset_performance,
            'recent_trades': recent_trades[-5:],  # Últimos 5
            'positions': self.state.get('positions', {}),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }

# Instância global
simulator = TradingSimulator()

if __name__ == '__main__':
    # Testar o simulador
    print("=== TESTE DO TRADING SIMULATOR ===")
    data = simulator.get_current_data()
    print(f"Portfolio Value: ${data['portfolio_value']:,.2f}")
    print(f"Active Positions: {data['active_positions']}")
    print(f"Today's Trades: {data['today_trades_count']}")
    print(f"Today's PnL: ${data['today_pnl']:,.2f}")
    print(f"Last Update: {data['last_update']}")
    
    print("\n=== GERANDO 3 TRADES DE TESTE ===")
    for i in range(3):
        trade = simulator.generate_trade()
        print(f"Trade {i+1}: {trade['asset']} {trade['action']} {trade['quantity']} @ ${trade['current_price']:,.2f}")
    
    print("\n=== DADOS APÓS TRADES ===")
    data = simulator.get_current_data()
    print(f"Portfolio Value: ${data['portfolio_value']:,.2f}")
    print(f"Cash: ${data['cash']:,.2f}")
    print(f"Total PnL: ${data['total_pnl']:,.2f}")

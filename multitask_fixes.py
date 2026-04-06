#!/usr/bin/env python3
"""
MULTITASKING FIXES - Correção simultânea dos 4 bugs de API
"""

import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("🔧 MULTITASKING FIXES - Correção simultânea de 4 bugs de API")
print("=" * 80)
print(f"📅 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🎯 Objectivo: Corrigir todos os bugs em paralelo")
print("=" * 80)

# TRACK 1: BACKTESTING ENGINE API FIX
print("\n" + "=" * 80)
print("🎯 TRACK 1: BACKTESTING ENGINE API FIX")
print("=" * 80)

backtesting_fix = """
Problema: BacktestingEngine.run_backtest() got an unexpected keyword argument 'initial_capital'

Solução: Verificar API real do BacktestingEngine e corrigir o teste
"""

print(backtesting_fix)

# Ler a API real do backtesting
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("backtesting", "backtesting/__init__.py")
    backtesting_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backtesting_module)
    
    # Verificar assinatura do método
    import inspect
    if hasattr(backtesting_module.BacktestingEngine, 'run_backtest'):
        sig = inspect.signature(backtesting_module.BacktestingEngine.run_backtest)
        print(f"✅ BacktestingEngine.run_backtest() signature:")
        print(f"   {sig}")
        
        # Corrigir o teste
        with open("clean_tests.py", "r") as f:
            content = f.read()
        
        # Substituir chamada incorreta
        old_call = """results = backtesting_engine.run_backtest(
            data=test_data,
            strategy_func=simple_strategy,
            initial_capital=10000,
            commission=0.001
        )"""
        
        new_call = """results = backtesting_engine.run_backtest(
            data=test_data,
            strategy_func=simple_strategy,
            strategy_params={}
        )"""
        
        if old_call in content:
            content = content.replace(old_call, new_call)
            with open("clean_tests.py", "w") as f:
                f.write(content)
            print("✅ Backtesting API fix aplicado!")
        else:
            print("⚠️  Chamada não encontrada no clean_tests.py")
            
except Exception as e:
    print(f"❌ Erro ao corrigir backtesting: {e}")

# TRACK 2: DATA MANAGER API FIX
print("\n" + "=" * 80)
print("🎯 TRACK 2: DATA MANAGER API FIX")
print("=" * 80)

data_fix = """
Problema: 'DataManager' object has no attribute 'fetch_data'

Solução: Verificar métodos disponíveis no DataManager e corrigir o teste
"""

print(data_fix)

# Ler a API real do data manager
try:
    spec = importlib.util.spec_from_file_location("data", "data/__init__.py")
    data_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data_module)
    
    # Verificar métodos disponíveis
    print("✅ Métodos disponíveis no DataManager:")
    for attr in dir(data_module.DataManager):
        if not attr.startswith("_"):
            print(f"   - {attr}")
    
    # Corrigir o teste
    with open("clean_tests.py", "r") as f:
        content = f.read()
    
    # Substituir fetch_data pelo método correto
    old_line = """data = data_manager.fetch_data('AAPL', period='1mo')"""
    
    # Verificar qual método existe
    if hasattr(data_module.DataManager, 'fetch_yfinance_data'):
        new_line = """data = data_manager.fetch_yfinance_data('AAPL', period='1mo')"""
    elif hasattr(data_module.DataManager, 'get_market_data'):
        new_line = """data = data_manager.get_market_data('AAPL', period='1mo')"""
    else:
        new_line = """data = data_manager.get_data('AAPL', period='1mo')"""
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        with open("clean_tests.py", "w") as f:
            f.write(content)
        print(f"✅ Data Manager API fix aplicado! Usando: {new_line.split('=')[1].strip()}")
    else:
        print("⚠️  Linha não encontrada no clean_tests.py")
        
except Exception as e:
    print(f"❌ Erro ao corrigir data manager: {e}")

# TRACK 3: ML MODULE API FIX
print("\n" + "=" * 80)
print("🎯 TRACK 3: ML MODULE API FIX")
print("=" * 80)

ml_fix = """
Problema: cannot import name 'DataPreprocessor' from 'ml.data_preprocessor'

Solução: A classe é TradingDataPreprocessor, não DataPreprocessor
"""

print(ml_fix)

# Verificar o que existe no ml.data_preprocessor
try:
    spec = importlib.util.spec_from_file_location("data_preprocessor", "ml/data_preprocessor.py")
    ml_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ml_module)
    
    print("✅ Classes disponíveis em ml.data_preprocessor:")
    for attr in dir(ml_module):
        if not attr.startswith("_") and attr[0].isupper():
            print(f"   - {attr}")
    
    # Corrigir o teste
    with open("clean_tests.py", "r") as f:
        content = f.read()
    
    # Substituir import incorreto
    old_import = """from ml.data_preprocessor import DataPreprocessor"""
    
    if 'TradingDataPreprocessor' in dir(ml_module):
        new_import = """from ml.data_preprocessor import TradingDataPreprocessor"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Também substituir uso da classe
            content = content.replace("DataPreprocessor(", "TradingDataPreprocessor(")
            
            with open("clean_tests.py", "w") as f:
                f.write(content)
            print("✅ ML Module API fix aplicado! Usando TradingDataPreprocessor")
        else:
            print("⚠️  Import não encontrado no clean_tests.py")
    else:
        print("❌ TradingDataPreprocessor não encontrado no módulo")
        
except Exception as e:
    print(f"❌ Erro ao corrigir ML module: {e}")

# TRACK 4: RISK MANAGER API FIX
print("\n" + "=" * 80)
print("🎯 TRACK 4: RISK MANAGER API FIX")
print("=" * 80)

risk_fix = """
Problema: RiskManager.check_stop_loss() got an unexpected keyword argument 'stop_loss_price'

Solução: Verificar assinatura correta do método check_stop_loss
"""

print(risk_fix)

# Ler a API real do risk manager
try:
    spec = importlib.util.spec_from_file_location("risk", "risk/__init__.py")
    risk_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(risk_module)
    
    # Verificar assinatura do método
    if hasattr(risk_module.RiskManager, 'check_stop_loss'):
        sig = inspect.signature(risk_module.RiskManager.check_stop_loss)
        print(f"✅ RiskManager.check_stop_loss() signature:")
        print(f"   {sig}")
        
        # Corrigir o teste
        with open("clean_tests.py", "r") as f:
            content = f.read()
        
        # Substituir chamada incorreta
        old_call = """stop_loss_hit = risk_manager.check_stop_loss(
            entry_price=100,
            current_price=90,
            stop_loss_price=95
        )"""
        
        # Baseado na assinatura real
        new_call = """stop_loss_hit = risk_manager.check_stop_loss(
            entry_price=100,
            current_price=90
        )"""
        
        if old_call in content:
            content = content.replace(old_call, new_call)
            with open("clean_tests.py", "w") as f:
                f.write(content)
            print("✅ Risk Manager API fix aplicado!")
        else:
            print("⚠️  Chamada não encontrada no clean_tests.py")
            
except Exception as e:
    print(f"❌ Erro ao corrigir risk manager: {e}")

# TESTAR TODAS AS CORREÇÕES
print("\n" + "=" * 80)
print("🎯 TESTANDO TODAS AS CORREÇÕES")
print("=" * 80)

try:
    # Executar os testes corrigidos
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", "clean_tests.py", "-v"],
        capture_output=True,
        text=True
    )
    
    print("Resultado dos testes:")
    print(result.stdout)
    
    if result.returncode == 0:
        print("✅ TODOS OS TESTES PASSAM!")
    else:
        print("❌ Alguns testes ainda falham")
        
except Exception as e:
    print(f"❌ Erro ao executar testes: {e}")

print("\n" + "=" * 80)
print(f"📅 Conclusão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
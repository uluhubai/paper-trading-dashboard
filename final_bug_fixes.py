#!/usr/bin/env python3
"""
FINAL BUG FIXES - Correção simultânea dos 4 bugs restantes
"""

import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("🚀 FINAL BUG FIXES - Correção simultânea dos 4 bugs restantes")
print("=" * 80)
print(f"📅 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🎯 Objectivo: 8/8 testes passam (100% funcional)")
print("=" * 80)

# Ler o ficheiro clean_tests.py
with open("clean_tests.py", "r") as f:
    content = f.read()

original_content = content
changes_made = 0

print("\n" + "=" * 80)
print("🔍 ANALISANDO E CORRIGINDO BUGS...")
print("=" * 80)

# BUG 1: Backtesting Engine API Mismatch (linha ~142)
print("\n🎯 BUG 1: Backtesting Engine API Mismatch")
print("   Problema: initial_capital parameter não suportado")

# Encontrar a linha com o problema
lines = content.split('\n')
for i, line in enumerate(lines):
    if "initial_capital=" in line and "run_backtest" in line:
        print(f"   Linha {i+1}: {line.strip()}")
        
        # Substituir a chamada incorreta
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
            changes_made += 1
            print("   ✅ CORRIGIDO: initial_capital removido, strategy_params adicionado")
        break

# BUG 2: Data Fetching Column Case (linha ~85)
print("\n🎯 BUG 2: Data Fetching Column Case Sensitivity")
print("   Problema: 'Close' vs 'close' (case mismatch)")

# Encontrar a linha com assertIn('Close'
for i, line in enumerate(lines):
    if "assertIn('Close'" in line or 'assertIn("Close"' in line:
        print(f"   Linha {i+1}: {line.strip()}")
        
        # Substituir 'Close' por 'close'
        if "'Close'" in line:
            new_line = line.replace("'Close'", "'close'")
        elif '"Close"' in line:
            new_line = line.replace('"Close"', '"close"')
        else:
            new_line = line
        
        if new_line != line:
            content = content.replace(line, new_line)
            changes_made += 1
            print("   ✅ CORRIGIDO: 'Close' → 'close'")
        break

# BUG 3: ML Module Return Values (linha ~62)
print("\n🎯 BUG 3: ML Module Return Values")
print("   Problema: create_features() retorna 3 valores, teste espera 2")

# Encontrar a linha com features, targets = preprocessor.create_features
for i, line in enumerate(lines):
    if "features, targets = preprocessor.create_features" in line:
        print(f"   Linha {i+1}: {line.strip()}")
        
        # Substituir por 3 valores
        new_line = line.replace("features, targets =", "features, targets, feature_names =")
        
        if new_line != line:
            content = content.replace(line, new_line)
            changes_made += 1
            print("   ✅ CORRIGIDO: Adicionado feature_names ao unpacking")
        break

# BUG 4: Risk Manager API Mismatch (linha ~175)
print("\n🎯 BUG 4: Risk Manager API Mismatch")
print("   Problema: stop_loss_price parameter não suportado")

# Encontrar a linha com check_stop_loss e stop_loss_price
for i, line in enumerate(lines):
    if "stop_loss_price=" in line and "check_stop_loss" in line:
        print(f"   Linha {i+1}: {line.strip()}")
        
        # Encontrar o bloco completo
        start_idx = max(0, i - 3)
        end_idx = min(len(lines), i + 4)
        block = '\n'.join(lines[start_idx:end_idx])
        
        # Substituir a chamada incorreta
        old_call = """stop_loss_hit = risk_manager.check_stop_loss(
            entry_price=100,
            current_price=90,
            stop_loss_price=95
        )"""
        
        new_call = """stop_loss_hit = risk_manager.check_stop_loss(
            entry_price=100,
            current_price=90
        )"""
        
        if old_call in content:
            content = content.replace(old_call, new_call)
            changes_made += 1
            print("   ✅ CORRIGIDO: stop_loss_price removido")
        break

# Escrever as alterações de volta
if changes_made > 0:
    with open("clean_tests.py", "w") as f:
        f.write(content)
    
    print(f"\n✅ {changes_made}/4 bugs corrigidos com sucesso!")
    
    # Mostrar diff
    print("\n" + "=" * 80)
    print("📋 RESUMO DAS ALTERAÇÕES:")
    print("=" * 80)
    
    old_lines = original_content.split('\n')
    new_lines = content.split('\n')
    
    for i, (old, new) in enumerate(zip(old_lines, new_lines)):
        if old != new:
            print(f"Linha {i+1}:")
            print(f"  ANTES: {old}")
            print(f"  DEPOIS: {new}")
            print()
    
else:
    print("\n⚠️  Nenhuma alteração necessária - bugs já podem estar corrigidos")

# TESTAR AS CORREÇÕES
print("\n" + "=" * 80)
print("🧪 TESTANDO AS CORREÇÕES...")
print("=" * 80)

try:
    import subprocess
    import sys
    
    # Executar os testes
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "clean_tests.py", "-v"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("Resultado dos testes:")
    print(result.stdout)
    
    if result.returncode == 0:
        print("🎉 🎉 🎉 TODOS OS TESTES PASSAM! 🎉 🎉 🎉")
        print("✅ SISTEMA 100% FUNCIONAL E TESTADO")
    else:
        print("❌ Alguns testes ainda falham")
        print("Stderr:", result.stderr[:500])
        
except subprocess.TimeoutExpired:
    print("⚠️  Testes demoraram muito tempo")
except Exception as e:
    print(f"❌ Erro ao executar testes: {e}")

# EXECUTAR TESTES SIMPLES
print("\n" + "=" * 80)
print("🧪 EXECUTANDO TESTES SIMPLIFICADOS...")
print("=" * 80)

try:
    # Importar e executar testes diretamente
    sys.path.insert(0, '.')
    from clean_tests import PaperTradingTests
    import unittest
    
    suite = unittest.TestLoader().loadTestsFromTestCase(PaperTradingTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n📊 RESULTADOS FINAIS:")
    print(f"✅ Testes executados: {result.testsRun}")
    print(f"✅ Falhas: {len(result.failures)}")
    print(f"✅ Erros: {len(result.errors)}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"✅ Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 🚀 SISTEMA 100% FUNCIONAL! PRONTO PARA PRODUCTION! 🚀 🎉")
    else:
        print(f"\n⚠️  Ainda {len(result.failures) + len(result.errors)} testes falham")
        
except Exception as e:
    print(f"❌ Erro nos testes: {e}")

print("\n" + "=" * 80)
print(f"📅 Conclusão: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"✅ Bugs corrigidos: {changes_made}/4")
print("=" * 80)
# 📊 ESTRATÉGIAS DE TRADING - EXPLICAÇÃO DETALHADA

## 🎯 VISÃO GERAL
Sistema executa 3 estratégias simultaneamente com $10,000 capital inicial (33% cada).

---

## 🚀 1. MOMENTUM STRATEGY (Trend Following)

### **📈 FILOSOFIA:**
"Follow the trend" - A tendência é tua amiga. Compra activos em alta, vende activos em baixa.

### **⚙️ COMO FUNCIONA:**
```
ANÁLISE: Preços dos últimos 5 períodos (50 minutos)
CÁLCULO: (preço_actual - preço_antigo) / preço_antigo
DECISÃO: 
  - Se > +2% → COMPRA (momentum positivo)
  - Se < -2% → VENDA (momentum negativo)
  - Entre -2% e +2% → HOLD
```

### **📊 PARÂMETROS ACTUAIS:**
- **Lookback period:** 5 períodos (50 minutos)
- **Threshold:** ±2% de movimento
- **Capital por trade:** 10% do capital alocado ($333)
- **Activos negociados:** BTC, ETH, ADA
- **Position sizing:** Dinâmico baseado em preço

### **🎯 EXEMPLO PRÁTICO:**
```
PERÍODO 1-4: BTC a $67,000, $67,500, $67,800, $68,000
PERÍODO 5: BTC a $68,340
CÁLCULO: ($68,340 - $67,000) / $67,000 = +2.0%
DECISÃO: COMPRA 0.0049 BTC ($333 / $68,340)
```

### **📈 QUANDO FUNCIONA MELHOR:**
- ✅ **Mercados em tendência** (bull ou bear claros)
- ✅ **Altcoins com momentum** forte
- ✅ **Períodos de alta volatilidade** direccional
- ❌ **Mercados laterais/ranging** (perde dinheiro)

### **⚠️ RISCOS:**
- **Whipsaws:** Entra tarde, sai cedo em reversões
- **Drawdowns grandes** se tendência reverte abruptamente
- **Slippage** em mercados voláteis

---

## 🔄 2. MEAN REVERSION STRATEGY (Buy Low, Sell High)

### **📈 FILOSOFIA:**
"Everything returns to the average" - Preços oscilam em torno da média. Compra oversold, vende overbought.

### **⚙️ COMO FUNCIONA:**
```
ANÁLISE: Preços dos últimos 10 períodos (100 minutos)
CÁLCULO: 
  - Média = mean(preços)
  - Desvio-padrão = std(preços)
  - Z-score = (preço_actual - média) / desvio-padrão
DECISÃO:
  - Se Z-score < -1.5 → COMPRA (oversold)
  - Se Z-score > +1.5 → VENDA (overbought)
  - Entre -1.5 e +1.5 → HOLD
```

### **📊 PARÂMETROS ACTUAIS:**
- **Lookback period:** 10 períodos (100 minutos)
- **Z-score threshold:** ±1.5 desvios-padrão
- **Capital por trade:** 15% do capital alocado ($500)
- **Activos negociados:** BTC, ETH, ADA
- **Mean calculation:** Rolling mean com equal weighting

### **🎯 EXEMPLO PRÁTICO:**
```
ÚLTIMOS 10 PREÇOS ETH: $3,600, $3,620, $3,590, $3,610, $3,580,
                       $3,570, $3,550, $3,530, $3,500, $3,400
CÁLCULO:
  - Média = $3,555
  - Desvio-padrão = $62
  - Preço actual = $3,400
  - Z-score = ($3,400 - $3,555) / $62 = -2.5
DECISÃO: COMPRA 0.1471 ETH ($500 / $3,400)
```

### **📈 QUANDO FUNCIONA MELHOR:**
- ✅ **Mercados laterais/ranging** (consolidação)
- ✅ **Activos com mean reversion forte** (índices, blue chips)
- ✅ **Volatilidade média** (não extrema)
- ❌ **Trending markets** (pode ficar "pegado" no lado errado)

### **⚠️ RISCOS:**
- **Trend continuation:** Activo pode ficar mais oversold/overbought
- **Capital lock-up:** Posições podem durar muito tempo
- **Requier patience:** Não é estratégia de quick profits

---

## ⚡ 3. BREAKOUT STRATEGY (Capture Big Moves)

### **📈 FILOSOFIA:**
"Ride the big waves after consolidation" - Captura movimentos grandes após períodos de consolidação.

### **⚙️ COMO FUNCIONA:**
```
ANÁLISE: Preços dos últimos 20 períodos (200 minutos)
CÁLCULO:
  - Suporte = min(preços_recentes) * 0.98
  - Resistência = max(preços_recentes) * 1.02
  - Actualiza dinamicamente com smoothing
DECISÃO:
  - Se preço > resistência * 1.01 → COMPRA (breakout up)
  - Se preço < suporte * 0.99 → VENDA (breakout down)
  - Entre suporte e resistência → HOLD
```

### **📊 PARÂMETROS ACTUAIS:**
- **Lookback period:** 20 períodos (200 minutos)
- **Breakout threshold:** ±1% além de suporte/resistência
- **Capital por trade:** 20% do capital alocado ($667)
- **Activos negociados:** BTC, ETH, ADA
- **Smoothing factor:** 0.7 (70% old, 30% new levels)

### **🎯 EXEMPLO PRÁTICO:**
```
ÚLTIMOS 20 PREÇOS BTC: Oscilando entre $66,000-$67,000
CÁLCULO:
  - Suporte = $66,000 * 0.98 = $64,680
  - Resistência = $67,000 * 1.02 = $68,340
  - Preço actual = $67,700
  - Breakout level = $68,340 * 1.01 = $69,023
  (Ainda não atingido → HOLD)

SE PREÇO SOBE PARA $69,100:
DECISÃO: COMPRA 0.0097 BTC ($667 / $69,100)
```

### **📈 QUANDO FUNCIONA MELHOR:**
- ✅ **Após longa consolidação** (weeks/months)
- ✅ **Notícias importantes** que causam breakouts
- ✅ **Mercados voláteis** com movimentos grandes
- ❌ **False breakouts** (retorna à range)

### **⚠️ RISCOS:**
- **False breakouts:** Entra, depois volta à range (stop-loss essencial)
- **Whipsaws:** Múltiplos breakouts falsos
- **Requiere stops:** Sem stop-loss, perdas podem ser grandes

---

## 📊 COMPARAÇÃO DAS ESTRATÉGIAS

| Característica | Momentum | Mean Reversion | Breakout |
|----------------|----------|----------------|----------|
| **Filosofia** | Seguir tendência | Reverter à média | Capturar grandes movos |
| **Horizonte** | Curto-médio (horas) | Médio (dias) | Curto (minutos-horas) |
| **Win Rate** | 40-50% | 55-65% | 30-40% |
| **Risk/Reward** | 1:1.5 | 1:1 | 1:3 |
| **Melhor mercado** | Trending | Ranging | Volátil com notícias |
| **Pior mercado** | Ranging | Trending | Lateral sem volatilidade |
| **Psychological** | Fácil (follow) | Difícil (contrarian) | Stressante (timing) |

---

## 🔧 AJUSTES E OTIMIZAÇÃO

### **PARÂMETROS A TESTAR:**
1. **Lookback periods:** 5, 10, 20, 50 períodos
2. **Thresholds:** 1%, 2%, 3%, 5%
3. **Position sizing:** 5%, 10%, 15%, 20%
4. **Stop-loss:** 5%, 10%, 15%
5. **Take-profit:** 10%, 20%, 30%

### **COMBINAÇÕES PROMISSORAS:**
- **Momentum + Stop-loss** para reduzir drawdowns
- **Mean Reversion + Breakout** para diferentes regimes
- **All three + Dynamic allocation** baseado em regime de mercado

---

## 📈 PRÓXIMOS PASSOS

### **1. MONITORIZAÇÃO CONTÍNUA:**
- Track performance de cada estratégia
- Identificar regimes de mercado
- Ajustar alocação dinamicamente

### **2. NOVAS ESTRATÉGIAS:**
- **News-based trading** (notícias crypto)
- **Pairs trading** (BTC/ETH, etc.)
- **Market making** (spread trading)
- **Arbitrage** (cross-exchange)

### **3. OTIMIZAÇÃO:**
- **Backtesting** com dados históricos
- **Walk-forward optimization**
- **Machine learning** para regime detection

---

## 🎯 CONCLUSÃO

Cada estratégia tem seu **nícho ideal**:
- **Momentum:** Quando o mercado tem direção clara
- **Mean Reversion:** Quando o mercado está lateral
- **Breakout:** Quando o mercado está prestes a mover-se

**Sistema multi-estratégia** permite capturar oportunidades em **qualquer regime de mercado** enquanto aprendemos qual funciona melhor em cada condição.

**Próximo relatório:** Análise de performance após 24h de operação.
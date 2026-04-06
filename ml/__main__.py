"""
Main module for ML trading system - integration test
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
import yfinance as yf
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.data_preprocessor import TradingDataPreprocessor
from ml.lstm_model import LSTMTradingModel
from ml.ensemble_model import EnsembleTradingModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ml_pipeline():
    """Test the complete ML pipeline"""
    
    print("🧪 TESTING ML TRADING PIPELINE")
    print("=" * 60)
    
    # 1. Fetch sample data
    print("1. Fetching market data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 2)  # 2 years of data
    
    ticker = yf.Ticker('AAPL')
    data = ticker.history(start=start_date, end=end_date)
    
    if data.empty:
        print("❌ No data fetched")
        return False
    
    print(f"✅ Fetched {len(data)} days of AAPL data")
    
    # 2. Preprocess data
    print("\n2. Preprocessing data...")
    preprocessor = TradingDataPreprocessor()
    prepared_data = preprocessor.prepare_for_training(
        data=data,
        sequence_length=60,
        test_size=0.2,
        scale_method='standard'
    )
    
    print(f"✅ Created {prepared_data['X_train'].shape[0]} training sequences")
    print(f"✅ Created {prepared_data['X_test'].shape[0]} test sequences")
    print(f"✅ Features: {len(prepared_data['feature_columns'])}")
    
    # 3. Train LSTM model
    print("\n3. Training LSTM model...")
    lstm_config = {
        'sequence_length': 60,
        'lstm_units': [50, 50],
        'dropout_rate': 0.2,
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 30,
        'early_stopping_patience': 5
    }
    
    lstm_model = LSTMTradingModel(lstm_config)
    lstm_results = lstm_model.integrate_with_trading_system(data, preprocessor)
    
    print(f"✅ LSTM trained: {lstm_results['training']['epochs_trained']} epochs")
    print(f"✅ LSTM R²: {lstm_results['evaluation']['r2']:.4f}")
    print(f"✅ LSTM Directional Accuracy: {lstm_results['evaluation']['directional_accuracy']:.2%}")
    
    # 4. Train Ensemble model
    print("\n4. Training Ensemble model...")
    
    # Reshape data for ensemble models (flatten sequences)
    X_train_flat = prepared_data['X_train'].reshape(
        prepared_data['X_train'].shape[0],
        -1
    )
    X_test_flat = prepared_data['X_test'].reshape(
        prepared_data['X_test'].shape[0],
        -1
    )
    
    ensemble_model = EnsembleTradingModel()
    ensemble_model.train_models(X_train_flat, prepared_data['y_train'])
    
    # Calculate weights from validation performance
    ensemble_model.calculate_weights_from_performance(
        X_test_flat, prepared_data['y_test']
    )
    
    # Evaluate ensemble
    ensemble_evaluation = ensemble_model.evaluate_models(
        X_test_flat, prepared_data['y_test']
    )
    
    print(f"✅ Ensemble trained: {len(ensemble_model.models)} models")
    print(f"✅ Ensemble R²: {ensemble_evaluation['ensemble']['r2']:.4f}")
    
    # 5. Compare models
    print("\n5. Model Comparison:")
    print("-" * 40)
    
    models_to_compare = {
        'LSTM': lstm_results['evaluation'],
        'Ensemble': ensemble_evaluation['ensemble']
    }
    
    for name, metrics in models_to_compare.items():
        print(f"{name}:")
        print(f"  R²: {metrics['r2']:.4f}")
        print(f"  Directional Accuracy: {metrics['directional_accuracy']:.2%}")
        print(f"  MAE: {metrics['mae']:.6f}")
        if 'total_return_simulated' in metrics:
            print(f"  Simulated Return: {metrics['total_return_simulated']:.2%}")
        print()
    
    # 6. Generate trading signals
    print("\n6. Generating trading signals...")
    
    # LSTM signals
    lstm_signals = lstm_model.create_trading_signals(
        lstm_results['predictions'],
        threshold=0.001
    )
    
    # Ensemble signals
    ensemble_signals = ensemble_model.create_trading_strategy(
        X_test_flat,
        threshold=0.001,
        confidence_weighted=True
    )
    
    print(f"✅ LSTM signals: {np.sum(lstm_signals != 0)} non-zero")
    print(f"✅ Ensemble signals: {np.sum(ensemble_signals != 0)} non-zero")
    
    # 7. Backtest results
    print("\n7. Backtest Results:")
    print("-" * 40)
    
    lstm_backtest = lstm_results['backtest']
    print(f"LSTM Backtest:")
    print(f"  Initial Capital: ${lstm_backtest['initial_capital']:,.2f}")
    print(f"  Final Capital: ${lstm_backtest['final_capital']:,.2f}")
    print(f"  Total Return: {lstm_backtest['total_return']:.2%}")
    print(f"  Sharpe Ratio: {lstm_backtest['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {lstm_backtest['max_drawdown']:.2%}")
    print(f"  Total Trades: {lstm_backtest['total_trades']}")
    
    # 8. Feature importance
    print("\n8. Feature Importance (Top 10):")
    
    feature_importance = ensemble_model.get_feature_importance()
    if feature_importance:
        # Use Random Forest feature importance as example
        rf_importance = feature_importance.get('random_forest')
        if rf_importance is not None:
            top_features = rf_importance.head(10)
            print("Random Forest Top Features:")
            for idx, row in top_features.iterrows():
                feature_idx = int(row['feature'])
                if feature_idx < len(prepared_data['feature_columns']):
                    feature_name = prepared_data['feature_columns'][feature_idx]
                    print(f"  {feature_name}: {row['importance']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ ML PIPELINE TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    return True

def main():
    """Main function"""
    
    try:
        success = test_ml_pipeline()
        if success:
            print("\n🎉 ML Trading System is operational!")
            print("\nNext steps:")
            print("1. Integrate with paper trading system")
            print("2. Add more features and models")
            print("3. Optimize hyperparameters")
            print("4. Deploy to production")
        else:
            print("\n❌ ML Pipeline test failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error in ML pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
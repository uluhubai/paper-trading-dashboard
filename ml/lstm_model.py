"""
LSTM Model for Price Prediction in Trading
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class LSTMTradingModel:
    """LSTM model for financial time series prediction"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'sequence_length': 60,
            'lstm_units': [50, 50],
            'dropout_rate': 0.2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 50,
            'validation_split': 0.1,
        early_stopping_patience = 10
            'early_stopping_patience': 10
        }
        
        self.model = None
        self.history = None
        self.scaler = None
        self.feature_columns = []
        
    def build_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """Build LSTM model architecture"""
        
        model = keras.Sequential()
        
        # First LSTM layer
        model.add(layers.LSTM(
            units=self.config['lstm_units'][0],
            return_sequences=True,
            input_shape=input_shape
        ))
        model.add(layers.Dropout(self.config['dropout_rate']))
        
        # Additional LSTM layers
        for units in self.config['lstm_units'][1:]:
            model.add(layers.LSTM(units=units, return_sequences=True))
            model.add(layers.Dropout(self.config['dropout_rate']))
        
        # Final LSTM layer (no return sequences)
        model.add(layers.LSTM(units=self.config['lstm_units'][-1]))
        model.add(layers.Dropout(self.config['dropout_rate']))
        
        # Dense layers
        model.add(layers.Dense(units=32, activation='relu'))
        model.add(layers.Dense(units=16, activation='relu'))
        
        # Output layer (regression)
        model.add(layers.Dense(units=1, activation='linear'))
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.config['learning_rate'])
        model.compile(
            optimizer=optimizer,
            loss='mse',  # Mean Squared Error for regression
            metrics=['mae', 'mse']  # Mean Absolute Error, Mean Squared Error
        )
        
        logger.info(f"Built LSTM model with {input_shape} input shape")
        model.summary(print_fn=logger.info)
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: np.ndarray = None, y_val: np.ndarray = None) -> Dict[str, Any]:
        """Train the LSTM model"""
        
        if self.model is None:
            input_shape = (X_train.shape[1], X_train.shape[2])
            self.model = self.build_model(input_shape)
        
        # Callbacks
        callbacks = []
        
        # Early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=self.config['early_stopping_patience'],
            restore_best_weights=True,
            verbose=1
        )
        callbacks.append(early_stopping)
        
        # Model checkpoint
        checkpoint = keras.callbacks.ModelCheckpoint(
            'best_lstm_model.h5',
            monitor='val_loss' if X_val is not None else 'loss',
            save_best_only=True,
            verbose=1
        )
        callbacks.append(checkpoint)
        
        # Reduce learning rate on plateau
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss' if X_val is not None else 'loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
        callbacks.append(reduce_lr)
        
        # Train model
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
            validation_split = None
        else:
            validation_data = None
            validation_split = self.config['validation_split']
        
        self.history = self.model.fit(
            X_train, y_train,
            batch_size=self.config['batch_size'],
            epochs=self.config['epochs'],
            validation_data=validation_data,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        # Load best model
        self.model = keras.models.load_model('best_lstm_model.h5')
        
        # Training results
        train_loss = self.history.history['loss'][-1]
        val_loss = self.history.history.get('val_loss', [train_loss])[-1]
        
        logger.info(f"Training completed: train_loss={train_loss:.6f}, val_loss={val_loss:.6f}")
        
        return {
            'train_loss': train_loss,
            'val_loss': val_loss,
            'history': self.history.history,
            'epochs_trained': len(self.history.history['loss'])
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        
        predictions = self.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, predictions)
        
        # Directional accuracy (for trading)
        directional_correct = np.sum(
            (predictions > 0) == (y_test > 0)
        ) / len(y_test)
        
        # Profit simulation (simplified)
        # If prediction > 0, we predict price will go up
        simulated_returns = np.where(predictions > 0, y_test, -y_test)
        total_return = np.prod(1 + simulated_returns) - 1
        
        metrics = {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'directional_accuracy': directional_correct,
            'total_return_simulated': total_return,
            'sharpe_ratio_simulated': np.mean(simulated_returns) / np.std(simulated_returns) * np.sqrt(252)
        }
        
        logger.info(f"Model evaluation: "
                   f"MAE={mae:.6f}, R²={r2:.4f}, "
                   f"Directional Accuracy={directional_correct:.2%}")
        
        return metrics
    
    def predict_future(self, last_sequence: np.ndarray, 
                      steps: int = 5) -> np.ndarray:
        """Predict multiple steps into the future"""
        
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            # Reshape for prediction (batch_size=1, sequence_length, n_features)
            current_sequence_reshaped = current_sequence.reshape(1, -1, current_sequence.shape[1])
            
            # Predict next step
            next_pred = self.model.predict(current_sequence_reshaped, verbose=0)[0, 0]
            predictions.append(next_pred)
            
            # Update sequence (shift and append prediction)
            # Note: This is simplified - in reality we'd need to update all features
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1, 0] = next_pred  # Assuming first feature is price
        
        return np.array(predictions)
    
    def save_model(self, filepath: str = 'lstm_trading_model.h5'):
        """Save model to file"""
        
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str = 'lstm_trading_model.h5'):
        """Load model from file"""
        
        self.model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")
    
    def create_trading_signals(self, predictions: np.ndarray, 
                              threshold: float = 0.0) -> np.ndarray:
        """Create trading signals from predictions"""
        
        # Simple strategy: buy if prediction > threshold, sell if < -threshold
        signals = np.zeros_like(predictions)
        signals[predictions > threshold] = 1  # Buy signal
        signals[predictions < -threshold] = -1  # Sell signal
        
        return signals
    
    def backtest_strategy(self, X_test: np.ndarray, y_test: np.ndarray,
                         initial_capital: float = 10000.0,
                         transaction_cost: float = 0.001) -> Dict[str, Any]:
        """Backtest trading strategy based on model predictions"""
        
        predictions = self.predict(X_test)
        signals = self.create_trading_signals(predictions)
        
        # Initialize backtest
        capital = initial_capital
        position = 0.0
        trades = []
        equity_curve = []
        
        for i in range(len(signals)):
            current_price = 100.0  # Simplified - would use actual prices
            signal = signals[i]
            
            if signal == 1 and position == 0:  # Buy signal, no position
                # Buy
                shares = capital * 0.1 / current_price  # Use 10% of capital
                cost = shares * current_price * (1 + transaction_cost)
                capital -= cost
                position = shares
                
                trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'cost': cost
                })
                
            elif signal == -1 and position > 0:  # Sell signal, have position
                # Sell
                proceeds = position * current_price * (1 - transaction_cost)
                capital += proceeds
                
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'proceeds': proceeds
                })
                
                position = 0.0
            
            # Mark-to-market
            if position > 0:
                capital += position * (current_price - trades[-1]['price'])
            
            equity_curve.append(capital)
        
        # Calculate performance metrics
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        total_return = (equity_curve[-1] - initial_capital) / initial_capital
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
        max_drawdown = self._calculate_max_drawdown(equity_series)
        
        results = {
            'initial_capital': initial_capital,
            'final_capital': equity_curve[-1],
            'total_return': total_return,
            'total_trades': len(trades),
            'winning_trades': sum(1 for trade in trades if trade.get('profit', 0) > 0),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'equity_curve': equity_curve,
            'trades': trades
        }
        
        logger.info(f"Backtest results: {total_return:.2%} return, "
                   f"Sharpe={sharpe_ratio:.2f}, {len(trades)} trades")
        
        return results
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        running_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - running_max) / running_max
        return drawdowns.min()
    
    def integrate_with_trading_system(self, data: pd.DataFrame,
                                    preprocessor: Any) -> Dict[str, Any]:
        """Complete pipeline: preprocess data, train model, generate signals"""
        
        # Prepare data
        prepared_data = preprocessor.prepare_for_training(
            data=data,
            sequence_length=self.config['sequence_length']
        )
        
        # Train model
        training_results = self.train(
            X_train=prepared_data['X_train'],
            y_train=prepared_data['y_train']
        )
        
        # Evaluate model
        evaluation_results = self.evaluate(
            X_test=prepared_data['X_test'],
            y_test=prepared_data['y_test']
        )
        
        # Generate trading signals
        all_predictions = self.predict(
            np.concatenate([prepared_data['X_train'], prepared_data['X_test']])
        )
        signals = self.create_trading_signals(all_predictions)
        
        # Backtest strategy
        backtest_results = self.backtest_strategy(
            X_test=prepared_data['X_test'],
            y_test=prepared_data['y_test']
        )
        
        return {
            'training': training_results,
            'evaluation': evaluation_results,
            'backtest': backtest_results,
            'predictions': all_predictions,
            'signals': signals,
            'prepared_data': prepared_data
        }
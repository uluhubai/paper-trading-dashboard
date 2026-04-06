"""
Ensemble Models for Trading Prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class EnsembleTradingModel:
    """Ensemble of machine learning models for trading prediction"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'models': {
                'random_forest': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'random_state': 42
                },
                'xgboost': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42
                },
                'lightgbm': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42
                },
                'gradient_boosting': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42
                }
            },
            'ensemble_method': 'weighted_average',  # 'average', 'weighted_average', 'stacking'
            'weights': None  # Will be determined based on performance
        }
        
        self.models: Dict[str, Any] = {}
        self.weights: Dict[str, float] = {}
        self.feature_importance: Dict[str, pd.DataFrame] = {}
        
    def initialize_models(self):
        """Initialize all ensemble models"""
        
        # Random Forest
        self.models['random_forest'] = RandomForestRegressor(
            **self.config['models']['random_forest']
        )
        
        # XGBoost
        self.models['xgboost'] = XGBRegressor(
            **self.config['models']['xgboost']
        )
        
        # LightGBM
        self.models['lightgbm'] = LGBMRegressor(
            **self.config['models']['lightgbm']
        )
        
        # Gradient Boosting
        self.models['gradient_boosting'] = GradientBoostingRegressor(
            **self.config['models']['gradient_boosting']
        )
        
        # Optional: CatBoost (can be slow)
        # self.models['catboost'] = CatBoostRegressor(
        #     **self.config['models'].get('catboost', {}),
        #     verbose=0
        # )
        
        logger.info(f"Initialized {len(self.models)} ensemble models")
    
    def train_models(self, X_train: np.ndarray, y_train: np.ndarray,
                    X_val: np.ndarray = None, y_val: np.ndarray = None):
        """Train all ensemble models"""
        
        if not self.models:
            self.initialize_models()
        
        training_results = {}
        
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            if X_val is not None and y_val is not None:
                # Train with validation set for early stopping
                if name == 'xgboost':
                    model.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        verbose=False
                    )
                elif name == 'lightgbm':
                    model.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        verbose=False
                    )
                else:
                    model.fit(X_train, y_train)
            else:
                model.fit(X_train, y_train)
            
            # Get feature importance if available
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = pd.DataFrame({
                    'feature': range(X_train.shape[1]),
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
            
            training_results[name] = {
                'trained': True,
                'n_features': X_train.shape[1]
            }
        
        logger.info("All ensemble models trained")
        return training_results
    
    def predict_individual(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """Get predictions from each individual model"""
        
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(X)
        
        return predictions
    
    def ensemble_predict(self, X: np.ndarray, 
                        method: str = None) -> np.ndarray:
        """Get ensemble prediction"""
        
        if method is None:
            method = self.config['ensemble_method']
        
        individual_predictions = self.predict_individual(X)
        
        if method == 'average':
            # Simple average
            all_predictions = np.array(list(individual_predictions.values()))
            ensemble_pred = np.mean(all_predictions, axis=0)
            
        elif method == 'weighted_average':
            # Weighted average based on model performance
            if not self.weights:
                # Default equal weights
                self.weights = {name: 1.0/len(self.models) for name in self.models.keys()}
            
            weighted_sum = np.zeros(X.shape[0])
            total_weight = 0
            
            for name, pred in individual_predictions.items():
                weight = self.weights.get(name, 1.0/len(self.models))
                weighted_sum += pred * weight
                total_weight += weight
            
            ensemble_pred = weighted_sum / total_weight if total_weight > 0 else np.mean(list(individual_predictions.values()), axis=0)
            
        elif method == 'stacking':
            # Stacking ensemble (would need meta-model)
            # For now, use average
            all_predictions = np.array(list(individual_predictions.values()))
            ensemble_pred = np.mean(all_predictions, axis=0)
            
        else:
            raise ValueError(f"Unknown ensemble method: {method}")
        
        return ensemble_pred
    
    def calculate_weights_from_performance(self, X_val: np.ndarray, y_val: np.ndarray):
        """Calculate model weights based on validation performance"""
        
        individual_predictions = self.predict_individual(X_val)
        weights = {}
        
        for name, pred in individual_predictions.items():
            # Calculate RMSE
            rmse = np.sqrt(mean_squared_error(y_val, pred))
            # Inverse RMSE as weight (better performance = higher weight)
            weights[name] = 1.0 / (rmse + 1e-10)
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        self.weights = {name: w/total_weight for name, w in weights.items()}
        
        logger.info(f"Calculated weights from validation performance: {self.weights}")
    
    def evaluate_models(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Evaluate all models individually and as ensemble"""
        
        evaluation_results = {}
        
        # Individual model evaluation
        individual_predictions = self.predict_individual(X_test)
        
        for name, pred in individual_predictions.items():
            metrics = self._calculate_metrics(y_test, pred)
            evaluation_results[name] = metrics
        
        # Ensemble evaluation
        ensemble_pred = self.ensemble_predict(X_test)
        ensemble_metrics = self._calculate_metrics(y_test, ensemble_pred)
        evaluation_results['ensemble'] = ensemble_metrics
        
        # Compare ensemble vs best individual model
        best_individual = max(
            [(name, metrics['r2']) for name, metrics in evaluation_results.items() if name != 'ensemble'],
            key=lambda x: x[1]
        )
        
        improvement = ensemble_metrics['r2'] - best_individual[1]
        
        logger.info(f"Best individual model: {best_individual[0]} (R²={best_individual[1]:.4f})")
        logger.info(f"Ensemble R²: {ensemble_metrics['r2']:.4f} (improvement: {improvement:.4f})")
        
        return evaluation_results
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        # Directional accuracy
        directional_correct = np.sum(
            (y_pred > 0) == (y_true > 0)
        ) / len(y_true)
        
        # Profit simulation
        simulated_returns = np.where(y_pred > 0, y_true, -y_true)
        total_return = np.prod(1 + simulated_returns) - 1 if len(simulated_returns) > 0 else 0
        
        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'directional_accuracy': directional_correct,
            'total_return_simulated': total_return
        }
    
    def get_feature_importance(self) -> Dict[str, pd.DataFrame]:
        """Get feature importance from all models"""
        
        if not self.feature_importance:
            logger.warning("Feature importance not available. Train models first.")
            return {}
        
        return self.feature_importance
    
    def create_trading_strategy(self, X: np.ndarray, 
                               threshold: float = 0.0,
                               confidence_weighted: bool = False) -> np.ndarray:
        """Create trading strategy based on ensemble predictions"""
        
        ensemble_pred = self.ensemble_predict(X)
        
        if confidence_weighted:
            # Get individual predictions for confidence calculation
            individual_preds = self.predict_individual(X)
            all_preds = np.array(list(individual_preds.values()))
            
            # Confidence = 1 - (standard deviation of predictions)
            confidence = 1 - np.std(all_preds, axis=0) / (np.abs(np.mean(all_preds, axis=0)) + 1e-10)
            confidence = np.clip(confidence, 0, 1)
            
            # Weight signals by confidence
            signals = np.zeros_like(ensemble_pred)
            signals[ensemble_pred > threshold] = confidence[ensemble_pred > threshold]
            signals[ensemble_pred < -threshold] = -confidence[ensemble_pred < -threshold]
            
        else:
            # Simple binary signals
            signals = np.zeros_like(ensemble_pred)
            signals[ensemble_pred > threshold] = 1
            signals[ensemble_pred < -threshold] = -1
        
        return signals
    
    def optimize_hyperparameters(self, X_train: np.ndarray, y_train: np.ndarray,
                                X_val: np.ndarray, y_val: np.ndarray,
                                param_grids: Dict[str, Dict] = None):
        """Optimize hyperparameters for ensemble models"""
        
        from sklearn.model_selection import GridSearchCV
        
        if param_grids is None:
            param_grids = {
                'random_forest': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15],
                    'min_samples_split': [2, 5, 10]
                },
                'xgboost': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.01, 0.1, 0.3]
                }
            }
        
        optimized_models = {}
        
        for name, param_grid in param_grids.items():
            if name not in self.models:
                continue
            
            logger.info(f"Optimizing hyperparameters for {name}...")
            
            # Create base model
            if name == 'random_forest':
                base_model = RandomForestRegressor(random_state=42)
            elif name == 'xgboost':
                base_model = XGBRegressor(random_state=42)
            elif name == 'lightgbm':
                base_model = LGBMRegressor(random_state=42)
            else:
                continue
            
            # Grid search
            grid_search = GridSearchCV(
                estimator=base_model,
                param_grid=param_grid,
                cv=3,
                scoring='neg_mean_squared_error',
                verbose=0,
                n_jobs=-1
            )
            
            grid_search.fit(X_train, y_train)
            
            # Update model with best parameters
            self.models[name] = grid_search.best_estimator_
            optimized_models[name] = {
                'best_params': grid_search.best_params_,
                'best_score': -grid_search.best_score_
            }
            
            logger.info(f"{name} optimized: {grid_search.best_params_}")
        
        return optimized_models
    
    def save_models(self, directory: str = 'ensemble_models'):
        """Save all ensemble models"""
        
        import joblib
        import os
        
        os.makedirs(directory, exist_ok=True)
        
        for name, model in self.models.items():
            filepath = os.path.join(directory, f'{name}.joblib')
            joblib.dump(model, filepath)
        
        # Save weights
        weights_path = os.path.join(directory, 'weights.json')
        import json
        with open(weights_path, 'w') as f:
            json.dump(self.weights, f)
        
        logger.info(f"Ensemble models saved to {directory}")
    
    def load_models(self, directory: str = 'ensemble_models'):
        """Load ensemble models from directory"""
        
        import joblib
        import os
        import json
        
        self.models = {}
        
        for filename in os.listdir(directory):
            if filename.endswith('.joblib'):
                name = filename.replace('.joblib', '')
                filepath = os.path.join(directory, filename)
                self.models[name] = joblib.load(filepath)
        
        # Load weights
        weights_path = os.path.join(directory, 'weights.json')
        if os.path.exists(weights_path):
            with open(weights_path, 'r') as f:
                self.weights = json.load(f)
        
        logger.info(f"Loaded {len(self.models)} ensemble models from {directory}")
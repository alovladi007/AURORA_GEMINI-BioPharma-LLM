"""
SAR (Structure-Activity Relationship) prediction models.

Baseline models for predicting molecular activity from structure.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import joblib
import logging
from pathlib import Path

# ML frameworks
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# Try to import PyTorch
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not installed. Neural network models will not be available.")
    PYTORCH_AVAILABLE = False


class SARPredictor:
    """
    Base class for SAR prediction models.
    """

    def __init__(self, model_type: str = "random_forest", task: str = "classification"):
        """
        Initialize SAR predictor.

        Args:
            model_type: Type of model ("random_forest", "neural_network")
            task: Prediction task ("classification" or "regression")
        """
        self.model_type = model_type
        self.task = task
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the model.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)
            **kwargs: Additional training arguments

        Returns:
            Training metrics
        """
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Predictions
        """
        raise NotImplementedError

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities (classification only).

        Args:
            X: Feature matrix (n_samples, n_features)

        Returns:
            Class probabilities
        """
        raise NotImplementedError

    def save(self, path: str):
        """Save model to disk."""
        raise NotImplementedError

    def load(self, path: str):
        """Load model from disk."""
        raise NotImplementedError


class RandomForestSARPredictor(SARPredictor):
    """
    Random Forest model for SAR prediction.

    Fast, interpretable baseline model using ensemble of decision trees.
    """

    def __init__(self, task: str = "classification", **kwargs):
        """
        Initialize Random Forest SAR predictor.

        Args:
            task: Prediction task ("classification" or "regression")
            **kwargs: Arguments for RandomForest (n_estimators, max_depth, etc.)
        """
        super().__init__(model_type="random_forest", task=task)

        # Default hyperparameters
        rf_kwargs = {
            "n_estimators": kwargs.get("n_estimators", 100),
            "max_depth": kwargs.get("max_depth", 20),
            "min_samples_split": kwargs.get("min_samples_split", 5),
            "min_samples_leaf": kwargs.get("min_samples_leaf", 2),
            "random_state": kwargs.get("random_state", 42),
            "n_jobs": kwargs.get("n_jobs", -1),
        }

        if self.task == "classification":
            self.model = RandomForestClassifier(**rf_kwargs)
        else:
            self.model = RandomForestRegressor(**rf_kwargs)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train Random Forest model.

        Args:
            X: Feature matrix
            y: Target vector
            **kwargs: Additional arguments (unused)

        Returns:
            Training metrics
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)
        self.trained = True

        # Compute training metrics
        train_preds = self.model.predict(X_scaled)

        if self.task == "classification":
            from app.ml.common.metrics import classification_metrics
            train_proba = self.model.predict_proba(X_scaled)[:, 1]
            metrics = classification_metrics(y, train_preds, train_proba)
        else:
            from app.ml.common.metrics import regression_metrics
            metrics = regression_metrics(y, train_preds)

        # Add feature importance
        metrics["feature_importance"] = self.model.feature_importances_.tolist()

        return metrics

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.trained:
            raise ValueError("Model must be trained before prediction")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if self.task != "classification":
            raise ValueError("predict_proba only available for classification")

        if not self.trained:
            raise ValueError("Model must be trained before prediction")

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def save(self, path: str):
        """Save model to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "task": self.task,
            "trained": self.trained,
        }, path)

    def load(self, path: str):
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.task = data["task"]
        self.trained = data["trained"]


class SimpleNeuralNetwork(nn.Module):
    """
    Simple feedforward neural network for SAR prediction.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int] = [256, 128, 64],
        output_dim: int = 1,
        dropout: float = 0.2
    ):
        """
        Initialize neural network.

        Args:
            input_dim: Input feature dimension
            hidden_dims: List of hidden layer sizes
            output_dim: Output dimension
            dropout: Dropout rate
        """
        super().__init__()

        layers = []
        prev_dim = input_dim

        # Hidden layers
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(prev_dim, output_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        """Forward pass."""
        return self.network(x)


class NeuralNetworkSARPredictor(SARPredictor):
    """
    Neural network model for SAR prediction.

    Flexible deep learning model with configurable architecture.
    """

    def __init__(
        self,
        task: str = "classification",
        hidden_dims: List[int] = [256, 128, 64],
        dropout: float = 0.2,
        learning_rate: float = 0.001,
        device: str = "cpu"
    ):
        """
        Initialize neural network SAR predictor.

        Args:
            task: Prediction task ("classification" or "regression")
            hidden_dims: List of hidden layer sizes
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
            device: Device to use ("cpu" or "cuda")
        """
        super().__init__(model_type="neural_network", task=task)

        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required for neural network models")

        self.hidden_dims = hidden_dims
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.device = device if torch.cuda.is_available() or device == "cpu" else "cpu"

        self.model = None
        self.optimizer = None
        self.input_dim = None

    def _build_model(self, input_dim: int):
        """Build neural network architecture."""
        output_dim = 1 if self.task == "regression" else 2

        self.model = SimpleNeuralNetwork(
            input_dim=input_dim,
            hidden_dims=self.hidden_dims,
            output_dim=output_dim,
            dropout=self.dropout
        ).to(self.device)

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.input_dim = input_dim

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        validation_split: float = 0.2,
        early_stopping_patience: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train neural network model.

        Args:
            X: Feature matrix
            y: Target vector
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Fraction for validation
            early_stopping_patience: Patience for early stopping

        Returns:
            Training metrics
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Build model
        if self.model is None:
            self._build_model(X_scaled.shape[1])

        # Split into train/val
        from app.ml.common.utils import split_dataset
        X_train, X_val, y_train, y_val = split_dataset(
            X_scaled, y,
            test_size=validation_split,
            random_state=42
        )

        # Convert to tensors
        X_train_t = torch.FloatTensor(X_train).to(self.device)
        y_train_t = torch.FloatTensor(y_train).to(self.device)
        X_val_t = torch.FloatTensor(X_val).to(self.device)
        y_val_t = torch.FloatTensor(y_val).to(self.device)

        # Loss function
        if self.task == "classification":
            criterion = nn.CrossEntropyLoss()
            y_train_t = y_train_t.long()
            y_val_t = y_val_t.long()
        else:
            criterion = nn.MSELoss()
            y_train_t = y_train_t.unsqueeze(1)
            y_val_t = y_val_t.unsqueeze(1)

        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        history = {"train_loss": [], "val_loss": []}

        for epoch in range(epochs):
            self.model.train()

            # Mini-batch training
            indices = torch.randperm(len(X_train_t))
            epoch_loss = 0.0

            for i in range(0, len(indices), batch_size):
                batch_idx = indices[i:i + batch_size]
                batch_X = X_train_t[batch_idx]
                batch_y = y_train_t[batch_idx]

                # Forward pass
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)

                # Backward pass
                loss.backward()
                self.optimizer.step()

                epoch_loss += loss.item()

            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val_t)
                val_loss = criterion(val_outputs, y_val_t).item()

            history["train_loss"].append(epoch_loss / (len(indices) // batch_size))
            history["val_loss"].append(val_loss)

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    logger.info(f"Early stopping at epoch {epoch + 1}")
                    break

        self.trained = True

        # Compute final metrics
        val_preds = self.predict(X_val)

        if self.task == "classification":
            from app.ml.common.metrics import classification_metrics
            val_proba = self.predict_proba(X_val)[:, 1]
            metrics = classification_metrics(y_val, val_preds, val_proba)
        else:
            from app.ml.common.metrics import regression_metrics
            metrics = regression_metrics(y_val, val_preds)

        metrics["training_history"] = history
        metrics["epochs_trained"] = epoch + 1

        return metrics

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.trained:
            raise ValueError("Model must be trained before prediction")

        self.model.eval()
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)

            if self.task == "classification":
                preds = torch.argmax(outputs, dim=1).cpu().numpy()
            else:
                preds = outputs.squeeze().cpu().numpy()

        return preds

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if self.task != "classification":
            raise ValueError("predict_proba only available for classification")

        if not self.trained:
            raise ValueError("Model must be trained before prediction")

        self.model.eval()
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            probas = torch.softmax(outputs, dim=1).cpu().numpy()

        return probas

    def save(self, path: str):
        """Save model to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "scaler": self.scaler,
            "task": self.task,
            "hidden_dims": self.hidden_dims,
            "dropout": self.dropout,
            "input_dim": self.input_dim,
            "trained": self.trained,
        }, path)

    def load(self, path: str):
        """Load model from disk."""
        checkpoint = torch.load(path, map_location=self.device)
        self.task = checkpoint["task"]
        self.hidden_dims = checkpoint["hidden_dims"]
        self.dropout = checkpoint["dropout"]
        self.input_dim = checkpoint["input_dim"]
        self.scaler = checkpoint["scaler"]
        self.trained = checkpoint["trained"]

        self._build_model(self.input_dim)
        self.model.load_state_dict(checkpoint["model_state_dict"])

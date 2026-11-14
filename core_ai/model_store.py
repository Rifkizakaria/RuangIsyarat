#!/usr/bin/env python
"""Model Store for RuangIsyarat - Lazy load & cache model .pkl per standar."""

import os
from pathlib import Path
from typing import Optional, Dict, Any

import pickle
import numpy as np


class ModelStore:
    """Singleton-style model store for lazy loading models."""
    
    _instance = None
    _models: Dict[str, Any] = {}
    _label_encoders: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def init(self):
        """Initialize the model store (called from UI)."""
        if self._initialized:
            return
        self._initialized = True
        
    @classmethod
    def get_model(cls, std_standar: str = "ASL"):
        """Get model for the specified standard, loading if necessary."""
        if std_standar in cls._models:
            return cls._models[std_standar], cls._label_encoders.get(std_standar)
        
        # Load model
        model, label_encoder = cls._load_model(std_standar)
        
        if model is not None:
            cls._models[std_standar] = model
            cls._label_encoders[std_standar] = label_encoder
            
        return model, label_encoder
    
    @classmethod
    def _load_model(cls, std_standar: str = "ASL") -> tuple:
        """
        Load model from .pkl file.
        
        Returns:
            Tuple of (model_object, label_encoder_or_None)
        """
        models_dir = Path(__file__).resolve().parents[1] / "models"
        model_path = models_dir / f"model_{std_standar.lower()}.pkl"
        
        if not model_path.exists():
            print(f"Model tidak ditemukan: {model_path}")
            return None, None
        
        try:
            with open(model_path, "rb") as f:
                data = pickle.load(f)
            
            # Handle different pickle formats
            if isinstance(data, dict):
                model = data.get("model")
                label_encoder = data.get("label_encoder",
                    data.get("classes", None))
                # If no explicit label_encoder, try to extract classes
                if label_encoder is None and "classes" in data:
                    label_encoder = data["classes"]
            else:
                model = data
                label_encoder = None
            
            return model, label_encoder
            
        except Exception as e:
            print(f"Error loading model {std_standar}: {e}")
            return None, None
    
    @classmethod
    def reload_model(cls, std_standar: str = "ASL"):
        """Force reload model for the specified standard."""
        if std_standar in cls._models:
            del cls._models[std_standar]
        if std_standar in cls._label_encoders:
            del cls._label_encoders[std_standar]
        return cls.get_model(std_standar)
    
    @classmethod
    def list_available_standars(cls) -> list:
        """List standars for which models are available."""
        available = []
        models_dir = Path(__file__).resolve().parents[1] / "models"
        if models_dir.exists():
            for pkl_file in models_dir.glob("*.pkl"):
                # Extract standard name from filename
                name = pkl_file.stem.replace("model_", "")
                available.append(name)
        return available


# Convenience function for UI
def init_model_store():
    """Initialize the global model store."""
    ModelStore()


if __name__ == "__main__":
    # Quick test
    store = ModelStore()
    model, encoder = store.get_model("ASL")
    if model is not None:
        print(f"Model ASL berhasil dimuat: {type(model).__name__}")
    else:
        print("Model ASL belum tersedia (harap latih model terlebih dahulu)")
"""Modelos de ML supervisados para el resultado 1X2.

Detecta en tiempo de ejecución qué librerías hay instaladas y elige el mejor
clasificador disponible siguiendo este orden de preferencia:

    LightGBM  →  XGBoost  →  RandomForest (scikit-learn)  →  None

Si ninguna está disponible (p. ej. entorno mínimo sin red) o el modelo no se ha
entrenado, `predict_proba` devuelve None y el motor cae a los modelos
estadísticos (Poisson/Dixon-Coles/ELO). Así el sistema nunca se rompe.
"""
from __future__ import annotations

import logging
import os
import pickle
from dataclasses import dataclass

logger = logging.getLogger("protipster.ml")

# Clases del objetivo 1X2.
CLASSES = ["home", "draw", "away"]


def _detect_backend():
    """Devuelve (nombre, factory) del mejor clasificador disponible."""
    try:
        import lightgbm as lgb  # noqa: F401

        def make():
            from lightgbm import LGBMClassifier

            return LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, verbose=-1)

        return "lightgbm", make
    except ImportError:
        pass
    try:
        import xgboost as xgb  # noqa: F401

        def make():
            from xgboost import XGBClassifier

            return XGBClassifier(
                n_estimators=300, learning_rate=0.05, max_depth=4,
                objective="multi:softprob", num_class=3, eval_metric="mlogloss",
            )

        return "xgboost", make
    except ImportError:
        pass
    try:
        from sklearn.ensemble import RandomForestClassifier  # noqa: F401

        def make():
            from sklearn.ensemble import RandomForestClassifier

            return RandomForestClassifier(n_estimators=400, max_depth=8, n_jobs=-1, random_state=42)

        return "random_forest", make
    except ImportError:
        pass
    return "none", None


@dataclass
class MLPredictor:
    """Envoltorio uniforme sobre el clasificador disponible."""

    model_name: str = "none"
    _model: object | None = None
    _trained: bool = False

    @classmethod
    def create(cls) -> "MLPredictor":
        name, factory = _detect_backend()
        model = factory() if factory else None
        return cls(model_name=name, _model=model)

    @property
    def available(self) -> bool:
        return self._model is not None

    @property
    def ready(self) -> bool:
        return self.available and self._trained

    def train(self, X: list[list[float]], y: list[int]) -> dict:
        """Entrena con vectores de features X y etiquetas y (0/1/2)."""
        if not self.available:
            return {"trained": False, "reason": "no ML backend installed"}
        try:
            self._model.fit(X, y)
            self._trained = True
            return {"trained": True, "backend": self.model_name, "samples": len(X)}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fallo entrenando %s: %s", self.model_name, exc)
            return {"trained": False, "reason": str(exc)}

    def predict_proba(self, features: list[float]) -> dict[str, float] | None:
        """Probabilidades {home,draw,away} o None si no se puede predecir."""
        if not self.ready:
            return None
        try:
            proba = self._model.predict_proba([features])[0]
            classes = list(getattr(self._model, "classes_", [0, 1, 2]))
            out = {CLASSES[c]: float(proba[i]) for i, c in enumerate(classes)}
            # Asegura las tres claves.
            for k in CLASSES:
                out.setdefault(k, 0.0)
            return out
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fallo prediciendo con %s: %s", self.model_name, exc)
            return None

    # --- Persistencia ---
    def save(self, path: str) -> bool:
        if not self.ready:
            return False
        try:
            with open(path, "wb") as fh:
                pickle.dump({"name": self.model_name, "model": self._model}, fh)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo guardar el modelo: %s", exc)
            return False

    @classmethod
    def load(cls, path: str) -> "MLPredictor | None":
        if not os.path.exists(path):
            return None
        try:
            with open(path, "rb") as fh:
                data = pickle.load(fh)
            return cls(model_name=data["name"], _model=data["model"], _trained=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo cargar el modelo: %s", exc)
            return None


# Instancia perezosa compartida (singleton ligero).
_PREDICTOR: MLPredictor | None = None
MODEL_PATH = os.environ.get("PROTIPSTER_MODEL_PATH", "ml_model.pkl")


def get_predictor() -> MLPredictor:
    global _PREDICTOR
    if _PREDICTOR is None:
        _PREDICTOR = MLPredictor.load(MODEL_PATH) or MLPredictor.create()
    return _PREDICTOR

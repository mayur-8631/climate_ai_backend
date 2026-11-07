from typing import Any, Dict, Protocol
from app.schemas.prediction import HazardDetail


class HazardModelProtocol(Protocol):
    """Protocol defining the interface for Lokesh's ML hazard models."""

    def predict(self, features: Dict[str, Any]) -> HazardDetail:
        """Takes an environmental feature dictionary and outputs a normalized HazardDetail."""
        ...


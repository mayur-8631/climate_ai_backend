import math
from typing import Optional


class EnvironmentalNormalizer:
    """Calculates derived meteorological indices and normalizes hazard indicators."""

    @staticmethod
    def calculate_heat_index(temp_c: float, humidity: float) -> float:
        """
        Calculate Heat Index in Celsius using the NOAA / Steadman-Rothfusz regression equation.
        """
        if temp_c < 20.0 or humidity < 10.0:
            return temp_c

        # Convert to Fahrenheit for standard Rothfusz coefficients
        t = (temp_c * 9.0 / 5.0) + 32.0
        r = humidity

        # Simple formula test
        hi_simple = 0.5 * (t + 61.0 + ((t - 68.0) * 1.2) + (r * 0.094))
        if hi_simple < 80.0:
            hi_f = hi_simple
        else:
            hi_f = (
                -42.379
                + 2.04901523 * t
                + 10.14333127 * r
                - 0.22475541 * t * r
                - 0.00683783 * (t ** 2)
                - 0.05481717 * (r ** 2)
                + 0.00122874 * (t ** 2) * r
                + 0.00085282 * t * (r ** 2)
                - 0.00000199 * (t ** 2) * (r ** 2)
            )

        # Convert back to Celsius
        return round((hi_f - 32.0) * 5.0 / 9.0, 1)

    @staticmethod
    def normalize_to_scale(value: float, min_val: float, max_val: float) -> float:
        """Clamps and scales any continuous variable to 0.0 - 100.0."""
        if max_val <= min_val:
            return 0.0
        scaled = ((value - min_val) / (max_val - min_val)) * 100.0
        return max(0.0, min(100.0, round(scaled, 1)))


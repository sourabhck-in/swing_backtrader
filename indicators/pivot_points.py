import numpy as np
from indicators.base_indicator import BaseIndicator


class PivotPointsIndicator(BaseIndicator):
    """
    Pivot Points Indicator

    Identifies significant high and low points in price data
    that can be used for support/resistance and stop loss placement.
    """

    def __init__(self, lookback_period=10, threshold=0.01):
        """
        Initialize Pivot Points indicator

        Parameters:
        -----------
        lookback_period : int, optional
            Lookback period for identifying pivots, by default 10
        threshold : float, optional
            Percentage threshold for pivot point identification, by default 0.01 (1%)
        """
        super().__init__(
            "PivotPoints", {"lookback_period": lookback_period, "threshold": threshold}
        )
        self.lookback_period = lookback_period
        self.threshold = threshold

    def calculate(self, data):
        """
        Calculate Pivot Points

        Parameters:
        -----------
        data : dict
            Price data with 'high', 'low' arrays

        Returns:
        --------
        dict
            Dictionary with 'pivot_highs' and 'pivot_lows' arrays
            (containing 1.0 at pivot points, 0.0 elsewhere)
        """
        # Extract data
        high = np.array(data["high"], dtype=float)
        low = np.array(data["low"], dtype=float)

        # Handle None/NaN values
        high = np.array([h if h is not None else np.nan for h in high])
        low = np.array([l if l is not None else np.nan for l in low])

        # Initialize result arrays with zeros
        size = len(high)
        pivot_highs = np.zeros(size)
        pivot_lows = np.zeros(size)

        # We need at least 2*lookback_period + 1 data points for proper calculation
        if size < 2 * self.lookback_period + 1:
            return {"pivot_highs": pivot_highs, "pivot_lows": pivot_lows}

        # Find pivot highs
        for i in range(self.lookback_period, size - self.lookback_period):
            # Skip if current bar is NaN
            if np.isnan(high[i]):
                continue

            # Check if higher than all bars in lookback period
            is_pivot_high = True
            for j in range(i - self.lookback_period, i):
                if not np.isnan(high[j]) and high[j] >= high[i]:
                    is_pivot_high = False
                    break

            if is_pivot_high:
                for j in range(i + 1, i + self.lookback_period + 1):
                    if not np.isnan(high[j]) and high[j] > high[i]:
                        is_pivot_high = False
                        break

            if is_pivot_high:
                pivot_highs[i] = 1.0

        # Find pivot lows
        for i in range(self.lookback_period, size - self.lookback_period):
            # Skip if current bar is NaN
            if np.isnan(low[i]):
                continue

            # Check if lower than all bars in lookback period
            is_pivot_low = True
            for j in range(i - self.lookback_period, i):
                if not np.isnan(low[j]) and low[j] <= low[i]:
                    is_pivot_low = False
                    break

            if is_pivot_low:
                for j in range(i + 1, i + self.lookback_period + 1):
                    if not np.isnan(low[j]) and low[j] < low[i]:
                        is_pivot_low = False
                        break

            if is_pivot_low:
                pivot_lows[i] = 1.0

        return {"pivot_highs": pivot_highs, "pivot_lows": pivot_lows}

import numpy as np
from indicators.base_indicator import BaseIndicator


class RelativeStrengthIndicator(BaseIndicator):
    """
    Relative Strength Indicator

    Compares the performance of a security to a benchmark (e.g., Nifty)
    over a specified lookback period.
    """

    def __init__(self, lookback_period=10):
        """
        Initialize Relative Strength indicator

        Parameters:
        -----------
        lookback_period : int, optional
            Lookback period for calculating relative strength, by default 10
        """
        super().__init__("RelativeStrength", {"lookback_period": lookback_period})
        self.lookback_period = lookback_period

    def calculate(self, data, benchmark_data):
        """
        Calculate Relative Strength values

        Parameters:
        -----------
        data : dict
            Price data for the security with 'close' array
        benchmark_data : dict
            Price data for the benchmark with 'close' array

        Returns:
        --------
        numpy.ndarray
            Relative strength values
        """
        # Extract close prices
        close = np.array(data["close"], dtype=float)
        benchmark_close = np.array(benchmark_data["close"], dtype=float)

        # Handle None/NaN values
        close = np.array([c if c is not None else np.nan for c in close])
        benchmark_close = np.array(
            [c if c is not None else np.nan for c in benchmark_close]
        )

        # Initialize result with NaN values
        size = len(close)
        rel_strength = np.full(size, np.nan)

        # Calculate indicators only where we have enough data
        if size <= self.lookback_period:
            return rel_strength

        # Calculate relative strength
        for i in range(self.lookback_period, size):
            if (
                np.isnan(close[i])
                or np.isnan(close[i - self.lookback_period])
                or np.isnan(benchmark_close[i])
                or np.isnan(benchmark_close[i - self.lookback_period])
            ):
                rel_strength[i] = np.nan
                continue

            # Calculate percentage change for security and benchmark
            security_change = (close[i] / close[i - self.lookback_period]) - 1
            benchmark_change = (
                benchmark_close[i] / benchmark_close[i - self.lookback_period]
            ) - 1

            # Calculate relative strength (difference in performance)
            rel_strength[i] = security_change - benchmark_change

        return rel_strength

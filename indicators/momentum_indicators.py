import numpy as np
from indicators.base_indicator import BaseIndicator


class RSIIndicator(BaseIndicator):
    """
    Relative Strength Index (RSI) indicator

    Measures the speed and change of price movements on a scale from 0 to 100.
    RSI is considered overbought when above 70 and oversold when below 30.
    """

    def __init__(self, period=14):
        """
        Initialize RSI indicator

        Parameters:
        -----------
        period : int, optional
            Lookback period, by default 14
        """
        super().__init__("RSI", {"period": period})
        self.period = period

    def calculate(self, data):
        """
        Calculate RSI values

        Parameters:
        -----------
        data : dict
            Price data with 'close' array

        Returns:
        --------
        numpy.ndarray
            RSI values array
        """
        # Extract close prices
        close = np.array(data["close"], dtype=float)

        # Handle None/NaN values
        close = np.array([c if c is not None else np.nan for c in close])

        # Initialize result with NaN values
        size = len(close)
        rsi = np.full(size, np.nan)

        # Calculate indicators only where we have enough data
        if size <= self.period:
            return rsi

        # Calculate price changes
        delta = np.zeros(size)
        for i in range(1, size):
            if np.isnan(close[i]) or np.isnan(close[i - 1]):
                delta[i] = np.nan
            else:
                delta[i] = close[i] - close[i - 1]

        # Calculate gains and losses
        gains = np.copy(delta)
        losses = np.copy(delta)
        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = -losses  # Make losses positive

        # Calculate average gains and losses
        avg_gain = np.zeros(size)
        avg_loss = np.zeros(size)

        # First values are just the average of the first n periods
        avg_gain[self.period] = np.nansum(gains[1 : self.period + 1]) / self.period
        avg_loss[self.period] = np.nansum(losses[1 : self.period + 1]) / self.period

        # Calculate remaining values using the formula
        for i in range(self.period + 1, size):
            if np.isnan(gains[i]) or np.isnan(losses[i]):
                avg_gain[i] = np.nan
                avg_loss[i] = np.nan
                continue

            avg_gain[i] = (avg_gain[i - 1] * (self.period - 1) + gains[i]) / self.period
            avg_loss[i] = (
                avg_loss[i - 1] * (self.period - 1) + losses[i]
            ) / self.period

        # Calculate RS and RSI
        for i in range(self.period, size):
            if np.isnan(avg_gain[i]) or np.isnan(avg_loss[i]):
                rsi[i] = np.nan
            elif avg_loss[i] == 0:
                rsi[i] = 100
            else:
                rs = avg_gain[i] / avg_loss[i]
                rsi[i] = 100 - (100 / (1 + rs))

        return rsi


class StochasticIndicator(BaseIndicator):
    """
    Stochastic Oscillator

    Measures the level of the close relative to the high-low range over a given period.
    Consists of %K (fast stochastic) and %D (slow stochastic).
    """

    def __init__(self, k_period=14, d_period=3, slowing=1):
        """
        Initialize Stochastic Oscillator

        Parameters:
        -----------
        k_period : int, optional
            %K period, by default 14
        d_period : int, optional
            %D period, by default 3
        slowing : int, optional
            Slowing period, by default 1
        """
        super().__init__(
            "Stochastic",
            {"k_period": k_period, "d_period": d_period, "slowing": slowing},
        )
        self.k_period = k_period
        self.d_period = d_period
        self.slowing = slowing

    def calculate(self, data):
        """
        Calculate Stochastic Oscillator values

        Parameters:
        -----------
        data : dict
            Price data with 'high', 'low', 'close' arrays

        Returns:
        --------
        dict
            Dictionary with 'k' and 'd' arrays
        """
        # Extract data
        high = np.array(data["high"], dtype=float)
        low = np.array(data["low"], dtype=float)
        close = np.array(data["close"], dtype=float)

        # Handle None/NaN values
        high = np.array([h if h is not None else np.nan for h in high])
        low = np.array([l if l is not None else np.nan for l in low])
        close = np.array([c if c is not None else np.nan for c in close])

        # Initialize result arrays with NaN values
        size = len(close)
        k_values = np.full(size, np.nan)
        d_values = np.full(size, np.nan)

        # Calculate indicators only where we have enough data
        if size <= self.k_period:
            return {"k": k_values, "d": d_values}

        # Calculate %K values
        for i in range(self.k_period - 1, size):
            # Get the range for the period
            start_idx = max(0, i - (self.k_period - 1))
            period_high = np.nanmax(high[start_idx : i + 1])
            period_low = np.nanmin(low[start_idx : i + 1])

            if np.isnan(period_high) or np.isnan(period_low) or np.isnan(close[i]):
                k_values[i] = np.nan
                continue

            if period_high == period_low:  # Avoid division by zero
                k_values[i] = 100
            else:
                k_values[i] = 100 * (close[i] - period_low) / (period_high - period_low)

        # Apply slowing if specified
        if self.slowing > 1:
            slowed_k = np.full(size, np.nan)
            for i in range(self.k_period + self.slowing - 2, size):
                slowed_k[i] = np.nanmean(k_values[i - (self.slowing - 1) : i + 1])
            k_values = slowed_k

        # Calculate %D values (simple moving average of %K)
        for i in range(self.k_period + self.d_period - 2, size):
            d_values[i] = np.nanmean(k_values[i - (self.d_period - 1) : i + 1])

        return {"k": k_values, "d": d_values}

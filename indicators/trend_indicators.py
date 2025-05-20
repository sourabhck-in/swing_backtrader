import numpy as np
from indicators.base_indicator import BaseIndicator


class ADXIndicator(BaseIndicator):
    """
    Average Directional Index (ADX) indicator

    Measures the strength of a trend (regardless of direction).
    Also calculates +DI and -DI for determining trend direction.
    """

    def __init__(self, period=14):
        """
        Initialize ADX indicator

        Parameters:
        -----------
        period : int, optional
            Lookback period, by default 14
        """
        super().__init__("ADX", {"period": period})
        self.period = period

    def calculate(self, data):
        """
        Calculate ADX, +DI, and -DI values

        Parameters:
        -----------
        data : dict
            Price data with 'high', 'low', 'close' arrays

        Returns:
        --------
        dict
            Dictionary with 'adx', 'pdi', 'mdi' arrays
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
        size = len(high)
        adx = np.full(size, np.nan)
        pdi = np.full(size, np.nan)
        mdi = np.full(size, np.nan)

        # Calculate indicators only where we have enough data
        if size <= self.period:
            return {"adx": adx, "pdi": pdi, "mdi": mdi}

        # Calculate True Range
        tr = np.zeros(size)
        tr[0] = high[0] - low[0]  # First TR is just the range
        for i in range(1, size):
            if np.isnan(high[i]) or np.isnan(low[i]) or np.isnan(close[i - 1]):
                tr[i] = np.nan
                continue

            hl = high[i] - low[i]
            hpc = abs(high[i] - close[i - 1])
            lpc = abs(low[i] - close[i - 1])
            tr[i] = max(hl, hpc, lpc)

        # Calculate +DM and -DM
        plus_dm = np.zeros(size)
        minus_dm = np.zeros(size)

        for i in range(1, size):
            if (
                np.isnan(high[i])
                or np.isnan(high[i - 1])
                or np.isnan(low[i])
                or np.isnan(low[i - 1])
            ):
                plus_dm[i] = np.nan
                minus_dm[i] = np.nan
                continue

            up_move = high[i] - high[i - 1]
            down_move = low[i - 1] - low[i]

            if up_move > down_move and up_move > 0:
                plus_dm[i] = up_move
            else:
                plus_dm[i] = 0

            if down_move > up_move and down_move > 0:
                minus_dm[i] = down_move
            else:
                minus_dm[i] = 0

        # Calculate smoothed TR, +DM, -DM
        smoothed_tr = np.zeros(size)
        smoothed_plus_dm = np.zeros(size)
        smoothed_minus_dm = np.zeros(size)

        # First value is sum of first n periods
        for i in range(1, self.period + 1):
            if i < size:
                if not np.isnan(tr[i]):
                    smoothed_tr[self.period] += tr[i]
                if not np.isnan(plus_dm[i]):
                    smoothed_plus_dm[self.period] += plus_dm[i]
                if not np.isnan(minus_dm[i]):
                    smoothed_minus_dm[self.period] += minus_dm[i]

        # Calculate remaining values using Wilder's smoothing
        for i in range(self.period + 1, size):
            if np.isnan(tr[i]) or np.isnan(plus_dm[i]) or np.isnan(minus_dm[i]):
                smoothed_tr[i] = np.nan
                smoothed_plus_dm[i] = np.nan
                smoothed_minus_dm[i] = np.nan
                continue

            smoothed_tr[i] = (
                smoothed_tr[i - 1] - (smoothed_tr[i - 1] / self.period) + tr[i]
            )
            smoothed_plus_dm[i] = (
                smoothed_plus_dm[i - 1]
                - (smoothed_plus_dm[i - 1] / self.period)
                + plus_dm[i]
            )
            smoothed_minus_dm[i] = (
                smoothed_minus_dm[i - 1]
                - (smoothed_minus_dm[i - 1] / self.period)
                + minus_dm[i]
            )

        # Calculate +DI and -DI
        for i in range(self.period, size):
            if np.isnan(smoothed_tr[i]) or smoothed_tr[i] == 0:
                pdi[i] = np.nan
                mdi[i] = np.nan
                continue

            pdi[i] = 100 * (smoothed_plus_dm[i] / smoothed_tr[i])
            mdi[i] = 100 * (smoothed_minus_dm[i] / smoothed_tr[i])

        # Calculate DX and ADX
        dx = np.zeros(size)
        for i in range(self.period, size):
            if np.isnan(pdi[i]) or np.isnan(mdi[i]) or (pdi[i] + mdi[i]) == 0:
                dx[i] = np.nan
                continue

            dx[i] = 100 * (abs(pdi[i] - mdi[i]) / (pdi[i] + mdi[i]))

        # First ADX value is average of first n DX values
        adx[2 * self.period - 1] = np.nanmean(dx[self.period : 2 * self.period])

        # Calculate remaining ADX values
        for i in range(2 * self.period, size):
            if np.isnan(dx[i]) or np.isnan(adx[i - 1]):
                adx[i] = np.nan
                continue

            adx[i] = ((self.period - 1) * adx[i - 1] + dx[i]) / self.period

        return {"adx": adx, "pdi": pdi, "mdi": mdi}

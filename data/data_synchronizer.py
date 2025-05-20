import pandas as pd
import numpy as np


class SynchronizedData:
    """
    Class for storing and accessing synchronized multi-timeframe data
    """

    def __init__(self, symbols, start_date, end_date):
        """
        Initialize the synchronized data container

        Parameters:
        -----------
        symbols : list
            List of symbols/security IDs
        start_date : str
            Start date in format 'YYYY-MM-DD'
        end_date : str
            End date in format 'YYYY-MM-DD'
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.timestamps = []  # Master unified timeline
        self.data = {}  # Main data container

        # Initialize the data structure
        self._initialize_data_structure()

    def _initialize_data_structure(self):
        """Initialize the nested data structure for all symbols"""
        for symbol in self.symbols:
            self.data[symbol] = {
                # Raw price data by timeframe
                "D": {"open": [], "high": [], "low": [], "close": [], "volume": []},
                "4H": {"open": [], "high": [], "low": [], "close": [], "volume": []},
                # Indicators by timeframe
                "indicators": {"D": {}, "4H": {}},  # Daily indicators  # 4H indicators
            }

    def load_and_synchronize(self, raw_data):
        """
        Load data from loaded dataframes and synchronize timeframes

        Parameters:
        -----------
        raw_data : dict
            Dictionary of raw data with symbol, timeframe structure

        Returns:
        --------
        self
            Returns self for method chaining
        """
        # Step 1: Create master timeline from 4H data
        self._create_master_timeline(raw_data)

        # Step 2: Synchronize data to master timeline
        self._synchronize_data(raw_data)

        return self

    def _create_master_timeline(self, raw_data):
        """
        Create master timeline from all timeframe data timestamps

        Parameters:
        -----------
        raw_data : dict
            Dictionary of raw data with symbol, timeframe structure
        """

        # Get all unique timestamps from both 4H and daily data across all symbols
        all_timestamps = set()

        for symbol in self.symbols:
            # Add all 4H timestamps
            if "4H" in raw_data[symbol]:
                all_timestamps.update(raw_data[symbol]["4H"].index)

            # For daily data, create timestamps for both 9:15 and 13:15 for each day
            if "D" in raw_data[symbol]:
                daily_df = raw_data[symbol]["D"]
                for day_dt in daily_df.index:
                    day_date = day_dt.date()
                    # Add 9:15 timestamp
                    morning_ts = pd.Timestamp(day_date) + pd.Timedelta(
                        hours=9, minutes=15
                    )
                    all_timestamps.add(morning_ts)
                    # Add 13:15 timestamp
                    afternoon_ts = pd.Timestamp(day_date) + pd.Timedelta(
                        hours=13, minutes=15
                    )
                    all_timestamps.add(afternoon_ts)

        # Sort timestamps and store as master timeline
        self.timestamps = sorted(all_timestamps)

    def _synchronize_data(self, raw_data):
        """
        Synchronize all data to master timeline

        Parameters:
        -----------
        raw_data : dict
            Dictionary of raw data with symbol, timeframe structure
        """
        for symbol in self.symbols:
            # Get raw dataframes
            df_4h = raw_data[symbol]["4H"]
            df_daily = raw_data[symbol]["D"]

            # For each timestamp in master timeline
            for ts in self.timestamps:
                # Process 4H data (direct mapping if exists)
                if ts in df_4h.index:
                    for col in ["open", "high", "low", "close", "volume"]:
                        self.data[symbol]["4H"][col].append(df_4h.loc[ts, col])
                else:
                    # Fill with None if 4H data doesn't exist for this timestamp
                    for col in ["open", "high", "low", "close", "volume"]:
                        self.data[symbol]["4H"][col].append(None)

                # Process daily data - find matching daily candle by date
                day_date = ts.date()

                # Find the daily candle for this date
                daily_matches = df_daily.loc[df_daily.index.date == day_date]

                if not daily_matches.empty:
                    # Found a matching daily candle
                    for col in ["open", "high", "low", "close", "volume"]:
                        self.data[symbol]["D"][col].append(daily_matches.iloc[0][col])
                else:
                    # No daily data for this date
                    for col in ["open", "high", "low", "close", "volume"]:
                        self.data[symbol]["D"][col].append(None)

    def add_indicator(self, symbol, timeframe, indicator_name, values):
        """
        Add calculated indicator values to the synchronized data

        Parameters:
        -----------
        symbol : str
            Symbol/Security ID
        timeframe : str
            Timeframe ('D' or '4H')
        indicator_name : str
            Name of the indicator
        values : list
            List of indicator values aligned with timestamps
        """
        # Ensure values list is the same length as timestamps
        if len(values) != len(self.timestamps):
            raise ValueError(
                f"Indicator values length ({len(values)}) does not match timestamps length ({len(self.timestamps)})"
            )

        # Add indicator values to the data structure
        self.data[symbol]["indicators"][timeframe][indicator_name] = values

    # Data access methods
    def get_price_data(self, symbol, timeframe, field="close"):
        """Get price data for a specific symbol, timeframe, and field"""
        return self.data[symbol][timeframe][field]

    def get_indicator(self, symbol, timeframe, indicator_name):
        """Get indicator data for a specific symbol, timeframe, and indicator"""
        return self.data[symbol]["indicators"][timeframe].get(indicator_name, None)

    def get_at_index(self, index, symbol, timeframe, field="close"):
        """Get data at a specific index position"""
        if 0 <= index < len(self.timestamps):
            return self.data[symbol][timeframe][field][index]
        return None

    def get_at_timestamp(self, timestamp, symbol, timeframe, field="close"):
        """Get data at a specific timestamp"""
        if timestamp in self.timestamps:
            idx = self.timestamps.index(timestamp)
            return self.get_at_index(idx, symbol, timeframe, field)
        return None

    def get_latest(self, current_index, symbol, timeframe, field="close"):
        """Get latest available data up to current_index"""
        # Find the latest non-None value
        for i in range(current_index, -1, -1):
            value = self.get_at_index(i, symbol, timeframe, field)
            if value is not None:
                return value
        return None

    def get_current_timeframe_data(self, index, symbol, timeframe):
        """Get all price data for a specific index and timeframe"""
        result = {}
        for field in ["open", "high", "low", "close", "volume"]:
            result[field] = self.get_at_index(index, symbol, timeframe, field)
        return result

    def get_indicator_values(self, index, symbol, timeframe=None):
        """Get all indicator values for a specific index"""
        result = {}

        if timeframe:
            # Get indicators for specific timeframe
            for indicator in self.data[symbol]["indicators"][timeframe]:
                result[indicator] = self.data[symbol]["indicators"][timeframe][
                    indicator
                ][index]
        else:
            # Get indicators for all timeframes
            result = {"D": {}, "4H": {}}
            for tf in ["D", "4H"]:
                for indicator in self.data[symbol]["indicators"][tf]:
                    result[tf][indicator] = self.data[symbol]["indicators"][tf][
                        indicator
                    ][index]

        return result

    def get_last_n_values(self, index, symbol, timeframe, field, n):
        """Get last n values up to index"""
        values = []
        count = 0
        current = index

        while count < n and current >= 0:
            value = self.get_at_index(current, symbol, timeframe, field)
            if value is not None:
                values.append(value)
                count += 1
            current -= 1

        return list(reversed(values))

    def get_trading_days_between(self, start_index, end_index):
        """Calculate number of trading days between two indices"""
        # Group timestamps by date to count unique trading days
        days = set()
        for i in range(start_index, end_index + 1):
            days.add(self.timestamps[i].date())
        return len(days)

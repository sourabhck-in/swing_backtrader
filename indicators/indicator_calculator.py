from indicators.indicator_factory import IndicatorFactory
from indicators.trend_indicators import ADXIndicator
from indicators.momentum_indicators import RSIIndicator, StochasticIndicator
from indicators.relative_strength import RelativeStrengthIndicator
from indicators.pivot_points import PivotPointsIndicator


class IndicatorCalculator:
    """
    Calculate and manage indicators for synchronized data

    Provides a high-level interface for calculating multiple indicators
    on synchronized multi-timeframe data.
    """

    def __init__(self, sync_data):
        """
        Initialize with synchronized data

        Parameters:
        -----------
        sync_data : object
            Synchronized multi-timeframe data object
        """
        self.sync_data = sync_data
        self.factory = IndicatorFactory()
        self._register_indicators()

    def _register_indicators(self):
        """Register all available indicators"""
        # Register trend indicators
        self.factory.register_indicator("adx", ADXIndicator)

        # Register momentum indicators
        self.factory.register_indicator("rsi", RSIIndicator)
        self.factory.register_indicator("stoch", StochasticIndicator)

        # Register relative strength
        self.factory.register_indicator("rel_strength", RelativeStrengthIndicator)

        # Register pivot points
        self.factory.register_indicator("pivot_points", PivotPointsIndicator)

    def calculate_for_symbol(self, symbol, timeframe, indicator_type, **params):
        """
        Calculate indicator for a specific symbol and timeframe

        Parameters:
        -----------
        symbol : str
            Symbol/security ID
        timeframe : str
            Timeframe ('D' or '4H')
        indicator_type : str
            Type of indicator to calculate
        **params : dict
            Parameters for the indicator

        Returns:
        --------
        array-like
            Calculated indicator values
        """
        # Print what we're calculating
        print(f"Calculating {indicator_type} for {symbol} on {timeframe} timeframe...")

        try:
            # Special handling for relative strength indicator
            if indicator_type == "rel_strength":
                if "benchmark_symbol" not in params:
                    raise ValueError(
                        "benchmark_symbol parameter required for relative_strength indicator"
                    )

                benchmark_symbol = params.pop("benchmark_symbol")

                # Get price data for the symbol and benchmark
                price_data = {
                    "open": self.sync_data.get_price_data(symbol, timeframe, "open"),
                    "high": self.sync_data.get_price_data(symbol, timeframe, "high"),
                    "low": self.sync_data.get_price_data(symbol, timeframe, "low"),
                    "close": self.sync_data.get_price_data(symbol, timeframe, "close"),
                    "volume": self.sync_data.get_price_data(
                        symbol, timeframe, "volume"
                    ),
                }

                benchmark_data = {
                    "open": self.sync_data.get_price_data(
                        benchmark_symbol, timeframe, "open"
                    ),
                    "high": self.sync_data.get_price_data(
                        benchmark_symbol, timeframe, "high"
                    ),
                    "low": self.sync_data.get_price_data(
                        benchmark_symbol, timeframe, "low"
                    ),
                    "close": self.sync_data.get_price_data(
                        benchmark_symbol, timeframe, "close"
                    ),
                    "volume": self.sync_data.get_price_data(
                        benchmark_symbol, timeframe, "volume"
                    ),
                }

                # Check for valid data
                if any(x is None for x in price_data.values()) or any(
                    x is None for x in benchmark_data.values()
                ):
                    print(f"Warning: Missing data for {symbol} or {benchmark_symbol}")
                    return None

                # Create indicator and calculate
                indicator = self.factory.create_indicator(indicator_type, **params)
                result = indicator.calculate(price_data, benchmark_data)

            else:
                # Get price data for the symbol
                price_data = {
                    "open": self.sync_data.get_price_data(symbol, timeframe, "open"),
                    "high": self.sync_data.get_price_data(symbol, timeframe, "high"),
                    "low": self.sync_data.get_price_data(symbol, timeframe, "low"),
                    "close": self.sync_data.get_price_data(symbol, timeframe, "close"),
                    "volume": self.sync_data.get_price_data(
                        symbol, timeframe, "volume"
                    ),
                }

                # Check for valid data
                if any(x is None for x in price_data.values()):
                    print(f"Warning: Missing data for {symbol}")
                    return None

                # Calculate indicator
                result = self.factory.calculate_indicator(
                    indicator_type, price_data, **params
                )

            # Store result in synchronized data
            if result is not None:
                if isinstance(result, dict):
                    # Multiple values (like ADX with pdi, mdi)
                    for key, values in result.items():
                        indicator_name = (
                            f"{indicator_type}_{key}"
                            if key != indicator_type
                            else indicator_type
                        )
                        self.sync_data.add_indicator(
                            symbol, timeframe, indicator_name, values
                        )
                        print(
                            f"Added indicator: {symbol} {timeframe} {indicator_name} with {len(values)} values"
                        )
                else:
                    # Single value array
                    self.sync_data.add_indicator(
                        symbol, timeframe, indicator_type, result
                    )
                    print(
                        f"Added indicator: {symbol} {timeframe} {indicator_type} with {len(result)} values"
                    )

            return result

        except Exception as e:
            print(
                f"Error calculating {indicator_type} for {symbol} on {timeframe}: {e}"
            )
            import traceback

            traceback.print_exc()
            return None

    def calculate_all_indicators(self, config):
        """
        Calculate all indicators defined in configuration

        Parameters:
        -----------
        config : dict
            Dictionary with indicator configuration
            Example:
            {
                'D': [
                    {'type': 'adx', 'symbols': ['1333'], 'params': {'period': 14}},
                    {'type': 'rsi', 'symbols': ['1333', '1660'], 'params': {'period': 14}}
                ],
                '4H': [
                    {'type': 'rsi', 'symbols': ['1333', '1660'], 'params': {'period': 14}},
                    {'type': 'stoch', 'symbols': ['1333'], 'params': {'k_period': 14, 'd_period': 3}}
                ]
            }
        """
        for timeframe, indicators in config.items():
            for indicator_config in indicators:
                indicator_type = indicator_config["type"]
                symbols = indicator_config.get("symbols", self.sync_data.symbols)
                params = indicator_config.get("params", {})

                # Special case for relative strength (needs benchmark)
                if indicator_type == "rel_strength":
                    benchmark_symbol = params.get("benchmark_symbol")
                    if not benchmark_symbol:
                        raise ValueError(
                            "benchmark_symbol required for rel_strength indicator"
                        )

                # Calculate for each symbol
                for symbol in symbols:
                    try:
                        self.calculate_for_symbol(
                            symbol, timeframe, indicator_type, **params
                        )
                    except Exception as e:
                        print(
                            f"Error calculating {indicator_type} for {symbol} on {timeframe}: {e}"
                        )

import numpy as np
import pandas as pd
from config.bt_parameters import SYMBOLS, START_DATE, END_DATE, NIFTY_ID
from data.data_processor import prepare_backtest_data
from indicators.indicator_calculator import IndicatorCalculator


def test_indicators():
    """Test indicator calculation"""
    # Load synchronized data
    print("Loading and synchronizing data...")
    sync_data = prepare_backtest_data(SYMBOLS, START_DATE, END_DATE)

    # Print initial data info
    print(f"Synchronized data contains {len(sync_data.timestamps)} timestamps")
    print(f"First timestamp: {sync_data.timestamps[0]}")
    print(f"Last timestamp: {sync_data.timestamps[-1]}")

    # Initialize indicator calculator
    calculator = IndicatorCalculator(sync_data)

    # Define indicator configuration
    indicator_config = {
        "D": [
            {"type": "adx", "symbols": SYMBOLS, "params": {"period": 14}},
            {"type": "rsi", "symbols": SYMBOLS, "params": {"period": 14}},
        ],
        "4H": [
            {"type": "rsi", "symbols": SYMBOLS, "params": {"period": 14}},
            {
                "type": "stoch",
                "symbols": SYMBOLS,
                "params": {"k_period": 14, "d_period": 3},
            },
        ],
    }

    # Calculate all indicators
    print("\nCalculating indicators...")
    try:
        # Calculate all indicators in configuration
        calculator.calculate_all_indicators(indicator_config)

        # Calculate relative strength for non-Nifty symbols against Nifty
        for symbol in SYMBOLS:
            if symbol != NIFTY_ID:
                print(
                    f"Calculating relative strength for {symbol} against {NIFTY_ID}..."
                )
                calculator.calculate_for_symbol(
                    symbol,
                    "D",
                    "rel_strength",
                    benchmark_symbol=NIFTY_ID,
                    lookback_period=10,
                )

        # Calculate pivots for 4H timeframe
        for symbol in SYMBOLS:
            print(f"Calculating pivot points for {symbol} on 4H timeframe...")
            calculator.calculate_for_symbol(
                symbol, "4H", "pivot_points", lookback_period=5
            )

    except Exception as e:
        print(f"Error calculating indicators: {e}")
        import traceback

        traceback.print_exc()

    # Print summary of calculated indicators
    print("\nSummary of calculated indicators:")
    for symbol in SYMBOLS:
        print(f"\nIndicators for {symbol}:")

        for timeframe in ["D", "4H"]:
            print(f"  {timeframe} timeframe:")

            # Check if indicators exist for this symbol and timeframe
            if timeframe not in sync_data.data[symbol]["indicators"]:
                print(f"    No indicators found")
                continue

            for indicator_name in sync_data.data[symbol]["indicators"][timeframe]:
                values = sync_data.data[symbol]["indicators"][timeframe][indicator_name]
                non_nan_values = [
                    v for v in values if v is not None and not np.isnan(v)
                ]

                if non_nan_values:
                    min_val = min(non_nan_values)
                    max_val = max(non_nan_values)
                    avg_val = sum(non_nan_values) / len(non_nan_values)
                    print(
                        f"    {indicator_name}: {len(non_nan_values)} values, range: {min_val:.2f} to {max_val:.2f}, avg: {avg_val:.2f}"
                    )
                else:
                    print(f"    {indicator_name}: No valid values")

    # Find a valid sample index for demonstration
    sample_symbol = SYMBOLS[0]
    valid_index = None

    # Try to find a valid index from any available indicator
    for timeframe in ["D", "4H"]:
        if valid_index is not None:
            break

        if timeframe not in sync_data.data[sample_symbol]["indicators"]:
            continue

        for indicator_name in sync_data.data[sample_symbol]["indicators"][timeframe]:
            values = sync_data.data[sample_symbol]["indicators"][timeframe][
                indicator_name
            ]

            if values is None:
                continue

            for i in range(len(values) - 1, 0, -1):
                if (
                    i < len(values)
                    and values[i] is not None
                    and not np.isnan(values[i])
                ):
                    valid_index = i
                    break

            if valid_index is not None:
                break

    # Print sample values if we found a valid index
    if valid_index is not None:
        timestamp = sync_data.timestamps[valid_index]
        print(
            f"\nSample indicator values for {sample_symbol} at index {valid_index} ({timestamp}):"
        )

        # Print available indicator values
        for timeframe in ["D", "4H"]:
            print(f"  {timeframe} timeframe:")

            if timeframe not in sync_data.data[sample_symbol]["indicators"]:
                print("    No indicators available")
                continue

            for indicator_name in sync_data.data[sample_symbol]["indicators"][
                timeframe
            ]:
                values = sync_data.data[sample_symbol]["indicators"][timeframe][
                    indicator_name
                ]

                if (
                    values is not None
                    and valid_index < len(values)
                    and values[valid_index] is not None
                    and not np.isnan(values[valid_index])
                ):
                    print(f"    {indicator_name}: {values[valid_index]:.2f}")
    else:
        print("\nNo valid indicator values found for demonstration")

    return sync_data, calculator


if __name__ == "__main__":
    test_indicators()

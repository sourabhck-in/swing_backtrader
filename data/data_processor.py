import pandas as pd
import numpy as np
from data.data_loader import load_data
from data.data_synchronizer import SynchronizedData
from config.bt_parameters import TIMEFRAMES


def load_and_process_data(symbols, start_date, end_date, data_path="./data"):
    """
    Main function to load, process and synchronize data for backtesting

    Parameters:
    -----------
    symbols : list
        List of symbols/security IDs to process
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    data_path : str, optional
        Path to data directory, by default './data'

    Returns:
    --------
    SynchronizedData
        Synchronized data object with aligned timeframes
    """
    # Step 1: Load raw data for all symbols
    raw_data = {}
    for symbol in symbols:
        try:
            raw_data[symbol] = load_data(
                symbol=symbol,
                timeframes=TIMEFRAMES,
                start_date=start_date,
                end_date=end_date,
            )
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            # Skip this symbol or handle the error as needed

    # Step 2: Create synchronized data structure
    sync_data = SynchronizedData(
        symbols=list(raw_data.keys()), start_date=start_date, end_date=end_date
    )

    # Step 3: Synchronize the data
    sync_data.load_and_synchronize(raw_data)

    # Step 4: Return the synchronized data
    return sync_data


def prepare_backtest_data(symbols, start_date, end_date):
    """
    Prepare data for backtesting with additional preprocessing

    Parameters:
    -----------
    symbols : list
        List of symbols/security IDs to process
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'

    Returns:
    --------
    SynchronizedData
        Fully processed synchronized data ready for backtesting
    """
    # Load and synchronize data
    sync_data = load_and_process_data(symbols, start_date, end_date)

    # Additional preprocessing could be added here
    # For example:
    # - Handle missing data
    # - Calculate additional derived fields
    # - Apply data quality checks

    return sync_data

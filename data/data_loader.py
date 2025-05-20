import os
import pandas as pd
from config.bt_parameters import DATA_PATH


def load_data(symbol, timeframes, start_date, end_date):
    """
    Load data for a specific symbol and timeframes
    """
    data = {}

    # Debug for date range
    print(f"Loading data for {symbol} from {start_date} to {end_date}")

    for timeframe in timeframes:
        # Map internal timeframe codes to file name conventions
        file_suffix = {"D": "daily", "4H": "4h"}.get(timeframe, timeframe.lower())

        file_path = f"{DATA_PATH}/historical/{symbol}/{symbol}_{file_suffix}.csv"

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")

        # Load the CSV file
        df = pd.read_csv(file_path)

        # Debug: Print original date range in the file
        print(
            f"File {file_path} has date range: {df['datetime'].min()} to {df['datetime'].max()}"
        )

        # Convert datetime column
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Debug: Print parsed date range
        print(
            f"After parsing, date range: {df['datetime'].min()} to {df['datetime'].max()}"
        )

        # Set datetime as index
        df.set_index("datetime", inplace=True)

        # Filter by date range if provided
        if start_date and end_date:
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)

            # Add full day to end date to include the entire day
            end_dt = end_dt + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

            # Debug: Print filter range
            print(f"Filtering data from {start_dt} to {end_dt}")

            # Filter
            df = df[(df.index >= start_dt) & (df.index <= end_dt)]

            # Debug: Print filtered date range
            print(
                f"After filtering, date range: {df.index.min() if not df.empty else 'Empty'} to {df.index.max() if not df.empty else 'Empty'}"
            )

        # Store in the data dictionary
        data[timeframe] = df

    return data

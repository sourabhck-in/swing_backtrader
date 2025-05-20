import pandas as pd
from config.bt_parameters import SYMBOLS, START_DATE, END_DATE
from data.data_processor import prepare_backtest_data


def main():
    # Debug configuration
    print(f"Using configuration:")
    print(f"  SYMBOLS: {SYMBOLS}")
    print(f"  START_DATE: {START_DATE}")
    print(f"  END_DATE: {END_DATE}")

    # Load and synchronize data
    print(f"\nLoading data for symbols: {SYMBOLS}")
    sync_data = prepare_backtest_data(SYMBOLS, START_DATE, END_DATE)

    # Print basic information
    print(f"\nSynchronized data contains {len(sync_data.timestamps)} timestamps")
    print(f"First timestamp: {sync_data.timestamps[0]}")
    print(f"Last timestamp: {sync_data.timestamps[-1]}")

    # Check if the last timestamp exists in the original data
    symbol = SYMBOLS[0]
    print("\nVerifying data integrity:")

    # Load original 4H data for comparison
    file_path = f"./data/historical/{symbol}/{symbol}_4h.csv"
    df_4h = pd.read_csv(file_path)
    df_4h["datetime"] = pd.to_datetime(df_4h["datetime"])

    # Check if last timestamp in sync_data exists in original data
    last_ts = sync_data.timestamps[-1]
    if last_ts in df_4h["datetime"].values:
        print(f"Last timestamp {last_ts} EXISTS in original 4H data")
    else:
        print(f"WARNING: Last timestamp {last_ts} DOES NOT EXIST in original 4H data!")

    # Count how many timestamps in the original data
    print(f"Original 4H data contains {len(df_4h)} rows")
    print(f"Synchronized data contains {len(sync_data.timestamps)} timestamps")

    if len(sync_data.timestamps) > len(df_4h):
        print(f"WARNING: Synchronized data has MORE timestamps than original data!")
    elif len(sync_data.timestamps) < len(df_4h):
        print(f"WARNING: Synchronized data has FEWER timestamps than original data!")

    # Print a sample of the synchronized data
    print("\nSample data:")
    print("Timestamp | 4H Close | Daily Close")
    print("-" * 40)

    # Print first few entries
    print("FIRST 5 ENTRIES:")
    for i in range(min(5, len(sync_data.timestamps))):
        timestamp = sync_data.timestamps[i]
        h4_close = sync_data.get_at_index(i, symbol, "4H", "close")
        d_close = sync_data.get_at_index(i, symbol, "D", "close")
        print(f"{timestamp} | {h4_close} | {d_close}")

    # Print last few entries
    print("\nLAST 5 ENTRIES:")
    for i in range(max(0, len(sync_data.timestamps) - 5), len(sync_data.timestamps)):
        timestamp = sync_data.timestamps[i]
        h4_close = sync_data.get_at_index(i, symbol, "4H", "close")
        d_close = sync_data.get_at_index(i, symbol, "D", "close")
        print(f"{timestamp} | {h4_close} | {d_close}")


if __name__ == "__main__":
    main()

# Configuration Parameters for Backtesting

# Securities to backtest
NIFTY_ID = "1333"  # ID of the Nifty index
SYMBOLS = ["1333", "1660", "2303"]  # Example security IDs

# Timeframes
TIMEFRAMES = ["D", "4H"]

# Date range for backtesting
START_DATE = "2025-01-01"
END_DATE = "2025-05-15"

# Data path
DATA_PATH = "./data"

# Indicator parameters
ADX_PERIOD = 14
ADX_WEAK_THRESHOLD = 20
ADX_STRONG_THRESHOLD = 30

RSI_PERIOD = 14
RSI_OVERSOLD = 40
RSI_OVERBOUGHT = 60

STOCH_K_PERIOD = 14
STOCH_D_PERIOD = 3
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80

PIVOT_LOOKBACK = 5
REL_STRENGTH_LOOKBACK = 10

# Portfolio parameters
INITIAL_CAPITAL = 100000
COMMISSION_RATE = 0.001  # 0.1%
SLIPPAGE = 0.0005  # 0.05%

# Position sizing parameters
FULL_POSITION_SIZE = 0.05  # 5% of capital for full position
REDUCED_POSITION_SIZE = 0.025  # 2.5% of capital for reduced position

# Risk management
MAX_DAYS_IN_TRADE = 10  # Maximum number of trading days to hold a position

# Performance tracking
SAVE_RESULTS = True
RESULTS_PATH = "./results/"
PLOT_EQUITY_CURVE = True

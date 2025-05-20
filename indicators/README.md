# Indicator Module

This module provides a flexible framework for calculating technical indicators for backtesting and strategy development.

## Features

- Clean separation between indicator calculation and signal generation
- Customizable indicator parameters
- Support for standard and custom indicators
- Easy integration with the backtesting framework

## Key Indicators

### Trend Indicators

- **ADX/DI System**: Measures trend strength and direction
  - ADX: Average Directional Index (strength)
  - +DI: Plus Directional Indicator (uptrend)
  - -DI: Minus Directional Indicator (downtrend)

### Momentum Indicators

- **RSI**: Relative Strength Index, measures momentum
- **Stochastic Oscillator**: Compares closing price to its price range

### Relative Strength

- **Relative Strength**: Compares security performance to benchmark (e.g., Nifty)

### Support/Resistance

- **Pivot Points**: Identifies significant highs and lows for support/resistance

## Usage

### Basic Usage

```python
# Initialize indicator calculator
calculator = IndicatorCalculator(sync_data)

# Calculate single indicator
calculator.calculate_for_symbol('1333', 'D', 'adx', period=14)

# Calculate indicator with multiple outputs
adx_results = calculator.calculate_for_symbol('1333', 'D', 'adx', period=14)
# Access outputs: adx_results['adx'], adx_results['pdi'], adx_results['mdi']

# Calculate relative strength
calculator.calculate_for_symbol('1660', 'D', 'rel_strength', 
                               benchmark_symbol='1333',
                               lookback_period=10)

Calculate Multiple Indicators

# Define indicator configuration
indicator_config = {
    'D': [
        {'type': 'adx', 'symbols': ['1333', '1660'], 'params': {'period': 14}},
        {'type': 'rsi', 'symbols': ['1333'], 'params': {'period': 14}}
    ],
    '4H': [
        {'type': 'rsi', 'symbols': ['1333', '1660'], 'params': {'period': 14}},
        {'type': 'stoch', 'symbols': ['1333'], 'params': {'k_period': 14, 'd_period': 3}}
    ]
}

# Calculate all indicators in configuration
calculator.calculate_all_indicators(indicator_config)

Accessing Indicator Values

# Get indicator value at specific index
adx_value = sync_data.get_indicator('1333', 'D', 'adx_adx')[index]
pdi_value = sync_data.get_indicator('1333', 'D', 'adx_pdi')[index]
mdi_value = sync_data.get_indicator('1333', 'D', 'adx_mdi')[index]
rsi_value = sync_data.get_indicator('1333', '4H', 'rsi')[index]

Extending with Custom Indicators
To add custom indicators:

Create a new class inheriting from BaseIndicator
Implement the calculate method
Register the indicator in the IndicatorCalculator

Example:

class CustomIndicator(BaseIndicator):
    def __init__(self, param1=10):
        super().__init__("CustomIndicator", {"param1": param1})
        self.param1 = param1
        
    def calculate(self, data):
        # Implementation
        return result

# Register the custom indicator
calculator.factory.register_indicator('custom', CustomIndicator)

```


With these files implemented, we've created a robust indicator system for your backtesting framework. The indicator system:

1. Calculates technical values only, no signal generation (as you requested)
2. Provides all the indicators needed for your swing trading strategy
3. Integrates seamlessly with your synchronized data structure
4. Offers flexibility for adding new indicators or customizing existing ones

You can now use this system to calculate the necessary indicators for your strategy, interpret them for signal generation, and implement the rest of your backtesting framework.

Would you like me to explain any particular part of the implementation in more detail, or would you like to move on to implementing the signal generation component next?

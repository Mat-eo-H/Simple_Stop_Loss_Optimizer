# Matt's Simple Stop Loss Optimizer

A Python tool for analyzing trading data to find the optimal stop loss setting by simulating profit/loss at different MAE (Maximum Adverse Excursion) thresholds.

## What It Does

The optimizer:
1. Loads your historical trade data from a CSV file
2. Calculates baseline metrics (no stop loss applied)
3. Simulates profit/loss at different MAE percentile thresholds
4. Shows which stop loss setting would have maximized profit
5. Displays improvement vs baseline with color-coded output

## Requirements

- Python 3.8 or higher
- pandas library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/SimpleStopLossOptimizer.git
cd SimpleStopLossOptimizer
```

2. Install dependencies:
```bash
pip install pandas
```

3. Set up your configuration:
```bash
# Copy the template to create your local config
cp config_template.py config_local.py

# Edit config_local.py to set your CSV path and thresholds
# (Use your preferred text editor)
```

## Configuration

Edit `config_local.py` to customize:

- **PATH_TO_CSV**: Default path to your trade data CSV file
- **DEFAULT_THRESHOLDS**: Percentile thresholds to test (e.g., [1.0, 3.0, 5.0, 10.0, ...])

**Note**: `config_local.py` is git-ignored to keep your personal settings private.

## CSV Data Format

Your CSV file must include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| MAE    | Maximum Adverse Excursion as percentage | -2.56 (means -2.56%) |
| Shares | Number of shares traded | 100 |
| Price  | Entry price | 25.50 |
| Profit | Actual profit/loss for the trade | -45.23 |

**Note**: MAE values should be negative percentages. Percentage strings (e.g., "-2.56%") are automatically converted to numeric values.

## Usage

### Basic Usage (uses default CSV from config)
```bash
python Simple_Stop_Loss_Optimizer.py
```

### Specify a different CSV file
```bash
python Simple_Stop_Loss_Optimizer.py path/to/your/trades.csv
```

### Custom thresholds
```bash
python Simple_Stop_Loss_Optimizer.py trades.csv --thresholds 5 10 25 50 75 95
```

### Full path example (Windows)
```bash
python Simple_Stop_Loss_Optimizer.py "C:\Users\YourName\Documents\Trading\trades.csv"
```

## Example Output

```
====================================================================================================
MATT'S SIMPLE STOP LOSS OPTIMIZER
====================================================================================================

Analyzing 116,188 trades with valid data

Baseline (No Stop Loss):
  Total Profit: $-109,387.92
  Win Rate: 46.4%
  Avg Profit/Trade: $-0.94

====================================================================================================
STOP LOSS SIMULATION RESULTS
====================================================================================================

MAE %      Thresh %   Trades     Stopped    Total $         Δ vs Base       $/Trade      Win%    
-----------------------------------------------------------------------------------------------
   -19.07% 1.0        116,188    1,159         -108,032.11      +1,355.81       -0.93    46.4%
   -12.01% 3.0        116,188    3,482         -106,086.50      +3,301.42       -0.91    46.2%
    -9.21% 5.0        116,188    5,808         -102,488.47      +6,899.45       -0.88    46.0%
    -6.17% 10.0       116,188    11,598         -92,208.74     +17,179.18       -0.79    45.3%
    ...

====================================================================================================
BEST STOP LOSS SETTING:
  MAE Threshold: -4.23%
  Percentile: 25.0%
  Total Profit: $-85,432.10
  Improvement: +$23,955.82 (+21.9%)
  Trades Stopped: 29,047 (25.0%)
  Win Rate: 43.2%
====================================================================================================
```

Green highlighting indicates improvements over the baseline.

## How It Works

The optimizer simulates applying a stop loss at different MAE thresholds:

1. **For each percentile threshold** (e.g., 5%, 10%, 25%):
   - Find the MAE value at that percentile (e.g., 25th percentile = -4.23%)
   - This becomes the stop loss threshold

2. **For each trade**:
   - If actual MAE < threshold (worse than threshold) → simulate stop loss:
     - `simulated_loss = shares × entry_price × mae_threshold / 100`
   - Otherwise → use actual profit (trade wasn't stopped)

3. **Calculate metrics**:
   - Total profit with this stop loss
   - Improvement vs baseline
   - Number of trades stopped
   - Win rate

4. **Identify best setting**: The threshold that maximizes total profit

## Understanding the Results

- **MAE %**: The stop loss threshold at this percentile
- **Thresh %**: The percentile being tested
- **Stopped**: Number of trades that would have been stopped
- **Total $**: Total profit/loss with this stop loss applied
- **Δ vs Base**: Improvement compared to no stop loss
- **$/Trade**: Average profit per trade
- **Win%**: Percentage of profitable trades

A positive Δ vs Base (green) means this stop loss would improve results.

## Data Preparation Tips

If your data has percentage columns stored as strings (e.g., "-2.56%"), the tool will automatically convert them. Make sure:

- MAE values are negative (representing losses)
- Price is the **entry price** (not exit price)
- Shares and Profit are numeric

## Folder Structure

```
SimpleStopLossOptimizer/
├── Simple_Stop_Loss_Optimizer.py  # Main script
├── config_template.py              # Template configuration
├── config_local.py                 # Your local config (git-ignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
└── data/                           # Put your CSV files here
    └── trades.csv
```

## Contributing

This is a personal tool, but suggestions and improvements are welcome! Feel free to open an issue or submit a pull request.

## License

MIT License - feel free to use and modify as needed.

## Author

Matt Hibbs

## Acknowledgments

Built to analyze trading data and optimize stop loss settings based on historical Maximum Adverse Excursion (MAE) analysis.

"""
Matt's Simple Stop Loss Optimizer

Analyzes trading data to find the approximate optimal stop loss setting by simulating
profit/loss at different MAE (Maximum Adverse Excursion) thresholds.

Usage:
    python Simple_Stop_Loss_Optimizer.py path/to/trades.csv

Required CSV columns:
    - MAE: Maximum Adverse Excursion as percentage (e.g., -2.56 = -2.56%)
    - Shares: Number of shares traded
    - Price: Entry price
    - Profit: Actual profit/loss for the trade

The tool will:
    1. Load your trade data
    2. Calculate baseline metrics (no stop loss)
    3. Simulate profit/loss at different MAE thresholds (using percentiles)
    4. Show which stop loss setting maximizes profit
    5. Display improvement vs baseline
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

try:
    import config_local as config
except ImportError:
    print("ERROR: config_local.py not found!")
    print("Please copy config_template.py to config_local.py and customize it.")
    sys.exit(1)


# Load configuration
DEFAULT_THRESHOLDS = config.DEFAULT_THRESHOLDS
PATH_TO_CSV = Path(config.PATH_TO_CSV)


def load_trade_data(csv_path: Path) -> pd.DataFrame:
    """Load trade data from CSV file."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Convert percentage columns (strip % and convert to float)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        
        sample = df[col].dropna().head(100)
        if sample.empty:
            continue
        
        # If most values end with '%', convert them
        if sample.astype(str).str.endswith('%').sum() > len(sample) * 0.5:
            df[col] = df[col].astype(str).str.rstrip('%').replace('', pd.NA)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def analyze_stop_loss(df: pd.DataFrame, threshold_pcts: list[float]) -> None:
    """
    Analyze optimal stop loss settings by simulating profit at different MAE thresholds.
    
    Args:
        df: DataFrame with trade data
        threshold_pcts: List of percentiles to test (e.g., [1.0, 5.0, 10.0, ...])
    """
    # Validate required columns
    required_cols = ['MAE', 'Shares', 'Price', 'Profit']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}\nAvailable columns: {list(df.columns)}")
    
    # Get valid data
    mae_series = pd.to_numeric(df['MAE'], errors='coerce')
    shares_series = pd.to_numeric(df['Shares'], errors='coerce')
    price_series = pd.to_numeric(df['Price'], errors='coerce')
    profit_series = pd.to_numeric(df['Profit'], errors='coerce')
    
    # Filter to rows with all required data
    valid_mask = mae_series.notna() & shares_series.notna() & price_series.notna() & profit_series.notna()
    valid_indices = df.index[valid_mask].tolist()
    
    if len(valid_indices) == 0:
        print("ERROR: No valid data found. Check that MAE, Shares, Ex. Price, and Profit columns contain numeric data.")
        return
    
    mae_valid = mae_series.loc[valid_indices]
    shares_valid = shares_series.loc[valid_indices]
    price_valid = price_series.loc[valid_indices]
    profit_valid = profit_series.loc[valid_indices]
    
    # Calculate baseline metrics
    baseline_total_profit = float(profit_valid.sum())
    baseline_win_rate = float((profit_valid > 0).mean()) * 100
    baseline_avg_profit = float(profit_valid.mean())
    baseline_trade_count = len(valid_indices)
    
    # Sort MAE values (most negative to least negative)
    mae_sorted = mae_valid.sort_values()
    
    # Display header
    print("=" * 100)
    print("MATT'S SIMPLE STOP LOSS OPTIMIZER")
    print("=" * 100)
    print(f"\nAnalyzing {baseline_trade_count:,} trades with valid data")
    print(f"\nBaseline (No Stop Loss):")
    print(f"  Total Profit: ${baseline_total_profit:,.2f}")
    print(f"  Win Rate: {baseline_win_rate:.1f}%")
    print(f"  Avg Profit/Trade: ${baseline_avg_profit:.2f}")
    print("\n" + "=" * 100)
    print("STOP LOSS SIMULATION RESULTS")
    print("=" * 100)
    print(f"\n{'MAE %':<10} {'Thresh %':<10} {'Trades':<10} {'Stopped':<10} {'Total $':<15} {'Δ vs Base':<15} {'$/Trade':<12} {'Win%':<8}")
    print("-" * 95)
    
    stop_loss_results = []
    
    for pct in threshold_pcts:
        # Find the MAE threshold at this percentile
        threshold_idx = max(0, int(len(mae_sorted) * (pct / 100.0)) - 1)
        mae_threshold = mae_sorted.iloc[threshold_idx]
        
        # Simulate profit with this stop loss
        simulated_profit_total = 0.0
        stopped_count = 0
        win_count = 0
        
        for idx in valid_indices:
            actual_mae = mae_series.loc[idx]
            actual_profit = profit_series.loc[idx]
            shares = shares_series.loc[idx]
            entry_price = price_series.loc[idx]
            
            # If actual MAE is worse (more negative) than threshold, simulate stop loss
            if actual_mae < mae_threshold:
                # Calculate loss at stop: shares * entry_price * mae_threshold / 100
                simulated_loss = shares * entry_price * mae_threshold / 100.0
                simulated_profit_total += simulated_loss
                stopped_count += 1
                if simulated_loss > 0:
                    win_count += 1
            else:
                # Trade wasn't stopped, use actual profit
                simulated_profit_total += actual_profit
                if actual_profit > 0:
                    win_count += 1
        
        delta_vs_base = simulated_profit_total - baseline_total_profit
        avg_profit = simulated_profit_total / baseline_trade_count
        win_rate = (win_count / baseline_trade_count * 100)
        
        # Color code based on improvement
        if delta_vs_base > 0:
            color = "\033[92m"  # Green for improvement
            reset = "\033[0m"
        else:
            color = ""
            reset = ""
        
        print(f"{mae_threshold:>9.2f}% {pct:<10.1f} {baseline_trade_count:<10,} {stopped_count:<10,} "
              f"{color}{simulated_profit_total:>14,.2f}{reset} {color}{delta_vs_base:>+14,.2f}{reset} "
              f"{avg_profit:>11.2f} {win_rate:>7.1f}%")
        
        stop_loss_results.append({
            'mae_threshold': mae_threshold,
            'percentile': pct,
            'total_profit': simulated_profit_total,
            'delta': delta_vs_base,
            'stopped_count': stopped_count,
            'win_rate': win_rate
        })
    
    # Find best stop loss setting
    best_result = max(stop_loss_results, key=lambda x: x['total_profit'])
    
    print("\n" + "=" * 100)
    print(f"\033[1mBEST STOP LOSS SETTING:\033[0m")
    print(f"  MAE Threshold: {best_result['mae_threshold']:.2f}%")
    print(f"  Percentile: {best_result['percentile']:.1f}%")
    print(f"  Total Profit: \033[92m${best_result['total_profit']:,.2f}\033[0m")
    print(f"  Improvement: \033[92m${best_result['delta']:+,.2f}\033[0m ({best_result['delta']/abs(baseline_total_profit)*100:+.1f}%)")
    print(f"  Trades Stopped: {best_result['stopped_count']:,} ({best_result['stopped_count']/baseline_trade_count*100:.1f}%)")
    print(f"  Win Rate: {best_result['win_rate']:.1f}%")
    print("=" * 100)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Matt's Simple Stop Loss Optimizer - Find optimal stop loss settings from trade data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python Simple_Stop_Loss_Optimizer.py trades.csv
    python Simple_Stop_Loss_Optimizer.py ../data/backtest_results.csv
    python Simple_Stop_Loss_Optimizer.py trades.csv --thresholds 5 10 25 50 75 95

Required CSV Columns:
    MAE         - Maximum Adverse Excursion (as %, e.g., -2.56)
    Shares      - Number of shares traded
    Price       - Entry price
    Profit      - Actual profit/loss
        """
    )
    
    parser.add_argument('csv_file', type=str, nargs='?', default=str(PATH_TO_CSV), help='Path to CSV file with trade data (default: data/trades.csv)')
    parser.add_argument(
        '--thresholds', 
        type=float, 
        nargs='+', 
        default=DEFAULT_THRESHOLDS,
        help='Percentile thresholds to test (default: 1, 3, 5, 10, 15, ..., 95)'
    )
    
    args = parser.parse_args()
    
    # Load data
    csv_path = Path(args.csv_file)
    print(f"Loading trade data from: {csv_path}")
    
    try:
        df = load_trade_data(csv_path)
        print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")
        
        # Run analysis
        analyze_stop_loss(df, sorted(args.thresholds))
        
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

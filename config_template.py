"""
Configuration Template for Simple Stop Loss Optimizer

SETUP INSTRUCTIONS:
1. Copy this file and save it as: config_local.py
2. Modify the values below to match your setup
3. Never commit config_local.py to git (it's in .gitignore)

The config_local.py file will be imported by the optimizer script.
"""

# Default path to your CSV file with trade data
# You can override this by passing a path as a command-line argument
PATH_TO_CSV = "data/trades.csv"

# Percentile thresholds to test for stop loss optimization
# These represent percentiles of the MAE distribution
# Default: Test at 1%, 3%, 5%, then every 5% from 10% to 95%
DEFAULT_THRESHOLDS = [
    1.0, 3.0, 5.0, 
    10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 
    45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 
    80.0, 85.0, 90.0, 95.0
]

# You can customize the thresholds to test fewer or different percentiles:
# Example - Only test major quartiles:
# DEFAULT_THRESHOLDS = [5.0, 25.0, 50.0, 75.0, 95.0]
#
# Example - Fine-grained testing every 2%:
# DEFAULT_THRESHOLDS = list(range(2, 100, 2))

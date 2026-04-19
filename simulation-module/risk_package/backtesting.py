"""
VaR backtesting and validation
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


def calculate_var_breaches(
    predicted_var: np.ndarray,
    actual_losses: np.ndarray,
    confidence: float = 0.95
) -> Dict[str, float]:
    """
    Calculate VaR breach statistics
    
    Args:
        predicted_var: Array of VaR predictions
        actual_losses: Array of actual realized losses
        confidence: VaR confidence level
        
    Returns:
        Dictionary with breach statistics
    """
    breaches = actual_losses > predicted_var
    breach_count = np.sum(breaches)
    total_days = len(predicted_var)
    breach_rate = breach_count / total_days
    expected_rate = 1 - confidence
    
    # Kupiec Test (Proportion of Failures test)
    # H0: Breach rate = expected rate
    if breach_count > 0:
        lr_stat = -2 * (
            breach_count * np.log(expected_rate) +
            (total_days - breach_count) * np.log(1 - expected_rate) -
            breach_count * np.log(breach_rate) -
            (total_days - breach_count) * np.log(1 - breach_rate)
        )
        # Critical value at 5% significance: 3.84 (chi-squared, 1 df)
        kupiec_pass = lr_stat < 3.84
    else:
        lr_stat = np.nan
        kupiec_pass = False
    
    return {
        'breach_count': int(breach_count),
        'total_observations': int(total_days),
        'breach_rate': float(breach_rate),
        'expected_breach_rate': float(expected_rate),
        'kupiec_lr_stat': float(lr_stat) if not np.isnan(lr_stat) else None,
        'kupiec_test_passed': bool(kupiec_pass)
    }


def calculate_actual_loss(
    previous_price: float,
    current_price: float,
    position_size: float = 1.0
) -> float:
    """
    Calculate actual loss from price change
    
    Args:
        previous_price: Price at start of period
        current_price: Price at end of period
        position_size: Number of shares/units
        
    Returns:
        Realized loss (positive = loss, negative = gain)
    """
    return (previous_price - current_price) * position_size


def generate_backtest_report(results: Dict) -> str:
    """
    Generate human-readable backtest report
    
    Args:
        results: Dictionary from calculate_var_breaches
        
    Returns:
        Formatted report string
    """
    status = "✅ PASS" if results['kupiec_test_passed'] else "❌ FAIL"
    
    report = f"""
╔══════════════════════════════════════════════════════════╗
║              VaR BACKTESTING REPORT                      ║
╠══════════════════════════════════════════════════════════╣
║  Total Observations:    {results['total_observations']:>5}                        ║
║  VaR Breaches:          {results['breach_count']:>5}                        ║
║  Breach Rate:           {results['breach_rate']*100:>5.2f}%                      ║
║  Expected Rate:         {results['expected_breach_rate']*100:>5.2f}%                      ║
║                                                          ║
║  Kupiec LR Statistic:   {results['kupiec_lr_stat']:>5.2f}                       ║
║  Test Result:           {status:>10}                    ║
╚══════════════════════════════════════════════════════════╝
"""
    return report
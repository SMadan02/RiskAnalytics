"""
Run VaR backtesting on historical data
"""
import psycopg2
import pandas as pd
from risk_package.backtesting import calculate_var_breaches, generate_backtest_report, calculate_actual_loss
from risk_package.config import DB_CONFIG

def run_backtest_for_symbol(symbol: str, lookback_days: int = 100):
    """Run backtest for a single symbol"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Fetch historical VaR predictions and actual prices
    query = f"""
    SELECT 
        timestamp,
        current_price,
        var_95,
        LAG(current_price) OVER (ORDER BY timestamp) as prev_price
    FROM risk_metrics
    WHERE symbol = %s
    AND timestamp > NOW() - INTERVAL '{lookback_days} days'
    ORDER BY timestamp
    """
    
    df = pd.read_sql(query, conn, params=(symbol,))
    
    # Calculate actual losses
    df['actual_loss'] = df.apply(
        lambda row: calculate_actual_loss(row['prev_price'], row['current_price']) 
        if pd.notna(row['prev_price']) else 0,
        axis=1
    )
    
    # Remove first row (no previous price)
    df = df.iloc[1:]
    
    # Run backtest
    results = calculate_var_breaches(
        predicted_var=df['var_95'].values,
        actual_losses=df['actual_loss'].values
    )
    
    # Print report
    print(f"\n{'='*60}")
    print(f"BACKTESTING: {symbol}")
    print(generate_backtest_report(results))
    
    # Store results
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO backtest_results 
        (test_date, symbol, lookback_days, breach_count, total_observations, 
         breach_rate, expected_breach_rate, kupiec_lr_stat, test_passed)
        VALUES (CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        symbol,
        lookback_days,
        results['breach_count'],
        results['total_observations'],
        results['breach_rate'],
        results['expected_breach_rate'],
        results['kupiec_lr_stat'],
        results['test_passed']
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    symbols = ['TSLA', 'NVDA', 'MSFT', 'JPM', 'AAPL']
    
    for symbol in symbols:
        try:
            run_backtest_for_symbol(symbol, lookback_days=30)
        except Exception as e:
            print(f"Error backtesting {symbol}: {e}")
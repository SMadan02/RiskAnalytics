"""
Simple Flask dashboard for risk metrics visualization
"""
from flask import Flask, render_template, jsonify
import psycopg2
import pandas as pd
from risk_package.config import DB_CONFIG

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/current_risk')
def current_risk():
    """Get latest risk metrics for all symbols"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    WITH latest AS (
        SELECT DISTINCT ON (symbol)
            symbol,
            current_price,
            var_95,
            es_95,
            volatility_forecast,
            timestamp
        FROM risk_metrics
        ORDER BY symbol, timestamp DESC
    )
    SELECT * FROM latest ORDER BY var_95 DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return jsonify(df.to_dict('records'))

@app.route('/api/var_trend/<symbol>')
def var_trend(symbol):
    """Get VaR trend for a symbol"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT 
        timestamp,
        var_95,
        es_95,
        volatility_forecast
    FROM risk_metrics
    WHERE symbol = %s
    AND timestamp > NOW() - INTERVAL '24 hours'
    ORDER BY timestamp
    """
    
    df = pd.read_sql(query, conn, params=(symbol,))
    conn.close()
    
    return jsonify({
        'timestamps': df['timestamp'].dt.strftime('%H:%M').tolist(),
        'var': df['var_95'].tolist(),
        'es': df['es_95'].tolist(),
        'vol': df['volatility_forecast'].tolist()
    })

@app.route('/api/backtest_summary')
def backtest_summary():
    """Get latest backtest results"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    query = """
    SELECT DISTINCT ON (symbol)
        symbol,
        breach_rate,
        expected_breach_rate,
        test_passed,
        test_date
    FROM backtest_results
    ORDER BY symbol, test_date DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
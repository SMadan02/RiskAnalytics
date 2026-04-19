from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import psycopg2
from datetime import datetime, timedelta

app = FastAPI()

DB_CONFIG = {
    "host": "timescaledb",
    "port": 5432,
    "database": "riskmetrics",
    "user": "riskengine",
    "password": "password123"
}

@app.get("/api/summary")
def get_summary():
    """Get portfolio-level summary"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Latest metrics per symbol
    cursor.execute("""
        SELECT DISTINCT ON (symbol)
            symbol, 
            current_price, 
            var_95, 
            es_95,
            timestamp
        FROM risk_metrics
        ORDER BY symbol, timestamp DESC
    """)
    
    latest = cursor.fetchall()
    
    # Calculate portfolio totals
    total_var = sum(row[2] for row in latest)
    total_es = sum(row[3] for row in latest)
    
    cursor.close()
    conn.close()
    
    return {
        "portfolio_var": round(total_var, 2),
        "portfolio_es": round(total_es, 2),
        "num_assets": len(latest),
        "timestamp": latest[0][4].isoformat() if latest else None,
        "assets": [
            {
                "symbol": row[0],
                "price": round(row[1], 2),
                "var": round(row[2], 2),
                "es": round(row[3], 2),
                "var_pct": round((row[2] / row[1]) * 100, 2)
            }
            for row in latest
        ]
    }

@app.get("/api/history/{symbol}")
def get_history(symbol: str, hours: int = 6):
    """Get VaR history for a symbol"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, var_95, es_95, current_price
        FROM risk_metrics
        WHERE symbol = %s 
          AND timestamp > NOW() - INTERVAL '%s hours'
        ORDER BY timestamp ASC
    """, (symbol, hours))
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {
        "symbol": symbol,
        "data": [
            {
                "time": row[0].isoformat(),
                "var": round(row[1], 2),
                "es": round(row[2], 2),
                "price": round(row[3], 2)
            }
            for row in rows
        ]
    }

# Serve static HTML
app.mount("/", StaticFiles(directory="static", html=True), name="static")
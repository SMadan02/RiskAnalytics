-- Track actual profit/loss for backtesting
CREATE TABLE IF NOT EXISTS actual_pnl (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    opening_price DOUBLE PRECISION NOT NULL,
    closing_price DOUBLE PRECISION NOT NULL,
    actual_return DOUBLE PRECISION,  -- (close - open) / open
    actual_pnl DOUBLE PRECISION,     -- Absolute P&L
    position_size INTEGER DEFAULT 100
);

CREATE INDEX idx_pnl_timestamp ON actual_pnl(timestamp DESC);
CREATE INDEX idx_pnl_symbol ON actual_pnl(symbol);

-- View: Join VaR predictions with actual outcomes
CREATE VIEW var_backtest AS
SELECT 
    r.timestamp,
    r.symbol,
    r.current_price,
    r.var_95,
    r.es_95,
    p.actual_pnl,
    CASE 
        WHEN ABS(p.actual_pnl) > r.var_95 THEN TRUE 
        ELSE FALSE 
    END as var_breach,
    CASE
        WHEN ABS(p.actual_pnl) > r.es_95 THEN TRUE
        ELSE FALSE
    END as es_breach
FROM risk_metrics r
LEFT JOIN actual_pnl p 
    ON r.symbol = p.symbol 
    AND DATE_TRUNC('day', r.timestamp) = DATE_TRUNC('day', p.timestamp);
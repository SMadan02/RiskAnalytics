CREATE TABLE var_backtesting (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    predicted_var DOUBLE PRECISION,
    actual_loss DOUBLE PRECISION,
    breach BOOLEAN,
    
    -- Rolling metrics
    breach_rate_100d DOUBLE PRECISION,  -- Last 100 days
    expected_breaches_100d INTEGER,
    actual_breaches_100d INTEGER
);

CREATE INDEX idx_backtest_symbol_time ON var_backtesting(symbol, timestamp DESC);

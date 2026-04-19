-- File: simulation-module/backtest_schema.sql

CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,
    test_date DATE NOT NULL,
    symbol TEXT NOT NULL,
    lookback_days INTEGER NOT NULL,
    breach_count INTEGER,
    total_observations INTEGER,
    breach_rate DOUBLE PRECISION,
    expected_breach_rate DOUBLE PRECISION,
    kupiec_lr_stat DOUBLE PRECISION,
    test_passed BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_backtest_date ON backtest_results(test_date DESC);
CREATE INDEX idx_backtest_symbol ON backtest_results(symbol);
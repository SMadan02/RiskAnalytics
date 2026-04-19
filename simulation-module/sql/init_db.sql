CREATE TABLE IF NOT EXISTS risk_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    current_price DOUBLE PRECISION,
    var_95 DOUBLE PRECISION,
    es_95 DOUBLE PRECISION,
    num_simulations INTEGER
);

-- Create index for fast time-based queries
CREATE INDEX idx_risk_timestamp ON risk_metrics(timestamp DESC);
CREATE INDEX idx_risk_symbol ON risk_metrics(symbol);
-- File: simulation-module/update_schema.sql

ALTER TABLE risk_metrics
ADD COLUMN IF NOT EXISTS volatility_forecast DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS volatility_method TEXT,
ADD COLUMN IF NOT EXISTS garch_params JSONB;

-- Create view for comparison
CREATE OR REPLACE VIEW var_comparison AS
SELECT 
    timestamp,
    symbol,
    current_price,
    var_95,
    es_95,
    volatility_forecast,
    LAG(var_95) OVER (PARTITION BY symbol ORDER BY timestamp) as prev_var,
    (var_95 - LAG(var_95) OVER (PARTITION BY symbol ORDER BY timestamp)) as var_change
FROM risk_metrics
ORDER BY timestamp DESC;
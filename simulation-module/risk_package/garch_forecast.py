"""
GARCH volatility forecasting for dynamic VaR calculation
"""
import numpy as np
import pandas as pd
from arch import arch_model
from typing import Tuple, Optional


def calculate_returns(prices: np.ndarray) -> np.ndarray:
    """
    Calculate log returns from price series
    
    Log returns are often used in financial modeling because they are time-additive and can
    handle compounding effects, making them more suitable for volatility modeling.
    
    Args:
        prices: Array of historical prices
        
    Returns:
        Array of log returns in percentage (multiplied by 100)
    """
    # np.log(prices[1:] / prices[:-1]) calculates the natural logarithm of price ratios
    # This gives us log returns: ln(P_t / P_t-1)
    # Multiplying by 100 converts to percentage form for easier interpretation
    return np.log(prices[1:] / prices[:-1]) * 100  # Convert to percentage


def fit_garch(returns: np.ndarray, p: int = 1, q: int = 1) -> Tuple[float, dict]:
    """
    Fit GARCH(p,q) model and forecast next-period volatility
    
    GARCH(p,q) stands for Generalized Autoregressive Conditional Heteroskedasticity model.
    It models time-varying volatility where recent shocks and volatility patterns affect 
    future volatility. Common choice is GARCH(1,1), which includes one lag of squared 
    residuals (ARCH term, q) and one lag of conditional variance (GARCH term, p).
    
    Key insight: Financial returns exhibit volatility clustering - periods of high volatility 
    tend to be followed by high volatility, and calm periods by calm periods. GARCH captures this.
    
    Args:
        returns: Historical return series (typically log returns)
        p: GARCH lag order - number of past conditional variances to include (default 1)
        q: ARCH lag order - number of past squared residuals to include (default 1)
           A lag refers to how many time steps back we look. lag=1 means one time step back.
        
    Returns:
        Tuple of (forecasted_volatility, model_summary dict with parameters)
    """
    # Fit GARCH(p,q) model to historical returns
    # rescale=False keeps returns in original percentage form; if True, would rescale internally
    model = arch_model(returns, vol='Garch', p=p, q=q, rescale=False)
    fitted_model = model.fit(disp='off')
    
    # Forecast next-period variance using the fitted model
    # The GARCH equation predicts future variance based on:
    # σ_t^2 = ω + α*ε_t-1^2 + β*σ_t-1^2
    # where ω (omega) = constant, α (alpha) = ARCH effect, β (beta) = GARCH effect
    forecast = fitted_model.forecast(horizon=1)
    forecasted_variance = forecast.variance.values[-1, 0]  # Extract 1-day ahead variance
    forecasted_vol = np.sqrt(forecasted_variance)  # Convert variance to volatility (standard deviation)
    
    # Extract model parameters for diagnostics and understanding model fit
    # omega (ω): constant term, baseline volatility level
    # alpha (α): coefficient on the ARCH term (recent shocks), measures volatility persistence from shocks
    # beta (β): coefficient on the GARCH term (recent volatility), measures volatility persistence from variance
    # log_likelihood: measure of model fit quality; higher values indicate better fit
    params = {
        'omega': fitted_model.params['omega'],
        'alpha': fitted_model.params['alpha[1]'],
        'beta': fitted_model.params['beta[1]'],
        'log_likelihood': fitted_model.loglikelihood
    }
    
    return forecasted_vol / 100, params  # Convert back from percentage


def calculate_realized_volatility(returns: np.ndarray, window: int = 20) -> float:
    """
    Calculate realized volatility (historical volatility) using standard deviation of recent returns
    
    Realized volatility is a backward-looking measure based on actual observed returns over 
    a rolling window, unlike GARCH which is a forward-looking model. Useful for:
    - Comparing against GARCH forecasts to assess model accuracy
    - Identifying recent volatility regimes
    - Risk assessment using historical patterns
    
    Args:
        returns: Return series (typically log returns)
        window: Lookback window in days (default 20 days ≈ 1 trading month)
        
    Returns:
        Annualized volatility estimate as decimal
    """
    # Slice the most recent window of returns from the time series
    recent_returns = returns[-window:]
    
    # Calculate daily standard deviation
    # Returns are in percentage form (multiplied by 100), so divide by 100 to get decimal form
    # Standard deviation of returns = daily volatility
    daily_vol = np.std(recent_returns) / 100  # Convert from percentage to decimal
    
    # Annualize the daily volatility
    # Multiply by sqrt(252) because there are approximately 252 trading days per year
    # Mathematically: Annual_Vol = Daily_Vol * sqrt(252)
    # This assumes returns are independent (which may not hold in practice due to volatility clustering)
    annual_vol = daily_vol * np.sqrt(252)  # Annualize to yearly volatility
    
    return annual_vol
import numpy as np
from typing import Tuple

def run_monte_carlo_var_garch(
    current_price: float,
    historical_prices: np.ndarray,
    mu: float = 0.0,
    T: float = 1/252,
    num_simulations: int = 10000,
    confidence: float = 0.95,
    use_garch: bool = True
) -> Tuple[float, float, float, dict]:
    """
    Run Monte Carlo simulation for VaR with dynamic GARCH volatility forecasting
    
    This function enhances standard Monte Carlo VaR by using GARCH model to forecast
    next-period volatility instead of using a static, historical volatility estimate.
    
    Why GARCH over fixed volatility?
    - Financial returns exhibit volatility clustering: high volatility periods tend to 
      cluster together, as do calm periods
    - GARCH captures this clustering by modeling volatility as dependent on recent shocks 
      and past volatility
    - Result: VaR estimates adapt to current market conditions rather than being static
    
    Traditional: VaR(sigma=fixed 30%) → same risk estimate regardless of market state
    GARCH way:  VaR(sigma=GARCH forecast) → risk estimate adapts to volatility regime
    
    Args:
        current_price: Current stock price (starting point for simulation)
        historical_prices: Array of historical prices (minimum ~60 days for GARCH fitting)
        mu: Drift parameter (expected return, typically 0 for risk-neutral valuation)
        T: Time horizon in years (1/252 = 1 trading day, default)
        num_simulations: Number of Monte Carlo paths to simulate (10,000 = balance of speed/accuracy)
        confidence: Confidence level for VaR calculation (0.95 = 95% confidence)
        use_garch: If True, use GARCH forecast; if False, fallback to historical volatility
        
    Returns:
        Tuple of (VaR, ES, volatility_used, garch_params) where:
        - VaR: Value at Risk at specified confidence level (positive loss amount)
        - ES: Expected Shortfall (average loss in tail scenarios)
        - volatility_used: Annualized volatility used for simulation
        - garch_params: Dictionary with model parameters (omega, alpha, beta, log_likelihood) 
                       or method info if using fallback
    """
    from .garch_forecast import calculate_returns, fit_garch, calculate_realized_volatility
    
    # Convert historical prices to returns (log returns)
    # This is necessary because GARCH models volatility of returns, not price levels
    returns = calculate_returns(historical_prices)
    
    if use_garch and len(returns) >= 60:
        # GARCH path: Use fitted GARCH(1,1) model for forward-looking volatility forecast
        # Why 60+ returns? GARCH needs sufficient history to reliably fit the model
        # fit_garch() returns:
        # - sigma: next-period forecasted volatility (annualized)
        # - garch_params: dict with (omega, alpha, beta) coefficients for diagnostics
        #   These show how volatility depends on recent shocks (alpha) vs past volatility (beta)
        sigma, garch_params = fit_garch(returns)
    else:
        # Fallback path: If insufficient history or GARCH disabled, use realized volatility
        # Realized volatility = historical std deviation of last 20 days, annualized
        # This is backward-looking (what happened recently) vs GARCH's forward-looking forecast
        sigma = calculate_realized_volatility(returns)
        garch_params = {'method': 'realized_vol', 'window': 20}
    
    # Run Monte Carlo simulation with Geometric Brownian Motion
    # Using the forecasted volatility (sigma) from GARCH or historical volatility
    # This generates 'num_simulations' possible price paths over T time period
    final_prices = simulate_gbm(current_price, mu, sigma, T, num_simulations)
    
    # Calculate VaR from simulated outcomes
    # VaR = maximum loss at specified confidence level (e.g., 95%)
    # Interpretation: "We are 95% confident losses will NOT exceed this amount"
    var_95, losses = calculate_var(current_price, final_prices, confidence)
    
    # Calculate Expected Shortfall
    # ES = average loss in the worst scenarios (tail of distribution beyond VaR threshold)
    # ES gives insight into severity of losses in extreme market moves
    es_95 = calculate_es(var_95, losses)
    
    # Return tuple: (VaR amount, Expected Shortfall, volatility used in simulation, model params)
    # Converting to float for serialization/storage purposes
    return (float(var_95), float(es_95), float(sigma), garch_params)

def run_monte_carlo_var(
    current_price: float,
    mu: float = 0.0,
    sigma: float = 0.30,
    T: float = 1/252,  # 1 day
    num_simulations: int = 10000,
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Run Monte Carlo simulation and return VaR and ES
    
    Returns:
        (var_95, es_95) as a tuple
    """
    final_prices = simulate_gbm(current_price, mu, sigma, T, num_simulations)
    var_95, var_threshold, losses = calculate_var(current_price, final_prices, confidence)
    es_95 = calculate_es(var_threshold, losses)    
    return (var_95, es_95)


def simulate_gbm(S0, mu, sigma, T, num_simulations):
    """
    Simulate stock prices using Geometric Brownian Motion
    
    Returns:
        Array of final prices (one per simulation)
    """
    # TODO: Implement this
    z = np.random.standard_normal(num_simulations)  # Generate random shocks
    drift = (mu - 0.5 * sigma**2) * T # Calculate drift
    diffusion = sigma * np.sqrt(T) * z  # Calculate diffusion
    ST = S0 * np.exp(drift + diffusion)  # GBM formula
    return ST

def calculate_var(initial_value, simulated_values, confidence=0.95):
    """
    Calculate Value at Risk (VaR)
    VaR at 95% confidence means we are 95% confident that losses will NOT exceed this amount.
    
    Args:
        initial_value: Starting portfolio value
        simulated_values: Array of simulated ending values
        confidence: Confidence level (0.95 = 95%)
    
    Returns:
        Tuple of (var_amount, var_percentile, losses_array)
        - var_amount: VaR as a positive loss amount (always >= 0)
        - var_percentile: The actual percentile value from distribution
        - losses: Array of calculated losses for further analysis
    """
    # Calculate losses: positive = loss, negative = gain
    losses = initial_value - simulated_values
    
    # Find the confidence percentile of the loss distribution
    # For 95% confidence, this is the 95th percentile of losses
    # This represents the loss level below which 95% of outcomes fall
    var_percentile = np.percentile(losses, confidence * 100)
    
    # VaR should always be reported as a positive number (amount of potential loss)
    var_amount = max(0, var_percentile)
    
    return var_amount, var_percentile, losses
    

def calculate_es(var_threshold, losses):
    """
    Calculate Expected Shortfall (Conditional Value at Risk)
    ES is the average loss in the worst-case scenarios (tail of the distribution)
    
    Args:
        var_threshold: The VaR threshold (loss level at confidence level)
        losses: Array of all simulated losses
    
    Returns:
        ES as a positive number (average loss in worst cases)
    """
    # We want to find the average loss of all simulations where the loss is greater than or equal to the VaR threshold. 
    # This means we are looking at the tail of the loss distribution that exceeds the VaR level.
    # Average of all losses exceeding VaR (worst 5% for 95% confidence)
    # Use > (strictly greater) because ES is the average of losses that EXCEED the VaR threshold
    tail_losses = losses[losses > var_threshold]
    
    # If no tail losses found (edge case), use >= as fallback
    if len(tail_losses) == 0:
        tail_losses = losses[losses >= var_threshold]
    
    es = np.mean(tail_losses) if len(tail_losses) > 0 else var_threshold
    
    return max(0, es)
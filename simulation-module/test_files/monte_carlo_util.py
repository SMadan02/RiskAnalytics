import numpy as np
# import matplotlib.pyplot as plt

# Parameters
S0 = 185.0       # Initial price
mu = 0.10        # 10% annual drift
sigma = 0.20     # 20% annual volatility
T = 1/252        # 1 day in years. Why 252? Because there are approximately 252 trading days in a year.
num_simulations = 10000

# Your task: Fill in the simulation logic

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

# def plot_distribution(losses, var_threshold, es_95):
    
#     # Add this after calculating losses:
#     plt.figure(figsize=(12, 5))

#     # Plot 1: Distribution of losses
#     plt.subplot(1, 2, 1)
#     plt.hist(losses, bins=50, alpha=0.7, edgecolor='black')
#     plt.axvline(var_threshold, color='red', linestyle='--', label=f'VaR 95%: ${var_95:.2f}')
#     plt.axvline(es_95, color='orange', linestyle='--', label=f'ES 95%: ${es_95:.2f}')
#     plt.xlabel('Loss ($)')
#     plt.ylabel('Frequency')
#     plt.title('Distribution of Portfolio Losses (10,000 simulations)')
#     plt.legend()

#     # Plot 2: Sample price paths
#     plt.subplot(1, 2, 2)
#     # Simulate a few full paths (not just endpoints)
#     for i in range(50):
#         path = [S0]
#         for _ in range(int(T * 252)):
#             z = np.random.standard_normal()
#             drift = (mu - 0.5 * sigma**2) * (1/252)
#             diffusion = sigma * np.sqrt(1/252) * z
#             path.append(path[-1] * np.exp(drift + diffusion))
#         plt.plot(path, alpha=0.3, linewidth=0.5)

#     plt.xlabel('Days')
#     plt.ylabel('Stock Price ($)')
#     plt.title('Sample Simulated Price Paths')
#     plt.tight_layout()
#     plt.show()
    # Main execution
if __name__ == "__main__":
    # Simulate
    final_prices = simulate_gbm(S0, mu, sigma, T, num_simulations)
    
    # Calculate portfolio values (assume 100 shares)
    shares = 100
    initial_portfolio = S0 * shares
    final_portfolios = final_prices * shares
    
    # Calculate risk metrics
    var_95, var_threshold, losses = calculate_var(initial_portfolio, final_portfolios)
    es_95 = calculate_es(var_threshold, losses)
    
    # Print results
    print(f"Initial Portfolio Value: ${initial_portfolio:,.2f}")
    print(f"VaR (95%): ${var_95:,.2f}")
    print(f"ES (95%): ${es_95:,.2f}")
    
    # Calculate counts and bin edges (e.g., 5 bins)
    counts, bin_edges = np.histogram(losses, bins=5)
    percentages = (counts / len(losses)) * 100

    print(f"{'Interval Range':^20} | {'Count':^7} | {'Percentage':^10}")
    print("-" * 45)
    for i in range(len(counts)):
        range_str = f"{bin_edges[i]:.1f} - {bin_edges[i+1]:.1f}"
        print(f"{range_str:^20} | {counts[i]:^7} | {percentages[i]:.1f}%")
    # plot_distribution(losses, var_threshold, es_95)
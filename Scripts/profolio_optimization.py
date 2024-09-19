import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from pypfopt import EfficientFrontier, risk_models, black_litterman, BlackLittermanModel

def Blacklitterman_weights(S, prior, returns_matrix, uncertainty_matrix, tickers, model_name):
    absolute_views = dict(zip(tickers.tolist(), returns_matrix[model_name].tolist()))
    view_confidences = uncertainty_matrix[model_name].tolist()
    bl = BlackLittermanModel(S, pi=prior, absolute_views=absolute_views, view_confidences=view_confidences)
    rets = bl.bl_returns()
    ef = EfficientFrontier(rets, S)
    ef.max_sharpe()
    print(ef.clean_weights())
    weights = ef.clean_weights()
    weights = np.array(list(weights.values()))
    predicted_features=ef.portfolio_performance(verbose=True)
    return (absolute_views, view_confidences), weights, predicted_features

def validation(returns, weights, predicted_features, risk_free_rate=0.02, shift=100):
    actual_returns, actual_volatility, actual_sharpe_ratio = calculate_sharpe_ratio_portfolio(returns[-shift:], weights, risk_free_rate)
    print(f"Portfolio Return: {actual_returns:.4f}")
    print(f"Portfolio Volatility: {actual_volatility:.4f}")
    print(f"Sharpe Ratio for the portfolio: {actual_sharpe_ratio:.2f}")
    actual_features = np.array([actual_returns, actual_volatility, actual_sharpe_ratio])
    distance = abs(actual_features - predicted_features)
    return actual_features, distance

def get_closest(S, prior, returns_matrix, uncertainty_matrix, returns, tickers, risk_free_rate=0.02, shift=100, model_names=['Linear Regression', 'Random Forest', 'XGBoost']):
    min_distance = float.inf
    for model_name in model_names:
        views, weights, predicted_features = Blacklitterman_weights(S, prior, returns_matrix, uncertainty_matrix, tickers, model_name)
        actual_features, distance = validation(returns, weights, predicted_features, risk_free_rate, shift)
        if np.mean(distance) < min_distance:
            min_distance = np.mean(distance)
            min_views = views
            min_actual_features = actual_features
            min_distance = distance
    return min_views, min_actual_features, min_distance

def Blacklitterman_test(absolute_views, view_confidences, tickers, start_date="2021-12-31", end_date="2024-03-31", verbose=True):
    ohlc = yf.download(tickers, start=start_date, end=end_date)
    prices = ohlc["Adj Close"]
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    market_prices = yf.download("SPY", start=start_date, end=end_date)["Adj Close"]
    delta = black_litterman.market_implied_risk_aversion(market_prices)
    prior = black_litterman.market_implied_prior_returns(get_mcaps(tickers), delta, S)
    bl = BlackLittermanModel(S, pi=prior, absolute_views=absolute_views, view_confidences=view_confidences)
    rets = bl.bl_returns()
    ef = EfficientFrontier(rets, S)
    ef.max_sharpe()
    print(ef.clean_weights())
    weights = ef.clean_weights()
    weights = np.array(list(weights.values()))
    predicted_features=ef.portfolio_performance(verbose=verbose)
    return weights, predicted_features

def get_mcaps(tickers):
    mcaps = {}
    for t in tickers:
        stock = yf.Ticker(t)
        shares_outstanding = stock.info.get('sharesOutstanding')
        marketCap=stock.history(start="2023-12-29", end="2024-03-31")['Close'].values[0] * shares_outstanding
        mcaps[t] = marketCap
    return mcaps

def calculate_sharpe_ratio_portfolio(returns, weights, risk_free_rate = 0.02, periods_per_year=252):
    """
    Calculate the Sharpe Ratio for a portfolio of assets.

    Parameters:
    returns (pd.DataFrame): DataFrame of daily returns of the assets.
    weights (np.array): Array of portfolio weights.
    risk_free_rate (float): Risk-free rate, expressed as an annualized rate.
    periods_per_year (int): Number of periods per year (252 for daily returns).

    Returns:
    tuple: The portfolio's volatility and Sharpe Ratio.
    """
    # Calculate the mean and covariance of daily returns
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    portfolio_return = (1+np.dot(weights, mean_returns)) ** periods_per_year - 1
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(periods_per_year)

    # Calculate the excess return
    excess_return = portfolio_return - risk_free_rate

    # Calculate the Sharpe Ratio
    sharpe_ratio = excess_return / portfolio_volatility

    return portfolio_return, portfolio_volatility, sharpe_ratio
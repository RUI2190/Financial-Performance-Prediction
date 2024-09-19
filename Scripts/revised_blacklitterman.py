import yfinance as yf
from datetime import date
from pypfopt import risk_models, black_litterman
from profolio_optimization import *
from views_prediction import *


tickers = ['NVDA', 'AAPL', 'GOOG']  # Example tickers for NVIDIA, Apple, and Google
returns_matrix, confidence_intervals_matrix, uncertainty_matrix = get_views(tickers)
df_combined = combined_data(tickers)
returns = get_returns(tickers, df_combined)

ohlc = yf.download(tickers, start='2021-12-31',end='2024-01-01')
prices = ohlc["Adj Close"]
S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
market_prices = yf.download("SPY", start='2021-12-31',end='2024-01-01')["Adj Close"]
delta = black_litterman.market_implied_risk_aversion(market_prices)
prior = black_litterman.market_implied_prior_returns(get_mcaps(tickers), delta, S)

views, actual_features, distance = get_closest(S, prior, returns_matrix, uncertainty_matrix, returns, tickers)

weights, predicted_features = Blacklitterman_test(views[0], views[1], tickers)

df_combined = combined_data(tickers, start_date="2024-03-31", end_date=date.today().strftime("%Y-%m-%d"))
returns = get_returns(tickers, df_combined)
actual_features, distance = validation(returns, weights, predicted_features)
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import yfinance as yf

# Function to preprocess data
def preprocess_data(df, shift=100):
    df['Date'] = pd.to_datetime(df.index)
    df.set_index('Date', inplace=True)
    df['Future_Return'] = df['Adj Close'].shift(-shift) / df['Adj Close'] - 1
    df = df.dropna(subset=['Future_Return'])
    df.loc[:, 'SMA_5'] = df['Adj Close'].rolling(window=5).mean()
    df = df.dropna()
    features = ['Open', 'High', 'Low', 'Adj Close', 'Volume', 'SMA_5']
    X = df[features]
    y = df['Future_Return']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y

# Function to train models and perform bootstrapping
def train_and_predict(X_train, y_train, X_test, n_iterations=100):
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBRegressor(objective='reg:squarederror', colsample_bytree=0.3, learning_rate=0.1, max_depth=5, alpha=10, n_estimators=100)
    }
    predictions = {}

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        preds = np.zeros((n_iterations, X_test.shape[0]))
        for i in range(n_iterations):
            preds[i] = model.predict(X_test)
        predictions[model_name] = preds.mean(axis=0)

    return predictions

# Function to preprocess data and split into training and testing sets
def split_data(company_data, shift=100):
    X, y = preprocess_data(company_data)
    train_size = int(len(X) - shift)
    return (X[:train_size], X[train_size:], y[:train_size], y[train_size:])

def get_views(tickers, start_date="2022-12-31", end_date="2024-03-31", models=['Linear Regression', 'Random Forest', 'XGBoost']):
    # Download historical data for each stock
    companies_data = []
    for ticker in tickers:
        companies_data.append(yf.download(ticker, start=start_date, end=end_date))

    # Preprocess data and split into training and testing sets
    data_splits = []
    for df in companies_data:
        data_splits.append(split_data(df))

    # Initialize matrices to store results
    n_companies = len(tickers)
    returns_dict = {model: [0]*n_companies for model in models}
    confidence_intervals_dict = {model: [[0, 0] for _ in range(n_companies)] for model in models}  # lower and upper bounds
    uncertainty_dict = {model: [0]*n_companies for model in models}

    # Train models and calculate predictions
    predicted_returns = []
    for i, (X_train, X_test, y_train, y_test) in enumerate(data_splits):
        predictions = train_and_predict(X_train, y_train, X_test)
        uncertainties = train_and_predict(X_train, y_train, X_test)
        predicted_returns.append(predictions)

        for _, model in enumerate(models):
            # Store predictions
            returns_dict[model][i] = predictions[model].mean()

            # Store confidence intervals (95% CI)
            confidence_intervals_dict[model][i][0] = predictions[model].mean() - 1.96 * uncertainties[model].mean()
            confidence_intervals_dict[model][i][1] = predictions[model].mean() + 1.96 * uncertainties[model].mean()

            # Calculate uncertainty as the width of the confidence interval
            uncertainty_dict[model][i] = confidence_intervals_dict[model][i][1] - confidence_intervals_dict[model][i][0]
    return returns_dict, confidence_intervals_dict, uncertainty_dict

# Download historical data for each stock
def combined_data(tickers, start_date="2022-12-31", end_date="2024-03-31", risk_free_rate=0.02, save=False, output_dir="./"):
    data = {}
    for ticker in tickers:
        data[ticker] = yf.download(ticker, start=start_date, end=end_date)[['Open', 'Adj Close']]

    # Combine the data into a single DataFrame
    df_combined = pd.DataFrame()
    for ticker in tickers:
        df_temp = data[ticker].copy()
        df_temp.columns = [f'{ticker}_Open', f'{ticker}_Close']
        df_combined = pd.merge(df_combined, df_temp, left_index=True, right_index=True, how='outer')

    # Add a sample risk-free rate (e.g., 1% per year, constant)
    df_combined['RiskFreeRate'] = risk_free_rate

    # Save the combined DataFrame to a CSV file
    if save:
        df_combined.to_csv(f'{output_dir}combined_stock_data.csv')

    # Display the combined DataFrame
    print(df_combined.head())
    return df_combined

def get_returns(tickers, df_combined):
    assets = []
    for ticker in tickers:
        assets.append(f"{ticker}_Close")
    for asset in assets:
        df_combined[f'{asset}_Return'] = df_combined[asset].pct_change()

    # Drop NaN values
    df_combined.dropna(inplace=True)

    # Select return columns
    return_columns = [f'{asset}_Return' for asset in assets]
    returns = df_combined[return_columns]

    return returns
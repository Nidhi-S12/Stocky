import tensorflow.keras as keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import pandas as pd
import tensorflow as tf
import random
import os

import pandas_ta as ta
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import RobustScaler
from datetime import timedelta

def set_seeds(seed=42):
    """Set seeds for reproducibility"""
    np.random.seed(seed)
    random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    # Force TensorFlow to use single thread
    # Multiple threads are a source of non-reproducible results
    session_conf = tf.compat.v1.ConfigProto(
        intra_op_parallelism_threads=1,
        inter_op_parallelism_threads=1
    )
    sess = tf.compat.v1.Session(config=session_conf)
    tf.compat.v1.keras.backend.set_session(sess)

def calculate_features(df):
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Close'].rolling(window=10).std()
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['EMA_20'] = df['Close'].ewm(span=20).mean()
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACDs'] = macd['MACDs_12_26_9']
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df

def prepare_data_simple(df, time_steps=60):
    df_features = calculate_features(df)
    features_list = ['Close', 'Return', 'Volatility', 'MA_20', 'EMA_20', 'MACD', 'MACDs', 'RSI']
    features_data = df_features[features_list].values
    scaler = RobustScaler()
    scaled = scaler.fit_transform(features_data)
    
    X, y = [], []
    for i in range(time_steps, len(scaled)):
        X.append(scaled[i - time_steps:i])
        y.append(scaled[i, 0])
    return np.array(X), np.array(y), scaler, features_list

def build_simple_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(64, input_shape=input_shape, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

def train_and_evaluate(df, time_steps=60):
    X, y, scaler, features_list = prepare_data_simple(df, time_steps)
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = build_simple_lstm_model((X.shape[1], X.shape[2]))
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    history = model.fit(X_train, y_train, epochs=50, batch_size=32, 
                        validation_data=(X_test, y_test), callbacks=[early_stop], verbose=0)

    preds = model.predict(X_test, verbose=0)
    actual = y_test

    center = scaler.center_[0]
    scale = scaler.scale_[0]
    preds_rescaled = preds.flatten() * scale + center
    actual_rescaled = actual * scale + center

    rmse = np.sqrt(mean_squared_error(actual_rescaled, preds_rescaled))
    print(f"Test RMSE: {rmse:.4f}")
    return model, scaler, preds_rescaled, actual_rescaled, history, X_test, y_test, features_list

def predict_next_days(df, model, scaler, days=10, time_steps=60):
    df = df.copy()
    features_list = ['Close', 'Return', 'Volatility', 'MA_20', 'EMA_20', 'MACD', 'MACDs', 'RSI']
    
    df_features = calculate_features(df)
    features_data = df_features[features_list].values
    scaled_features = scaler.transform(features_data)
    if len(scaled_features) < time_steps:
        raise ValueError("Not enough data for prediction")
    sequence = scaled_features[-time_steps:].copy()
    
    future_preds = []
    for _ in range(days):
        input_seq = sequence.reshape(1, time_steps, -1)
        pred_scaled = model.predict(input_seq, verbose=0)[0][0]
        
        center = scaler.center_[0]
        scale = scaler.scale_[0]
        pred = pred_scaled * scale + center
        future_preds.append(pred)
        
        last_date = df.index[-1]
        future_date = last_date + pd.Timedelta(days=1)
        new_row = pd.Series(data={'Close': pred}, name=future_date)
        df = pd.concat([df, new_row.to_frame().T])
        
        df_features = calculate_features(df)
        last_features = df_features[features_list].iloc[-1:].values
        last_scaled = scaler.transform(last_features)
        sequence = np.vstack([sequence[1:], last_scaled])
    
    return future_preds

def predict_future_prices(model, scaler, df, feature_columns, days=30, time_steps=60):
    preds = predict_next_days(df, model, scaler, days=days, time_steps=time_steps)
    last_date = df.index[-1]
    future_dates = []
    current_date = last_date
    for _ in range(days):
        current_date += timedelta(days=1)
        while current_date.weekday() >= 5:
            current_date += timedelta(days=1)
        future_dates.append(current_date)
    return np.array(preds), future_dates

def evaluate_model(model, scaler, X_test, y_test, feature_columns):
    try:
        test_pred_scaled = model.predict(X_test, verbose=0).flatten()
        n = min(len(test_pred_scaled), len(y_test))
        test_pred_scaled = test_pred_scaled[-n:]
        actual_scaled = y_test[-n:]
        center = scaler.center_[0]
        scale = scaler.scale_[0]
        test_pred_inverse = test_pred_scaled * scale + center
        test_actual_inverse = actual_scaled * scale + center

        mae = float(mean_absolute_error(test_actual_inverse, test_pred_inverse))
        rmse = float(np.sqrt(mean_squared_error(test_actual_inverse, test_pred_inverse)))
        mape = float(np.mean(np.abs((test_actual_inverse - test_pred_inverse) / 
                                    (test_actual_inverse + 1e-10))) * 100)
        r2 = float(r2_score(test_actual_inverse, test_pred_inverse))
        metrics = {
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "r2": r2,
            "test_pred_inverse": test_pred_inverse,
            "test_actual_inverse": test_actual_inverse
        }
        return metrics
    except Exception as e:
        raise Exception(f"Error evaluating model: {str(e)}")

def save_trained_model(model, scaler, feature_columns, path="./saved_model"):
    """Save the trained model and its metadata"""
    if not os.path.exists(path):
        os.makedirs(path)
    model.save(f"{path}/lstm_model")
    np.save(f"{path}/scaler_center.npy", scaler.center_)
    np.save(f"{path}/scaler_scale.npy", scaler.scale_)
    with open(f"{path}/feature_columns.txt", "w") as f:
        f.write(",".join(feature_columns))
    print(f"Model saved to {path}")

def load_trained_model(path="./saved_model"):
    """Load the trained model and its metadata"""
    from sklearn.preprocessing import RobustScaler
    from tensorflow.keras.models import load_model
    
    model = load_model(f"{path}/lstm_model")
    scaler = RobustScaler()
    # We need to set these attributes manually
    scaler.center_ = np.load(f"{path}/scaler_center.npy")
    scaler.scale_ = np.load(f"{path}/scaler_scale.npy")
    with open(f"{path}/feature_columns.txt", "r") as f:
        feature_columns = f.read().split(",")
    return model, scaler, feature_columns

def train_lstm_model(df, time_steps=60):
    # Set seeds for reproducibility
    set_seeds(42)
    
    model, scaler, preds_rescaled, actual_rescaled, history, X_test, y_test, feature_columns = train_and_evaluate(df, time_steps)
    df_clean = df
    # After training, save the model
    save_trained_model(model, scaler, feature_columns)
    return model, scaler, X_test, y_test, df_clean, feature_columns, history

def detect_currency(ticker, stock_info=None):
    """Detect the currency for a stock ticker"""
    ticker = ticker.upper()
    
    # Indian stock exchanges
    if (ticker.endswith('.NS') or ticker.endswith('.BO') or 
        ticker in ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICI', 'SBIN', 'ITC', 'HDFCBANK', 'BHARTIARTL', 'ASIANPAINT']):
        return 'INR', '₹'
    
    # European stocks
    if ticker.endswith('.PA') or ticker.endswith('.DE') or ticker.endswith('.MI'):
        return 'EUR', '€'
    
    # UK stocks
    if ticker.endswith('.L'):
        return 'GBP', '£'
    
    # Japanese stocks
    if ticker.endswith('.T'):
        return 'JPY', '¥'
    
    # Try to get from stock info if available
    if stock_info:
        currency = stock_info.get('currency', 'USD')
        currency_symbols = {
            'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 
            'JPY': '¥', 'CAD': 'C$', 'AUD': 'A$', 'CHF': 'CHF',
            'CNY': '¥', 'KRW': '₩'
        }
        return currency, currency_symbols.get(currency, currency)
    
    # Default to USD
    return 'USD', '$'
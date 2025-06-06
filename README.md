# AI Stock Price Predictor

This project is an interactive Streamlit web application for stock price prediction using deep learning (LSTM) and advanced technical indicators. It uses `yfinance` for data, `pandas-ta` for technical features, and a simple LSTM model for forecasting.

## Features

- **Historical Data Fetching:** Retrieves stock price data using Yahoo Finance.
- **Feature Engineering:** Computes technical indicators with [pandas-ta](https://github.com/twopirllc/pandas-ta):
  - Moving Averages (MA-20, EMA-20)
  - MACD (12,26,9) & Signal
  - RSI (14)
  - Volatility, Returns
- **Deep Learning Model:** LSTM-based neural network with dropout and dense layers.
- **Prediction Visualization:** Interactive charts for historical and predicted prices, volume, and confidence intervals.
- **Performance Metrics:** MAE, RMSE, MAPE, R².
- **Downloadable Results:** Export predictions as CSV.
- **Simple, Fast Pipeline:** Designed for quick experimentation and educational use.

## Architecture
The system architecture follows a streamlined workflow:

1. **Data Collection Layer**: Yahoo Finance API retrieves historical stock data
2. **Preprocessing Layer**: Technical indicators are calculated and data is normalized
3. **Model Layer**: LSTM neural network trained on prepared features
4. **Prediction Layer**: Future price predictions with confidence intervals
5. **Visualization Layer**: Interactive Streamlit UI displays results and insights

The LSTM model architecture consists of:
- Input layer with time-series features
- LSTM layer with 64 units
- Dropout layer (0.2) for regularization
- Dense layer with 32 units and ReLU activation
- Output layer for price prediction

| ![](/assets/architecture.png) 

## Project Structure

```
.
├── main.py            # Streamlit app UI and workflow
├── model.py           # Feature engineering, model training, prediction, evaluation
├── requirements.txt   # Python dependencies
├── assets/            # Diagrams and images
│   └── architecture_diagram.png  # System architecture diagram
└── README.md          # Project documentation
```

## How It Works

1. **User selects a stock, date range, and prediction settings in the sidebar.**
2. **App fetches historical price data and computes technical indicators.**
3. **LSTM model is trained on the features with early stopping.**
4. **Future prices are predicted and visualized with performance metrics.**
5. **Results can be downloaded for further analysis.**

## Setup

1. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    Make sure to include:
    ```
    streamlit
    yfinance
    pandas
    pandas-ta
    tensorflow
    scikit-learn
    plotly
    ```

2. **Run the app:**
    ```bash
    streamlit run main.py
    ```

## Update

This project now features a streamlined LSTM-based stock prediction pipeline with advanced technical indicators powered by `pandas-ta`. The app is faster, easier to use, and provides more insightful analytics with improved feature engineering and interactive visualizations. Simply select your stock and date range, and get instant AI-driven forecasts and performance metrics.

## Notes

- The pipeline uses a simple LSTM model and a small set of technical indicators for speed and clarity.
- For production or research, you can extend the feature set, tune hyperparameters, or add more advanced models.
- The app is for educational and research purposes only.
- Supports international stocks with appropriate currency display (USD, INR, EUR, etc.)

## Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies.

## Credits

- Built with [Streamlit](https://streamlit.io/), [TensorFlow/Keras](https://www.tensorflow.org/), [pandas-ta](https://github.com/twopirllc/pandas-ta), [yfinance](https://github.com/ranaroussi/yfinance), and [Plotly](https://plotly.com/python/).

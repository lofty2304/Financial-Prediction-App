# app.py - Flask Backend for AuraLens Capital Dashboard

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import ta # For technical analysis indicators

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing frontend to access

@app.route('/get_stock_data', methods=['GET'])
def get_stock_data():
    """
    Fetches historical stock data and calculates technical indicators.
    Expected query parameters:
    - ticker: Stock ticker symbol (e.g., 'AAPL', 'NBCC.NS' for NSE)
    - days: Number of historical days to fetch (default: 365)
    """
    ticker_symbol = request.args.get('ticker', 'AAPL')
    days = int(request.args.get('days', 365))

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        # Fetch data using yfinance
        # yfinance can handle many international stocks by appending exchange suffixes
        # e.g., 'NBCC.NS' for NSE, 'SAGILITY.BO' for BSE
        data = yf.download(ticker_symbol, start=start_date, end=end_date)

        if data.empty:
            return jsonify({"error": f"No data found for {ticker_symbol}. Please check the ticker symbol and ensure it's valid for the selected exchange (e.g., NBCC.NS for NSE). If it's a mutual fund, direct NAV APIs are required."}), 404

        # Calculate Technical Indicators
        # Ensure 'Close' column exists and is numeric
        if 'Close' not in data.columns:
            return jsonify({"error": "Close price column not found in fetched data."}), 500
        
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        data.dropna(subset=['Close'], inplace=True) # Drop rows where Close is NaN after coercion

        # SMA (20)
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        
        # RSI (14)
        # Ensure the series is suitable for RSI calculation
        close_series = data['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.squeeze() # Convert DataFrame to Series if necessary
        data['RSI_14'] = ta.momentum.rsi(close_series, window=14)

        # Handle NaN values for indicators (e.g., fill with None or 0 for JSON serialization)
        data = data.replace({np.nan: None})

        # Prepare data for JSON response
        response_data = {
            "dates": data.index.strftime('%Y-%m-%d').tolist(),
            "prices": data['Close'].tolist(),
            "sma20": data['SMA_20'].tolist(),
            "rsi14": data['RSI_14'].tolist(),
            "last_close": data['Close'].iloc[-1],
            "avg_close_30_days": data['Close'].tail(30).mean(),
            "52_week_high": data['Close'].max(),
            "52_week_low": data['Close'].min()
        }

        return jsonify(response_data), 200

    except Exception as e:
        app.logger.error(f"Error fetching data for {ticker_symbol}: {e}")
        return jsonify({"error": f"Failed to fetch data for {ticker_symbol}: {str(e)}"}), 500

if __name__ == '__main__':
    # For local development, run on port 5000
    # In a production environment (like Render), the port will be set by the platform
    app.run(debug=True, host='0.0.0.0', port=5000)

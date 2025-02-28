# Stock News Sentiment Dashboard

A Streamlit-powered dashboard that displays real-time stock news with ML-based sentiment analysis and technical signals.

## Features
- Real-time stock news aggregation
- Advanced ML-based sentiment analysis using FinBERT
- Technical analysis signals using indicators (RSI, MACD, Bollinger Bands)
- Auto-refreshing data feed
- Clickable news headlines with source links
- IST timezone support

## Dependencies
- Python 3.11+

### Python Packages
```txt
streamlit==1.31.0
pandas==2.2.0
numpy==1.26.0
gnews==0.3.6
nltk==3.8.1
torch==2.1.0
transformers==4.36.0
yfinance==0.2.35
ta==0.11.0
pytz==2024.1
```

### System Dependencies (packages.txt)
```txt
python3-dev
build-essential
git
```

## Deployment on Hugging Face Spaces

1. Create a new Space:
   - Choose "Streamlit" as the SDK
   - Select Python 3.11

2. Files to upload:
   - All Python files from the `utils/` directory
   - `main.py` and `background_worker.py`
   - `.streamlit/config.toml`
   - `styles/custom.css`
   - `attached_assets/MW-SECURITIES-IN-F&O-28-Feb-2025.csv`

3. The Spaces deployment will automatically:
   - Install dependencies from requirements.txt
   - Install system packages from packages.txt
   - Start the Streamlit server

4. Environment setup is handled automatically by Hugging Face Spaces.

## Local Development
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the background worker:
   ```bash
   python background_worker.py
   ```
4. Start the Streamlit app:
   ```bash
   streamlit run main.py
   ```
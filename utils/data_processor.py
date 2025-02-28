import pandas as pd
import time
from datetime import datetime
import pytz
import json
from pathlib import Path
from utils.news_fetcher import NewsFetcher
from utils.ml_sentiment_analyzer import MLSentimentAnalyzer
import ta
import numpy as np
import yfinance as yf

class DataProcessor:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.sentiment_analyzer = MLSentimentAnalyzer()
        self.cache_file = Path('data_cache/news_data.json')
        self.cache_file.parent.mkdir(exist_ok=True)

        # Initialize cache if it doesn't exist
        if not self.cache_file.exists():
            self.process_data()

    def get_technical_signals(self, symbol):
        try:
            # Get stock data from yfinance
            ticker = yf.Ticker(f"{symbol}.NS")  # Assuming NSE symbols
            hist = ticker.history(period="1mo")

            if len(hist) < 14:  # Need minimum data for indicators
                return "Neutral"

            # Calculate technical indicators using 'ta' library
            # RSI
            rsi = ta.momentum.RSIIndicator(hist['Close'], window=14).rsi().iloc[-1]

            # MACD
            macd = ta.trend.MACD(hist['Close'])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]

            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(hist['Close'])
            bb_high = bollinger.bollinger_hband().iloc[-1]
            bb_low = bollinger.bollinger_lband().iloc[-1]
            current_price = hist['Close'].iloc[-1]

            # Combine signals
            signals = []

            # RSI signals
            if rsi > 70:
                signals.append("Overbought")
            elif rsi < 30:
                signals.append("Oversold")

            # MACD signals
            if macd_line > signal_line:
                signals.append("Bullish")
            else:
                signals.append("Bearish")

            # Bollinger Bands signals
            if current_price > bb_high:
                signals.append("Overbought")
            elif current_price < bb_low:
                signals.append("Oversold")

            # Determine final signal
            bullish_count = len([s for s in signals if s in ["Bullish", "Oversold"]])
            bearish_count = len([s for s in signals if s in ["Bearish", "Overbought"]])

            if bullish_count > bearish_count:
                return "Bullish"
            elif bearish_count > bullish_count:
                return "Bearish"
            else:
                return "Neutral"

        except Exception as e:
            print(f"Error getting technical signals for {symbol}: {str(e)}")
            return "Neutral"

    def process_data(self):
        try:
            symbols = self.news_fetcher.read_symbols('attached_assets/MW-SECURITIES-IN-F&O-28-Feb-2025.csv')[1:]
            news_data = []
            processed_count = 0

            for symbol in symbols:
                try:
                    news = self.news_fetcher.get_news_for_symbol(symbol)
                    if news:
                        sentiment, score = self.sentiment_analyzer.analyze_sentiment(news['title'])
                        published_dt = datetime.strptime(news['published_date'], '%a, %d %b %Y %H:%M:%S GMT')
                        published_dt = published_dt.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone('Asia/Kolkata'))

                        # Get technical signals
                        tech_signal = self.get_technical_signals(symbol)

                        news_data.append({
                            'Symbol': symbol,
                            'Sentiment': sentiment,
                            'Score': score,
                            'Technical': tech_signal,
                            'Headline': news['title'],
                            'Published': published_dt.strftime('%Y-%m-%d %I:%M %p IST'),
                            'Timestamp': published_dt.isoformat(),
                            'URL': news['url']
                        })
                        processed_count += 1
                        print(f"Processed {processed_count} symbols with news")
                except Exception as e:
                    print(f"Error processing symbol {symbol}: {str(e)}")
                    continue

            if news_data:  # Only update if we have data
                # Sort by timestamp
                news_data.sort(key=lambda x: x['Timestamp'], reverse=True)

                # Save to cache file
                self.cache_file.write_text(json.dumps(news_data))
                print(f"Updated cache with {len(news_data)} news items")
                return True
            elif self.cache_file.exists():  # Keep existing data if new fetch fails
                print("No new data fetched, keeping existing cache")
                return True
            else:
                print("No data available and no existing cache")
                return False

        except Exception as e:
            print(f"Error in process_data: {str(e)}")
            return False

    def run_continuous(self):
        while True:
            print("Processing data...")
            self.process_data()
            time.sleep(60)  # Update every minute

    def get_cached_data(self):
        try:
            if self.cache_file.exists():
                data = json.loads(self.cache_file.read_text())
                return pd.DataFrame(data)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading cache: {str(e)}")
            return pd.DataFrame()
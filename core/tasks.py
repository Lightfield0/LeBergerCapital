from django.db import IntegrityError
import yfinance as yf
from .models import StockData
from celery import shared_task

@shared_task
def fetch_and_save_stock_data():
    ticker_sectors = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "NVDA": "Technology",
        "WMT": "Consumer Products",
        "MC.PA": "Consumer Products",
        "KO": "Consumer Products",
        "AIR": "Industrial",
        "SAF.PA": "Industrial",
        "GE": "Industrial"
    }

    for ticker, sector in ticker_sectors.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")

        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            percentage_change = ((current_price - open_price) / open_price) * 100


            # Fetch additional info
            info = stock.info

            # Update or create the stock data object
            stock_data, created = StockData.objects.update_or_create(
                ticker=ticker,
                defaults={
                    'sector': sector,
                    'current_price': current_price,
                    'open_price': open_price,
                    'percentage_change': percentage_change,
                    'info': info,  # Directly assign if using JSONField
                    # 'info': json.dumps(info) if using TextField
                }
            )
            if created:
                print(f"Created new record for {ticker}")
            else:
                print(f"Updated record for {ticker}")

from celery import shared_task
from django.db import transaction
from .models import StockData
from .stockAnalyzer import AggressiveStockAnalyzer, ConservativeStockAnalyzer
import yfinance as yf


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

        # Fetch additional info
        info = stock.info

        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            percentage_change = ((current_price - open_price) / open_price) * 100

            # Create and save the stock data object
            StockData.objects.create(
                ticker=ticker,
                sector=sector,
                current_price=current_price,
                open_price=open_price,
                percentage_change=percentage_change,
                info=info,  # Directly assign if using JSONField
                # info=json.dumps(info) if using TextField
            )
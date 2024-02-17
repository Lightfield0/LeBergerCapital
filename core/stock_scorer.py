import yfinance as yf
import pandas as pd
import math

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            percentage_change = ((current_price - open_price) / open_price) * 100
        else:
            current_price, open_price, percentage_change = 0, 0, 0

        info = stock.info

        stock_data = {
            "Stock Price": current_price,
            "Dividends": info.get("dividendYield", 0) * 100 if info.get("dividendYield") is not None else 0,
            "P/E Ratio": info.get("trailingPE", 0),
            "Transaction Volume": info.get("averageVolume", 0),
            "P/B Ratio": info.get("priceToBook", 0),
            "Revenue Growth": info.get("revenueGrowth", 0),
            "Profit Margin": info.get("profitMargins", 0),
            "Sector Beta": info.get("beta", 0),
            "FiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
            "Last Close": info.get("regularMarketPreviousClose", 0),
            "Daily Variation": f"{info.get('regularMarketDayLow', 0)} - {info.get('regularMarketDayHigh', 0)}",
            "Yearly Range": f"{info.get('fiftyTwoWeekLow', 0)} - {info.get('fiftyTwoWeekHigh', 0)}",
            "Market Cap": info.get("marketCap", 0),
            "Average Volume": info.get("averageVolume", 0),
            "Yield (Dividends)": f"{info.get('dividendYield', 0) * 100 if info.get('dividendYield') is not None else 0} %",
            "Main Exchange": info.get("exchange", ""),
            "Percentage Change for the Day": f"{percentage_change} %"
        }

    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        stock_data = {}  

    return stock_data

def normalize_data_aggressive(stock_data):
  normalized_data = {}

  # Stock Price
  max_price = stock_data["FiftyTwoWeekHigh"]
  current_price = stock_data["Stock Price"]
  normalized_data["Stock Price"] = (current_price / max_price) * 5 if max_price else 0

  # Dividends
  dividend_yield = stock_data["Dividends"]
  normalized_data["Dividends"] = dividend_yield * 2

  # P/E Ratio
  pe_ratio = stock_data["P/E Ratio"]
  normalized_data["P/E Ratio"] = min(pe_ratio, 10) if pe_ratio else 0

  # Transaction Volume
  average_volume = stock_data["Transaction Volume"]
  max_volume = stock_data["Average Volume"]
  normalized_data["Transaction Volume"] = (math.log(average_volume + 1) / math.log(max_volume + 1)) * 5 if average_volume else 0

  # P/B Ratio
  pb_ratio = stock_data["P/B Ratio"]
  normalized_data["P/B Ratio"] = min(10, (1 / (pb_ratio + 0.01)) * 15) if pb_ratio else 0

  # Revenue Growth
  revenue_growth = stock_data["Revenue Growth"]
  normalized_data["Revenue Growth"] = min(20, revenue_growth * 20)

  # Profit Margin
  profit_margin = stock_data["Profit Margin"]
  normalized_data["Profit Margin"] = profit_margin * 10

  # Sector Beta
  beta = stock_data["Sector Beta"]
  normalized_data["Sector Beta"] = min(10, (beta + 1) * 10) if beta else 0

  return normalized_data

def calculate_score(normalized_data, weights):
    total_score = 0
    for key in normalized_data:
        total_score += normalized_data[key] * weights.get(key, 0)
    return total_score

aggressive_weights = {
    "Stock Price": 0.05,  
    "Dividends": 0.05,      
    "P/E Ratio": 0.10,  
    "Transaction Volume": 0.05,     
    "P/B Ratio": 0.20,  
    "Revenue Growth": 0.30,      
    "Profit Margin": 0.10,          
    "Sector Beta": 0.15              
}

def fetch_and_score_stocks(tickers, weights):
  results = {}
  for ticker in tickers:
      stock_data = get_stock_data(ticker)
      normalized_data = normalize_data_aggressive(stock_data)
      score = calculate_score(normalized_data, weights)
      results[ticker] = {"Score": score, "Data": stock_data}

  sorted_results = dict(sorted(results.items(), key=lambda item: item[1]["Score"], reverse=True))

  return sorted_results

# Example usage
tickers_example = ["AAPL", "MSFT", "NVDA"]
sorted_scores = fetch_and_score_stocks(tickers_example, aggressive_weights)

for rank, (ticker, data) in enumerate(sorted_scores.items(), start=1):
    print(f"{'='*40}")  
    print(f"Rank {rank}: Ticker: {ticker}, Score: {data['Score']}\n")
    for key, value in data["Data"].items():
        print(f"{key}: {value}")
    print("\n")

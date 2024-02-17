import yfinance as yf
import math

class StockAnalyzer:
    def __init__(self, tickers, weights):
        self.tickers = tickers
        self.weights = weights
        self.results = {}

    def fetch_and_score_stocks(self):
        for ticker in self.tickers:
            stock_data = self.get_stock_data(ticker)
            if stock_data:  # Ensure stock_data is not empty
                normalized_data = self.normalize_data_aggressive(stock_data)
                score = self.calculate_score(normalized_data)
                self.results[ticker] = {"Score": score, "Data": stock_data}
        self.sort_results()

    def get_stock_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="1m")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[0]
                percentage_change = ((current_price - open_price) / open_price) * 100
            else:
                return {}  # Return empty if no historical data

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
                "Percentage Change for the Day": percentage_change
            }
            return stock_data
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            return {}

    def normalize_data_aggressive(self, stock_data):
        normalized_data = {
            "Stock Price": (stock_data["Stock Price"] / stock_data["FiftyTwoWeekHigh"]) * 5 if stock_data["FiftyTwoWeekHigh"] else 0,
            "Dividends": stock_data["Dividends"] * 2,
            "P/E Ratio": min(stock_data["P/E Ratio"], 10) if stock_data["P/E Ratio"] else 0,
            "Transaction Volume": (math.log(stock_data["Transaction Volume"] + 1) / math.log(stock_data["Average Volume"] + 1)) * 5 if stock_data["Transaction Volume"] else 0,
            "P/B Ratio": min(10, (1 / (stock_data["P/B Ratio"] + 0.01)) * 15) if stock_data["P/B Ratio"] else 0,
            "Revenue Growth": min(20, stock_data["Revenue Growth"] * 20),
            "Profit Margin": stock_data["Profit Margin"] * 10,
            "Sector Beta": min(10, (stock_data["Sector Beta"] + 1) * 10) if stock_data["Sector Beta"] else 0,
        }
        return normalized_data

    def calculate_score(self, normalized_data):
        total_score = 0
        for key in normalized_data:
            total_score += normalized_data[key] * self.weights.get(key, 0)
        return total_score

    def sort_results(self):
        self.results = dict(sorted(self.results.items(), key=lambda item: item[1]["Score"], reverse=True))

    def display_results(self):
        for rank, (ticker, data) in enumerate(self.results.items(), start=1):
            print(f"{'='*40}")  
            print(f"Rank {rank}: Ticker: {ticker}, Score: {data['Score']}\n")
            for key, value in data["Data"].items():
                print(f"{key}: {value}")
            print("\n")

# Example usage
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

tickers_example = ["AAPL", "MSFT", "NVDA"]
analyzer = StockAnalyzer(tickers_example, aggressive_weights)
analyzer.fetch_and_score_stocks()
analyzer.display_results()
# print(analyzer.results)

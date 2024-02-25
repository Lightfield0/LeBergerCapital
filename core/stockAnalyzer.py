from .models import StockData
import yfinance as yf
import math

class AggressiveStockAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers
        self.weights = {
        "Stock Price": 0.05,  
        "Dividends": 0.05,      
        "P/E Ratio": 0.10,  
        "Transaction Volume": 0.05,     
        "P/B Ratio": 0.20,  
        "Revenue Growth": 0.30,      
        "Profit Margin": 0.10,          
        "Sector Beta": 0.15              
        }
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
            stock = StockData.objects.filter(ticker=ticker)
            # stock = yf.Ticker(ticker)
            # hist = stock.history(period="1d", interval="1m")
            # if not hist.empty:
            current_price = stock.current_price
            open_price = stock.open_price
            percentage_change = stock.percentage_change
            # else:
            #     return {}  # Return empty if no historical data

            info = stock.info
            sozluk = {
                "Summary": {
                    "Previous Close": info.get('previousClose'),
                    "Open": info.get('open'),
                    # "Bid": info.get('bidSize'),
                    # "Ask": info.get('askSize'),
                    "Day's Range": f"{info.get('dayLow')} - {info.get('dayHigh')}",
                    "52 Week Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
                    "Volume": info.get('volume'),
                    "Avg. Volume": info.get('averageVolume'),
                    "Market Cap": info.get('marketCap'),
                    "Beta (5Y Monthly)": info.get('beta'),
                    "PE Ratio (TTM)": info.get('trailingPE'),
                    "EPS (TTM)": info.get('trailingEps'),
                    "Earnings Date": info.get('timeZoneFullName'),  # Potentially incorrect, consider verifying the correct key for Earnings Date
                    # "Forward Dividend & Yield": f"{info.get('dividendRate')} - {info.get('dividendYield')}",
                    "Ex-Dividend Date": info.get('exDividendDate'),
                    "1y Target Est": info.get('targetMeanPrice'),
                },
                "Statistics": {
                    "Valuation Measures": {
                        "Market Cap (intraday)": info.get('marketCap'),
                        "Enterprise Value": info.get('enterpriseValue'),
                        "Trailing P/E": info.get('trailingPE'),
                        "Forward P/E": info.get('forwardPE'),
                        "PEG Ratio (5 yr expected)": info.get('pegRatio'),
                        "Price/Sales (ttm)": info.get('priceToSalesTrailing12Months'),
                        "Price/Book (mrq)": info.get('priceToBook'),
                        "Enterprise Value/Revenue": info.get('enterpriseToRevenue'),
                        "Enterprise Value/EBITDA": info.get('enterpriseToEbitda'),
                    },
                    "Financial Highlights": {
                        "Fiscal Year": {
                            "Fiscal Year Ends": f"{info.get('lastFiscalYearEnd')} - {info.get('nextFiscalYearEnd')}",
                            "Most Recent Quarter (mrq)": info.get('mostRecentQuarter'),
                        },
                        "Profitability": {
                            "Profit Margin": info.get('profitMargins'),
                            "Operating Margin (ttm)": info.get('operatingMargins'),
                        },
                        "Management Effectiveness": {
                            "Return on Assets (ttm)": info.get('returnOnAssets'),
                            "Return on Equity (ttm)": info.get('returnOnEquity'),
                        },
                        "Income Statement": {
                            "Revenue (ttm)": info.get('totalRevenue'),
                            "Revenue Per Share (ttm)": info.get('revenuePerShare'),
                            "Quarterly Revenue Growth (yoy)": info.get('totalRevenue'),
                            # "Gross Profit (ttm)": info.get(''),
                            "EBITDA": info.get('ebitda'),
                            "Net Income Avi to Common (ttm)": info.get('netIncomeToCommon'),
                            "Diluted EPS (ttm)": info.get('trailingEps'),
                            # "Quarterly Earnings Growth (yoy)": info.get('earningsQuarterlyGrowth'),
                        },
                        "Balance Sheet": {
                            "Total Cash (mrq)": info.get('totalCash'),
                            "Total Cash Per Share (mrq)": info.get('totalCashPerShare'),
                            "Total Debt (mrq)": info.get('totalDebt'),
                            "Total Debt/Equity (mrq)": info.get('debtToEquity'),
                            "Current Ratio (mrq)": info.get('currentRatio'),
                            "Book Value Per Share (mrq)": info.get('bookValue'),
                        },
                        "Cash Flow Statement": {
                            "Operating Cash Flow (ttm)": info.get('operatingCashflow'),
                            "Levered Free Cash Flow (ttm)": info.get('freeCashflow'),
                        },
                    },
                    "Trading Information": {
                        "Stock Price History": {
                            "Beta (5Y Monthly)": info.get('beta'),
                            "52-Week Change 3": info.get('52WeekChange'),
                            "S&P500 52-Week Change 3": info.get('SandP52WeekChange'),
                            "52 Week High 3": info.get('fiftyTwoWeekHigh'),
                            "52 Week Low 3": info.get('fiftyTwoWeekLow'),
                            "50-Day Moving Average 3": info.get('fiftyDayAverage'),
                            "200-Day Moving Average 3": info.get('twoHundredDayAverage'),
                        },
                        "Share Statistics": {
                            "Avg Vol (3 month) 3": info.get('averageVolume'),
                            "Avg Vol (10 day) 3": info.get('regularMarketVolume'),
                            "Shares Outstanding 5": info.get('sharesOutstanding'),
                            "Implied Shares Outstanding 6": info.get('impliedSharesOutstanding', None),  # Using None as a default value if key doesn't exist
                            "Float 8": info.get('floatShares'),
                            "% Held by Insiders 1": info.get('heldPercentInsiders'),
                            "% Held by Institutions 1": info.get('heldPercentInstitutions'),
                            "Shares Short (Jan 31, 2024) 4": info.get('sharesShort'),
                            "Short Ratio (Jan 31, 2024) 4": info.get('shortRatio'),
                            "Short % of Float (Jan 31, 2024) 4": info.get('shortPercentOfFloat'),
                            "Short % of Shares Outstanding (Jan 31, 2024) 4": info.get('sharesPercentSharesOut'),
                            "Shares Short (prior month Dec 29, 2023) 4": info.get('sharesShortPriorMonth'),
                        },
                        "Dividends & Splits": {
                            "Forward Annual Dividend Rate 4": info.get('dividendRate'),
                            "Forward Annual Dividend Yield 4": info.get('dividendYield'),
                            "Trailing Annual Dividend Rate 3": info.get('trailingAnnualDividendRate'),
                            "Trailing Annual Dividend Yield 3": info.get('trailingAnnualDividendYield'),
                            "5 Year Average Dividend Yield 4": info.get('fiveYearAvgDividendYield'),
                            "Payout Ratio 4": info.get('payoutRatio'),
                            "Dividend Date 3": info.get('lastDividendDate'),  # Potentially incorrect, consider verifying the correct key for Dividend Date
                            "Ex-Dividend Date 4": info.get('exDividendDate'),
                            "Last Split Factor 2": info.get('lastSplitFactor'),
                            "Last Split Date 3": info.get('lastSplitDate'),
                        }
                    }
                }
            }

            stock_data = {
                "AllData": sozluk,
                "Name": info.get('shortName'),
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


class ConservativeStockAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers
        self.weights = {
            "Stock Price": 0.05,  
            "Dividends": 0.25,      
            "P/E Ratio": 0.20,  
            "Transaction Volume": 0.05,     
            "P/B Ratio": 0.10,  
            "Revenue Growth": 0.05,      
            "Profit Margin": 0.10,          
            "Sector Beta": 0.20              
        }
        self.results = {}

    def fetch_and_score_stocks(self):
        for ticker in self.tickers:
            stock_data = self.get_stock_data(ticker)
            if stock_data:  
                normalized_data = self.normalize_data_conservative(stock_data)  
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
                return {}  

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

    def normalize_data_conservative(self, stock_data):
        normalized_data = {
            "Stock Price": (stock_data["Stock Price"] / stock_data["FiftyTwoWeekHigh"]) * 10 if stock_data["FiftyTwoWeekHigh"] else 0,
            "Dividends": stock_data["Dividends"] * 10,
            "P/E Ratio": min(stock_data["P/E Ratio"], 10) if stock_data["P/E Ratio"] else 0,
            "Transaction Volume": (math.log(stock_data["Transaction Volume"] + 1) / math.log(stock_data["Average Volume"] + 1)) * 5 if stock_data["Transaction Volume"] else 0,
            "P/B Ratio": min(10, (1 / (stock_data["P/B Ratio"] + 0.01)) * 10) if stock_data["P/B Ratio"] else 0,
            "Revenue Growth": stock_data["Revenue Growth"] * 5,
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

# # Example usage
# aggressive_weights = {
#     "Stock Price": 0.05,  
#     "Dividends": 0.05,      
#     "P/E Ratio": 0.10,  
#     "Transaction Volume": 0.05,     
#     "P/B Ratio": 0.20,  
#     "Revenue Growth": 0.30,      
#     "Profit Margin": 0.10,          
#     "Sector Beta": 0.15              
# }

# tickers_example = ["AAPL", "MSFT", "NVDA"]
# analyzer = StockAnalyzer(tickers_example, aggressive_weights)
# analyzer.fetch_and_score_stocks()
# analyzer.display_results()
# # print(analyzer.results)

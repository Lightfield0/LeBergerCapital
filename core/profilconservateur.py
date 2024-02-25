#profil conservateur 
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
            "Prix des Actions": current_price,
            "Dividendes": info.get("dividendYield", 0) * 100 if info.get("dividendYield") is not None else 0,
            "Ratio Cours/Bénéfice (P/E)": info.get("trailingPE", 0),
            "Volume de Transactions": info.get("averageVolume", 0),
            "Ratio Cours/Valeur Comptable (P/B)": info.get("priceToBook", 0),
            "Croissance des Revenus": info.get("revenueGrowth", 0),
            "Marge Bénéficiaire": info.get("profitMargins", 0),
            "Beta du Secteur": info.get("beta", 0),
            "FiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
            "Dernière Clôture": info.get("regularMarketPreviousClose", 0),
            "Variation sur la Journée": f"{info.get('regularMarketDayLow', 0)} - {info.get('regularMarketDayHigh', 0)}",
            "Plage sur l'Année": f"{info.get('fiftyTwoWeekLow', 0)} - {info.get('fiftyTwoWeekHigh', 0)}",
            "Capitalisation Boursière": info.get("marketCap", 0),
            "Volume Moyen": info.get("averageVolume", 0),
            "Rendement (Dividendes)": f"{info.get('dividendYield', 0) * 100 if info.get('dividendYield') is not None else 0} %",
            "Place Boursière Principale": info.get("exchange", ""),
            "Variation en Pourcentage sur une Journée": f"{percentage_change} %"
        }

    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {ticker}: {e}")
        stock_data = {}  

    return stock_data

def normalize_data_conservative(stock_data):
  normalized_data = {}

  # Prix des Actions
  # Utiliser le ratio du prix actuel au plus haut sur 52 semaines
  max_price = stock_data["FiftyTwoWeekHigh"]
  current_price = stock_data["Prix des Actions"]
  normalized_data["Prix des Actions"] = (current_price / max_price) * 10 if max_price else 0

  # Dividendes
  # Donner une grande importance aux dividendes pour un profil conservateur
  dividend_yield = stock_data["Dividendes"]
  normalized_data["Dividendes"] = dividend_yield * 10

  # Ratio Cours/Bénéfice (P/E)
  # Valoriser les faibles ratios P/E
  pe_ratio = stock_data["Ratio Cours/Bénéfice (P/E)"]
  normalized_data["Ratio Cours/Bénéfice (P/E)"] = (1 / (pe_ratio + 0.01)) * 10 if pe_ratio else 0

  # Volume de Transactions
  # Moins important pour un profil conservateur, mais peut indiquer la liquidité
  average_volume = stock_data["Volume de Transactions"]
  max_volume = stock_data["Volume Moyen"]
  normalized_data["Volume de Transactions"] = (math.log(average_volume + 1) / math.log(max_volume + 1)) * 5 if average_volume else 0

  # Ratio Cours/Valeur Comptable (P/B)
  # Valoriser les faibles ratios P/B
  pb_ratio = stock_data["Ratio Cours/Valeur Comptable (P/B)"]
  normalized_data["Ratio Cours/Valeur Comptable (P/B)"] = (1 / (pb_ratio + 0.01)) * 10 if pb_ratio else 0

  # Croissance des Revenus
  # Moins important pour un profil conservateur
  revenue_growth = stock_data["Croissance des Revenus"]
  normalized_data["Croissance des Revenus"] = revenue_growth * 5

  # Marge Bénéficiaire
  # Important pour la stabilité financière
  profit_margin = stock_data["Marge Bénéficiaire"]
  normalized_data["Marge Bénéficiaire"] = profit_margin * 10

  # Beta du Secteur
  # Préférer un beta faible pour moins de volatilité
  beta = stock_data["Beta du Secteur"]
  normalized_data["Beta du Secteur"] = (1 - beta) * 10 if beta else 10  # Inverser pour valoriser un faible beta

  return normalized_data


def calculate_score(normalized_data, weights):
    score_total = 0
    for key in normalized_data:
        score_total += normalized_data[key] * weights.get(key, 0)
    return score_total

weights_conservateur = {
    "Stock Price": 0.05,  
    "Dividends": 0.25,      
    "P/E Ratio": 0.20,  
    "Transaction Volume": 0.05,     
    "P/B Ratio": 0.10,  
    "Revenue Growth": 0.05,      
    "Profit Margin": 0.10,          
    "Sector Beta": 0.20              
}


def fetch_and_score_stocks(tickers, weights):
  results = {}
  for ticker in tickers:
      stock_data = get_stock_data(ticker)
      normalized_data = normalize_data_conservative(stock_data)  # Mise à jour pour le profil conservateur
      score = calculate_score(normalized_data, weights)
      results[ticker] = {"Score": score, "Data": stock_data}

  sorted_results = dict(sorted(results.items(), key=lambda item: item[1]["Score"], reverse=True))

  return sorted_results



#technologique
tickers_example = ["AAPL", "MSFT", "NVDA"]
#tuketim_urunleri
#tickers_example = ["WMT", "MC.PA", "KO"]
#endustriel
#tickers_example = ["AIR", "SAF.PA", "GE"]

sorted_scores = fetch_and_score_stocks(tickers_example, weights_conservateur)


for rank, (ticker, data) in enumerate(sorted_scores.items(), start=1):
    print(f"{'='*40}")  
    print(f"Classement {rank}: Ticker: {ticker}, Score: {data['Score']}\n")
    for key, value in data["Data"].items():
        print(f"{key}: {value}")
    print("\n")










# profil modere
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

def normalize_data_moderate(stock_data):
    normalized_data = {}
    # Assurez-vous d'importer la bibliothèque math pour la fonction log

    # Prix des Actions
    max_price = stock_data.get("FiftyTwoWeekHigh", 0)
    current_price = stock_data.get("Prix des Actions", 0)
    normalized_data["Prix des Actions"] = (current_price / max_price) * 7.5 if max_price else 0

    # Dividendes
    dividend_yield = stock_data.get("Dividendes", 0)
    normalized_data["Dividendes"] = dividend_yield * 5

    # Ratio Cours/Bénéfice (P/E)
    pe_ratio = stock_data.get("Ratio Cours/Bénéfice (P/E)", 0)
    normalized_data["Ratio Cours/Bénéfice (P/E)"] = (10 - min(pe_ratio, 10)) if pe_ratio else 0

    # Volume de Transactions
    average_volume = stock_data.get("Volume de Transactions", 0)
    max_volume = stock_data.get("Volume Moyen", 0)
    normalized_data["Volume de Transactions"] = (math.log(average_volume + 1) / math.log(max_volume + 1)) * 7.5 if average_volume and max_volume else 0

    # Ratio Cours/Valeur Comptable (P/B)
    pb_ratio = stock_data.get("Ratio Cours/Valeur Comptable (P/B)", 0)
    normalized_data["Ratio Cours/Valeur Comptable (P/B)"] = min(10, (1 / (pb_ratio + 0.01)) * 10) if pb_ratio else 0

    # Croissance des Revenus
    revenue_growth = stock_data.get("Croissance des Revenus", 0)
    normalized_data["Croissance des Revenus"] = min(15, revenue_growth * 10)

    # Marge Bénéficiaire
    profit_margin = stock_data.get("Marge Bénéficiaire", 0)
    normalized_data["Marge Bénéficiaire"] = profit_margin * 7.5

    # Beta du Secteur
    beta = stock_data.get("Beta du Secteur", 0)
    normalized_data["Beta du Secteur"] = 5 + min(5, (beta * 5)) if beta else 5

    return normalized_data

def calculate_score(normalized_data, weights):
    score_total = 0
    for key in normalized_data:
        score_total += normalized_data[key] * weights.get(key, 0)
    return score_total

weights_agressif = {
    "Prix des Actions": 0.05, 
    "Dividendes": 0.05,  
    "Ratio Cours/Bénéfice (P/E)": 0.10,  
    "Volume de Transactions": 0.05,  
    "Ratio Cours/Valeur Comptable (P/B)": 0.15,  
    "Croissance des Revenus": 0.35,  
    "Marge Bénéficiaire": 0.10,  
    "Beta du Secteur": 0.15  
}

def fetch_and_score_stocks(tickers, weights):
    results = {}
    for ticker in tickers:
        stock_data = get_stock_data(ticker)
        normalized_data = normalize_data_moderate(stock_data)  # Utilisez la version modérée pour la normalisation
        score = calculate_score(normalized_data, weights)
        results[ticker] = {"Score": score, "Data": stock_data}

    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]["Score"], reverse=True))
    return sorted_results

# Exemple d'utilisation
tickers_example = ["AAPL", "MSFT", "NVDA"]
sorted_scores = fetch_and_score_stocks(tickers_example, weights_agressif)

for rank, (ticker, data) in enumerate(sorted_scores.items(), start=1):
    print(f"{'='*40}")  
    print(f"Classement {rank}: Ticker: {ticker}, Score: {data['Score']}\n")
    for key, value in data["Data"].items():
        print(f"{key}: {value}")
    print("\n")
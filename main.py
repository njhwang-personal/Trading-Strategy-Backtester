from data import fetch_data
from strategy import trading_strategy
from simulate import simulation
from pathlib import Path
import json

def main():
    ticker = "NVDA"
    years = 5
    df = fetch_data(ticker, years)
    df = trading_strategy(df, 1)
    df, final_portfolio, metrics = simulation(df, years)
    
    Path("artifacts").mkdir(exist_ok=True)      # creates directory for outputs
    df.to_csv("artifacts/Portfolio.csv", index=True)
    with open("artifacts/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    

if __name__ == "__main__":
    main()
from typing import Tuple, Dict
import pandas as pd
import numpy as np

def simulation(df: pd.DataFrame, years: int )-> Tuple[pd.DataFrame, float, Dict[str, float]]:

    #start with x amount of money invested
    #whenever Action says 1, buy
    #whenever Action says -1, sell
    #reinvest whatever capital we have when we buy again
    #measure the difference from when we buy between when we sell (closing price)

     
    # Take a look at trade freq, what hits, what misses
    # look at clusters. Why are these trades happening????? - good for FPGA
    if "Close" not in df.columns:
        raise ValueError("simulation expects a 'Close' column")
    if "ExecAction" not in df.columns:
        raise ValueError("simulation expects an 'ExecAction' column (-1/0/+1)")
    init_capital = 1000.0
    capital = init_capital
    shares_held = 0.0
    df['Portfolio'] = capital
    df['Shares'] = shares_held
    df['Max Drawdown Amount'] = 0.0
    df['Max Drawdown Percent'] = 0.0
    

    for i in range(1, len(df)):
        action = int(df['ExecAction'].iat[i])
        prices = df['Close'].iloc[i]
        price = float(prices.iloc[0])
        
        if action == 1 and capital > 0.0 and shares_held == 0.0:
            shares_held = capital/price
            capital = 0.0
            
        elif action == -1 and shares_held > 0.0:
            capital = shares_held * price
            shares_held = 0.0

        df.at[df.index[i], 'Shares'] = shares_held
        if shares_held > 0.0:
            df.at[df.index[i], 'Portfolio'] = shares_held * price
        else:
            df.at[df.index[i], 'Portfolio'] = capital

############################ MEASURES ##############################################


        # CAPR (Compound Annual Growth Rate) = ((Final Portfolio Value / Initial Capital)^(1/years) - 1)
        # goal = 15-25%

        # Max Drawdown = rolling max((Peak Portfolio Value - Trough Portfolio Value)/Peak Portfolio Value) 
        # (largest drop from peak to trough before new high is reached)
        # goal = <25%

        # Sharpe Ratio = (Average Portfolio Return - Risk Free Rate)/Standard Deviation of Returns
        # A measure of risk-adjusted return. It shows how much excess return you're getting per unit of risk (volatility)
        # High returns are only good if they’re consistent and not super volatile. Sharpe Ratio balances that.
        # Higher = better. Want >2, >1 is fine
        # penalizes overall volatily

        # Sortino Ratio = (Average Portfolio Return - Risk Free Rate)/Standard Deviation of NEGATIVE Returns
        # Assesses how much return an investment generates for each unit of bad risk taken. 
        # A higher Sortino ratio indicates a better return for the amount of downside risk. 
        # Higher Sortino Ratio = better risk-adjusted returns
        # want >1 ideally
        # penalizes only downside volatility

        # Calmar Ratio = (CAGR / |Max Drawdown|)
        # Measures return relative to drawdown risk
        # ideally > 1.0-3.0
        # High Calmar Ratio = The strategy delivers strong returns with relatively small worst-case losses.
        # Low Calmar Ratio = Returns aren’t high enough to justify the amount of drawdown risk taken.

        # Profit factor = (Gross Profit / |Gross Loss|)
        # Measures the ratio of total gains to total losses over a period.
        # <1 = unprofitable
        # > 1.5-2 is ideal

        # Win rate = (# of winning trades / total num of trades) * 100

        # Expectancy = (Win rate * avg PnL of winning trades) - (loss rate * avg loss amount)
        # How much you can expect to make or lose per trade on average if you keep trading the same way.
        # >0 = profitable, you expect to make more money over time
        # <0 = losing, expect to lose money over time
        # if expectancy = 60, you expect to make $60 per trade

    ########## Max Drawdown ############################
    rolling = df['Portfolio'].cummax() #rolling max
    df['Max Drawdown Amount'] = ((df['Portfolio'] - rolling))
    df['Max Drawdown Percent'] = ((df['Portfolio'])/rolling-1.0)
    max_drawdown_amt = df['Max Drawdown Amount'].min()
    max_drawdown_pct = df['Max Drawdown Percent'].min()


    ######## Sharpe and Sortino Ratios #################
    df["Daily Return"] = 0.0
    risk_fr = 0
    df["Daily Return"] = df['Portfolio'].pct_change( )#period = day, can change later
    dev = df["Daily Return"].std()
    if(dev == 0 or pd.isna(dev)):
        sharpe = np.nan
    else:
        sharpe = ((df["Daily Return"].mean() - risk_fr)/dev) * (252**(1/2)) #annualize (252 trading days in a year)


    downside_returns = df.loc[df["Daily Return"] < 0, "Daily Return"]
    dev_sort = downside_returns.std()
    if(dev_sort != 0):
        sortino = ((df["Daily Return"].mean() - risk_fr)/dev_sort) * (252**(1/2))
    else:
        sortino = float("inf")

    ######### Profit Factor #############   
    trades = df.loc[(df["ExecAction"] == 1.0) | (df["ExecAction"] == -1.0), "Portfolio"]

    if len(trades) %2 != 0:
         trades = pd.concat([trades, pd.Series([df["Portfolio"].iloc[-1]])], ignore_index=True)
    
    evens = 0
    odds = 1
    gross_profit = 0.0
    gross_loss = 0.0
    wins = []
    losses = []
    while evens < len(trades) and odds < len(trades):
        pnl = trades.iloc[odds] - trades.iloc[evens]
        if(pnl > 0.0):
            gross_profit += pnl
            wins.append(pnl)
        elif pnl < 0.0:
            gross_loss += pnl
            losses.append(pnl)
        odds +=2
        evens +=2

    profit_factor = (gross_profit / np.abs(gross_loss)) if gross_loss != 0 else float("inf")

    ######## Win rate and Expectancy ##########
    tot_trades = len(trades)/2
    win_rate = (len(wins) / tot_trades) if tot_trades > 0 else np.nan
    loss_rate = (len(losses) / tot_trades) if tot_trades > 0 else np.nan
    avg_win  = (sum(wins)   / len(wins))   if wins   else 0.0
    avg_loss = abs((sum(losses) / len(losses))) if losses else 0.0
    expectancy = (win_rate*avg_win) - (loss_rate*avg_loss)


    ############ CAGR, Final Portfolio, and Calmer Ratio ###############
    final_portfolio = shares_held * df['Close'].iloc[-1] if shares_held > 0.0 else capital
    cagr = ((final_portfolio / init_capital)**(1/years)-1)
    if hasattr(cagr, "size") and cagr.size == 1:
        cagr = float(cagr.squeeze())
    if hasattr(final_portfolio, "size") and final_portfolio.size == 1:
       final_portfolio = final_portfolio.squeeze()


    calmar = (cagr / np.abs(max_drawdown_pct)) if max_drawdown_pct < 0 else float("inf")


    ############ Metrics ####################

    metrics = {
        "Final Portfolio": final_portfolio,
        "CAGR": float(cagr*100),
        "Max Drawdown Amount": float(max_drawdown_amt),
        "Max Drawdown Percent": float(max_drawdown_pct*100),
        "Sharpe": float(sharpe),
        "Sortino": float(sortino),
        "Calmar": float(calmar),
        "Profit Factor": float(profit_factor),
        "Win Rate": float(win_rate*100),
        "Expectancy": float(expectancy),
        "Trades": float(tot_trades),


    }

    ########### Print #############
    for k, v in metrics.items():
        print(f"{k}: {v}")

    #include table that lays these out all nicely?
        
    return df, final_portfolio, metrics


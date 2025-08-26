from dataclasses import dataclass, field
from typing import Callable, Dict, Any
import numpy as np
import pandas as pd

    #########################
    # To do (8/15/2025):    #
    # - parametrize         #
    # - add tests           #
    # - more strategies     #
    # - github              #
    #########################



    ############ SMA Crossover ######################
    # used for long-term trend filtering
    # 50 and 200 day windows

def sma_crossover(data: pd.DataFrame, fast: int = 50, slow: int = 200) -> pd.DataFrame:
    if "Close" not in data.columns:
        raise ValueError("'Close' column not found")
    if fast >= slow:
        raise ValueError("sma_crossover: fast must be < slow")
    data['SMA_50'] = data['Close'].rolling(window=fast, min_periods = fast).mean()
    data['SMA_200'] = data['Close'].rolling(window = slow, min_periods = slow).mean()
    data['Signal_SMA'] = 0
    data.loc[data['SMA_50'] > data['SMA_200'], 'Signal_SMA'] = 1            #Finds golden crosses
    data['Action'] = data['Signal_SMA'].diff()                             #Defines action
    data['ExecAction'] = data['Action'].shift(1).fillna(0).astype(int)

    return data


    ############ RSI Mean Reversion - no trend indication #########################
    # use relative strength index to detect overbought or oversold conditions
    # wilder's smoothing to make numbers less jumpy
    # buy when RSI is oversold RSI < 30, sell when overbought RSI > 70
def rsi_no_trend(data: pd.DataFrame, period: int = 14, buy_thresh: float = 30.0, sell_thresh: float = 70.0)-> pd.DataFrame:
    if "Close" not in data.columns:
        raise ValueError("'Close' column not found")
    data['Price Change'] = data['Close'].diff()
    data['Gain'] = data['Price Change'].clip(lower=0)
    data['Loss'] = -data['Price Change'].clip(upper=0)
    alpha = 1.0 / period
    data['Avg Gain'] = data['Gain'].ewm(alpha=alpha, adjust=False, min_periods=period).mean()     #wilders smoothing
    data['Avg Loss'] = data['Loss'].ewm(alpha=alpha, adjust=False, min_periods=period).mean()
    data['Relative Strength (RS)'] = data['Avg Gain'] / data['Avg Loss'].replace(0, np.nan)
    data['RSI'] = 100 - (100/(1+data['Relative Strength (RS)']))
    buy_cross  = (data['RSI'].shift(1) >= buy_thresh) & (data['RSI'] < buy_thresh)
    sell_cross = (data['RSI'].shift(1) <= sell_thresh) & (data['RSI'] > sell_thresh)
    
    data['Action_RSI'] = 0.0
    holding = False   # State tracking
    for i in range(len(data)):
        if not holding and bool(buy_cross.iloc[i]):
            data.iloc[i, data.columns.get_loc('Action_RSI')] = 1  # Buy
            holding = True
        elif holding and bool(sell_cross.iloc[i]):
            data.iloc[i, data.columns.get_loc('Action_RSI')] = -1 # Sell
            holding = False
    
    data['ExecAction'] = data['Action_RSI'].shift(1).fillna(0).astype(int)

    return data

    ############ Exponential Moving Averages (EMA) crossover #########
    # used for short-term, fast-reacting strategies (day trading, momentum)
    # gives more weight to recent prices os it reacts faster to new changes
    # EMA = Price(t) * alpha + EMA(t-1) * (1-alpha), alpha = how much weight today's prices get
    # Buy/Hold when shortterm goes above longterm
    # 12 day and 26 day windows

def ema_crossover(data: pd.DataFrame, fast: int = 12, slow: int = 26):
    if "Close" not in data.columns:
        raise ValueError("'Close' column not found")
    if fast >= slow:
        raise ValueError("ema_crossover: fast must be < slow")
    data['EMA_12'] = data['Close'].ewm(span = fast, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span = slow, adjust=False).mean()
    data['Signal_EMA'] = 0
    data.loc[data['EMA_12'] > data['EMA_26'], 'Signal_EMA'] = 1
    data['Action'] = data['Signal_EMA'].diff()
    data['ExecAction'] = data['Action'].shift(1).fillna(0).astype(int)
    return data

    ############ Bollinger Band Breakout ####################


    ############ Momentum / Rate of Change ##################


    ############ Moving Average Convergence Divergence ######

    ############ Volatility Stop / ATR-based Trailing Stop ##

@dataclass
class StrategySpec:
    name: str
    builder: Callable[..., pd.DataFrame]
    defaults: Dict[str, Any] = field(default_factory=dict)

STRATEGIES: Dict[int, StrategySpec] = {
    
    1: StrategySpec("SMA Crossover", builder = sma_crossover,
                    defaults = {"fast": 50, "slow": 200}),
    2: StrategySpec("RSI Mean Reversion", builder = rsi_no_trend,
                    defaults = {"period": 14, "buy_thresh": 30.0, "sell_thresh": 70.0}),
    3: StrategySpec("EMA Crossover", builder = ema_crossover,
                    defaults = {"fast": 12, "slow": 26})

    # Add more here later: 3=Bollinger, 4=MACD, 5=ATR stop, etc.
}



def build_exec_actions(df: pd.DataFrame, strategy_code: int, **overrides) -> tuple[pd.Series, pd.DataFrame]:
    """Run the selected strategy builder and return a clean ExecAction Series."""
    if strategy_code not in STRATEGIES:
        raise ValueError(f"Unknown strategy_code={strategy_code}. Options: {list(STRATEGIES.keys())}")

    spec = STRATEGIES[strategy_code]
    params = {**spec.defaults, **overrides}
    out = spec.builder(df.copy(), **params)

    if 'ExecAction' not in out.columns:
        raise ValueError(
            f"Strategy '{spec.name}' did not produce 'ExecAction'. "
            f"Ensure the builder returns a DataFrame with that column."
        )

    exec_series = out['ExecAction'].astype(int).rename('ExecAction')
    extras = out.drop(columns=['ExecAction'])
    return exec_series,extras

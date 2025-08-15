# Start off with SMA crossover 50, 200, golden cross
# expand from there

# Next:
# 1. EMA crossover
# 2. RSI-based trading
# 3. Bollinger Bands
# 4. Mean reversion
import pandas as pd
from strategies import build_exec_actions, STRATEGIES



def trading_strategy(data: pd.DataFrame, strategy_code: int = 1, **overrides) -> pd.DataFrame:
    exec_actions, extras = build_exec_actions(data, strategy_code, **overrides)
    if "Close" in extras.columns:
        extras = extras.drop(columns=["Close"])
    elif isinstance(extras.columns, pd.MultiIndex):
        extras = extras.drop(columns=[col for col in extras.columns if col[0] == "Close"])

    out = data[['Close']].join(extras, how = 'left')
    out['ExecAction'] = exec_actions.astype(int)
    out.attrs['strategy'] = {
        "code": strategy_code,
        "name": STRATEGIES[strategy_code].name,
        "params": {**STRATEGIES[strategy_code].defaults, **overrides}
    }
    return out


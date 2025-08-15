# Trading Strategy Backtester Personal Project

A Python backtesting engine for evaluating trading strategies with historical market data

## Current Features:

 - **Strategies**:  
    - SMA Crossover (50/200 day windows)
    - RSI Mean Reversion - no trend filter (14-day, 30/70 thresholds)
 - **Performance Metrics**:
    - CAGR, Sharpe, Sortino, Calmar Ratio
    - Max Drawdown (amount & percent)
    - Profit Factor, Win Rate, Expectancy
- **Clean, Modular Architecture**:
    - Easy to add new strategies
    - Separate data fetching, signal generation, and simulation logic
- **Result Outputs**:
    - `artifacts/Portfolio.csv` — daily portfolio values
    - `artifacts/metrics.json` — summary performance stats


## In the Future:

- **Strategies**:  
    - RSI Mean Reversion with trend filter
    - Exponential Moving Averages (EMA) crossover
    - Bollinger Band Breakout
    - Momentum / Rate of Change
    - Moving Average Convergence Divergence
    - Volatility Stop / ATR-based Trailing Stop
- **Technical Enhancements** 
    - API Development Integration (Python + Node.js) – Connect to real-time market data and broker APIs for live strategy testing and execution.
    - RAG Pipeline - Embed and store historical backtest results and strategy notes in a vector database for semantic search and AI strategy retrieval and recommendation
    - AI/ML (TensorFlow/Pytorch) - Experiment with predictive models for trade signal generation, portfolio optimization, and risk management
    - JSON Data Handling - Standardize input/output formats for interoperability with APIs, dashboards, and analytic tools
    - Cloud Deployment (AWS/Azure/GCP) - Leverage cloud storage for historical data and cloud compute for parallel backtests
    - Frontend visualization dashboard (React + Javascript) - selecting strategies, run backtests, visualize equity curves, trades, and performance metrics

## Requirements
Install dependencies:
```bash
pip install -r requirements.txt
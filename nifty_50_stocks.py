# -*- coding: utf-8 -*-
"""nifty_50 stocks.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FFqtvuZ8mSC4o6i0x3JSRx3cowIvpxZu
"""



!pip install  yfinance

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Define the Stock class
class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.historical_data = self.download_historical_data()

    def download_historical_data(self):
        # Download historical stock data from Yahoo Finance
        data = yf.download(self.symbol, start="2019-01-01", end="2021-01-01")
        return data

    def cur_price(self, cur_date):
        # Get the closing price of the stock on the specified date
        return self.historical_data.loc[cur_date]['Close']

    def n_day_ret(self, n, cur_date):
        # Calculate the N-day returns as on the specified date
        return (self.cur_price(cur_date) / self.historical_data.loc[cur_date - pd.DateOffset(days=n)]['Close']) - 1

    def daily_ret(self, cur_date):
        # Calculate the daily returns on the specified date
        return (self.cur_price(cur_date) / self.historical_data.loc[cur_date - pd.DateOffset(days=1)]['Close']) - 1

    def last_30_days_price(self, cur_date):
        # Get an array of last 30 days prices
        return self.historical_data.loc[cur_date - pd.DateOffset(days=30):cur_date]['Close'].values

    def volatility(self):
        # Calculate the volatility of the stock
        return np.sqrt(252) * np.std(self.historical_data['Close'].pct_change().dropna()) * 100

    def sharpe_ratio(self):
        # Calculate the Sharpe ratio of the stock
        mean_return = np.mean(self.historical_data['Close'].pct_change().dropna())
        return np.sqrt(252) * mean_return / self.volatility()

# Define the active stock selection strategy
def active_stock_selection_strategy(start_date, end_date, num_days, initial_equity):
    # Define the list of Nifty50 stocks
    nifty50_stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'HINDUNILVR', 'HDFC', 'INFY', 'KOTAKBANK', 'ICICIBANK', 'BAJFINANCE', 'ITC', 'LT', 'AXISBANK', 'ASIANPAINT', 'M&M', 'MARUTI', 'NTPC', 'SUNPHARMA', 'ONGC', 'BHARTIARTL', 'TITAN', 'NESTLEIND', 'POWERGRID', 'ULTRACEMCO', 'HEROMOTOCO', 'WIPRO', 'COALINDIA', 'IOC', 'SBIN', 'TECHM', 'BAJAJ-AUTO', 'INDUSINDBK', 'GRASIM', 'DRREDDY', 'NEOGEN', 'HCLTECH', 'CIPLA', 'SHREECEM', 'JSWSTEEL', 'BRITANNIA', 'BPCL', 'GAIL', 'DIVISLAB', 'EICHERMOT', 'ADANIPORTS', 'HINDALCO', 'UPL', 'TATAMOTORS', 'SBILIFE', 'BAJAJFINSV', 'HDFCLIFE', 'TATASTEEL', 'ONGC']

    # Initialize the portfolio with equal weights for each stock
    portfolio = {stock: initial_equity / len(nifty50_stocks) for stock in nifty50_stocks}

    # Loop through each month and select stocks with positive returns
    cur_date = start_date
    while cur_date <= end_date:
        # Get the 30-day returns for each stock
        returns = {stock: Stock(stock).n_day_ret(num_days, cur_date) for stock in nifty50_stocks}

        # Select stocks with positive returns
        selected_stocks = [stock for stock in nifty50_stocks if returns[stock] > 0]

        # Update the portfolio with the selected stocks
        portfolio = {stock: portfolio[stock] if stock in selected_stocks else 0 for stock in nifty50_stocks}

        # Rebalance the portfolio
        total_value = sum(portfolio.values())
        portfolio = {stock: (portfolio[stock] / total_value) * initial_equity for stock in nifty50_stocks}

        # Move to the next month
        cur_date += pd.DateOffset(months=1)

    # Calculate the performance metrics for the portfolio
    nifty50_index = yf.download('^NSEI', start=start_date, end=end_date)
    nifty50_return = (nifty50_index.loc[end_date]['Close'] / nifty50_index.loc[start_date]['Close']) - 1
    benchmark_allocation = {stock: initial_equity / len(nifty50_stocks) for stock in nifty50_stocks}
    benchmark_return = sum([Stock(stock).daily_ret(end_date) * benchmark_allocation[stock] for stock in nifty50_stocks])
    sample_strategy_return = sum([Stock(stock).daily_ret(end_date) * portfolio[stock] for stock in nifty50_stocks])
    cagr = ((sample_strategy_return / initial_equity) ** (1 / (num_days / 365))) - 1
    volatility = np.sqrt(252) * np.std(nifty50_index['Close'].pct_change().dropna()) * 100
    sharpe_ratio = np.sqrt(252) * (sample_strategy_return / initial_equity - nifty50_return) / volatility

    # Return the performance metrics
    return {
        'nifty50_return': nifty50_return,
        'benchmark_return': benchmark_return,
        'sample_strategy_return': sample_strategy_return,
        'cagr': cagr,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'portfolio': portfolio
    }

# Define the Streamlit app
def app():
    # Set the app title and description
    st.set_page_config(page_title='Nifty50 Portfolio', page_icon=':money_with_wings:', layout='wide')
    st.title('Nifty50 Portfolio')
    st.write('This app allows you to create an active stock selection strategy for the Nifty50 index and compare its performance with a benchmark.')

    # Get the user inputs
    start_date = st.date_input('Simulation Start Date', value=pd.to_datetime('2019-01-01'))
    end_date = st.date_input('Simulation End Date', value=pd.to_datetime('2021-01-01'))
    num_days = st.slider('Number of Days for Stock Selection', min_value=1, max_value=30, value=30)
    initial_equity = st.number_input('Initial Equity', value=1000000)

    # Run the active stock selection strategy and display the results
    if st.button('Run Simulation'):
        results = active_stock_selection_strategy(start_date, end_date, num_days, initial_equity)
        st.write('### Portfolio Allocation')
        st.write(pd.DataFrame.from_dict(results['portfolio'], orient='index', columns=['Allocation']))
        st.write('### Performance Metrics')
        st.write(f"CAGR: {results['cagr']:.2%}")
        st.write(f"Volatility: {results['volatility']:.2%}")
        st.write(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        st.write(f"Nifty50 Return: {results['nifty50_return']:.2%}")
        st.write(f"Benchmark Return: {results['benchmark_return']:.2%}")
        st.write(f"Sample Strategy Return: {results['sample_strategy_return']:.2%}")

# Run the Streamlit app
if __name__ == '__main__':
    app()

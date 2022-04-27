#pip install pandas
#pip install matplotlib
#pip install pandas-datareader
#pip install yfinance

import pandas as pd 
import pandas_datareader as pdr
from matplotlib import pyplot as plt
import yfinance as yf

from matplotlib import rcParams
tickers = ['MSFT', 'AAPL', 'NFLX']

data = pdr.get_data_yahoo(tickers,start = '2018-01-01')['Close']
rcParams['figure.figsize'] = 12,6
plt.plot(data)
plt.grid(True)
plt.title('2018-present')
plt.legend(tickers)
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

print(get_current_price('MSFT'))
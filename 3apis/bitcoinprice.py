#pip install numpy
#pip install pandas
#pip install matplotlib
##pip install yfinance

import numpy as np
import pandas as pd

import yfinance as yf
from matplotlib import pyplot as plt

from matplotlib import rcParams

# Get Bitcoin data
data = yf.download(tickers='BTC-USD', period = '10d', interval = '1d')
data.reset_index(inplace = True)
data = data.drop(['Open', 'High', 'Low','Adj Close', 'Volume'], axis=1)
rcParams['figure.figsize'] = 12,6
plt.plot(data['Date'],data['Close'])
plt.grid(True)
plt.title('BTC prices Last 10 days')
plt.legend('BTC-USD')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

BTC = yf.Ticker("BTC-USD")
price = BTC.info['regularMarketPrice']
print(price)
 
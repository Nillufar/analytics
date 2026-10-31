"""Loading Data"""
"""
Data does not appear in a clean table ready for analysis.
Analysts need to collect, load, and prepare data before 
any modeling or decision-making can take place.

Financial data is typically messy, incomplete, 
and stored in many different formats.

We will focus on three common ways to load data:
    - CSV files
    - Excel files
    - API

An API (Application Programming Interface) is a set of rules 
that allow one software to communicate with another. Is a way
for one computer program to request data from another computer
program over the internet. This allows us to automate the data
collection process. 
"""
# pip install pytickersymbols
#pip install yfinance

from pytickersymbols import PyTickerSymbols
import yfinance as yf
import pandas as pd


""" Loading from a CSV """
ff_data = pd.read_csv("ff_factors.csv")

#check data
#ff_data.head()
#ff_data.tail()
#ff_data.shape
#ff_data.columns
#ff_data.dtypes
#ff_data.index.dtype
#ff_data.index.name
#ff_data.isna().sum()
#ff_data.describe()

#Common loading alternatives
#ff_data_2 = pd.read_csv("ff_factors.csv", header=None)
#ff_data_3 = pd.read_csv("ff_factors.csv", names = ["these", "are", "my", "custom", "column","names" ,"for","headers"])
#ff_data4 = pd.read_csv("ff_factors.csv",index_col="date")
# na_values=["NULL"]



#setting index

ff_data = ff_data.set_index("date")
#ff_data = ff_data.rename(columns={"original": "new"})
ff_data.index.name = "Date"
ff_data.index.dtype
ff_data.index = pd.to_datetime(ff_data.index, format="%Y%m%d")




"""Loading data from Excel"""


Vol_index = pd.read_excel("Vol_index.xlsx")
Vol_index = pd.read_excel("Vol_index.xlsx",sheet_name="Vol_index")
Vol_index = Vol_index.set_index("Date")
Vol_index.index.dtype



df = pd.read_excel("Vol_index.xlsx",sheet_name="Sheet1",usecols="G:G",skiprows=7,nrows=4)
df = pd.read_excel("Vol_index.xlsx",sheet_name="Sheet1",usecols="G:G",skiprows=7,nrows=4,header=None)


#Large dataset
Fund_data = pd.read_csv("Fund_data.csv")
Fund_data.head()
Fund_data.tail()
cols = Fund_data.columns 
Fund_data["datadate"].dtype
Fund_data["datadate"].head(10)
Fund_data["datadate"] = pd.to_datetime(Fund_data["datadate"],format="%d/%m/%Y")
Fund_data = Fund_data.rename(columns={"datadate": "Date"})
Fund_data["Date"].head(10)
Fund_data.dtypes.head(20)
#initial screening

Fund_data = Fund_data.sort_values(["gvkey", "Date"])
Fund_data[["gvkey", "Date"]].isna().sum()
Fund_data.duplicated(subset=["gvkey", "Date"]).sum()

"""Loading data from API"""

stock_data = PyTickerSymbols()

sp500_stocks = stock_data.get_stocks_by_index('S&P 500')
nasdaq_stocks = stock_data.get_stocks_by_index('NASDAQ 100')
dow_stocks = stock_data.get_stocks_by_index('DOW JONES')

sp500_tickers = [stock['symbol'] for stock in sp500_stocks]

#Downloading data
start_date = "2020-01-01"
prices = yf.download(sp500_tickers, start="2020-01-01", auto_adjust=False)
adj_close_prices = prices['Adj Close']
adj_close_prices.index.dtype
adj_close_prices.dtypes
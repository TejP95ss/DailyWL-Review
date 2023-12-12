import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta 
from colorama import Fore
import requests
from bs4 import BeautifulSoup

url = "https://companiesmarketcap.com"
page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')

table = soup.find('table')
body = table.find('tbody')
all_ticker_divs = body.find_all("div", class_= "company-code")
market_caps = table.find_all('td', class_ = "td-right")

Tickers = [word.text for word in all_ticker_divs]
Market_Caps = [word.text for word in market_caps]
Market_Caps = Market_Caps[1:]
Corrected_Market_Caps = []

for x in Market_Caps:
    if x[-1:].isalpha() == True:
        if x[-1:] == "T":
            string = x[:-2]
            newstring = string[1:]
            value =  1000 * float(newstring)
            Corrected_Market_Caps.append(value)
        else: 
            string = x[:-2]
            newstring = string[1:]
            value = float(newstring)
            Corrected_Market_Caps.append(value)
    else: continue
remove_sa = Tickers.index('2222.SR')
del Tickers[remove_sa], Corrected_Market_Caps[remove_sa]

enddate = datetime.now() + timedelta(days=1)
startdate = enddate - timedelta(days=10)
endstringdate = enddate.strftime("%Y-%m-%d")
startstringdate = startdate.strftime("%Y-%m-%d")
table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
symbol_column = table[0]["Symbol"]
updated_symbol_column = symbol_column.replace(["BRK.B", "BF.B"], ["BRK-B", "BF-B"])
prices = yf.download(updated_symbol_column.tolist(), start = startstringdate, end = endstringdate)
reversedprices = prices["Adj Close"][::-1]
swapped = reversedprices.transpose()
swapped.columns.name = "Tickers"
daychanges = [round((((reversedprices.iloc[0, x]/reversedprices.iloc[1, x]) - 1)*100), 3) for x in range(503)]
swapped["1D Percent Changes"] = daychanges
day_change_sorted = swapped.sort_values(by=['1D Percent Changes'])

def top_gainers_and_losers(df):
    print(f"Stats for {(df.columns.values[0].date())}-{df.columns.values[0].strftime('%A')} \n")
    for x in range(10):
        print(Fore.RED + f"{df.index[x]}: {df.iloc[x, df.shape[1] - 1]}")
    print("\n")
    for x in range(10):
        print(Fore.GREEN + f"{df.index[df.shape[0] - 1 - x]}: {df.iloc[df.shape[0] - 1 - x, df.shape[1] - 1]}")
    print(Fore.WHITE + "\n")


def top_market_cap(df):
    for x in range(10):
        list_all_tickers = df.index.values.tolist()
        index = list_all_tickers.index(Tickers[x])
        if df.iloc[index, df.shape[1] - 1] >= 0:
            print(Fore.GREEN + f"{Tickers[x]}: {df.iloc[index, df.shape[1] - 1]}")
        else: print(Fore.RED + f"{Tickers[x]}: {df.iloc[index, df.shape[1] - 1]}")

    print(Fore.WHITE + "\n")

top_gainers_and_losers(day_change_sorted)
top_market_cap(day_change_sorted)

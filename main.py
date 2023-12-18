import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta 
from colorama import Fore
import requests
from bs4 import BeautifulSoup
import squarify 
import matplotlib
import numpy as np

url = "https://companiesmarketcap.com/usa/largest-companies-in-the-usa-by-market-cap/"
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
    print(Fore.BLUE + "Top 10 Losers")
    print(Fore.WHITE)
    for x in range(10):
        print(Fore.RED + f"{x+1}: {df.index[x]}: {df.iloc[x, df.shape[1] - 1]}")
    print(Fore.BLUE + "\n")
    print("Top 10 Gainers")
    print(Fore.WHITE)
    for x in range(10):
        print(Fore.GREEN + f"{x+1}: {df.index[df.shape[0] - 1 - x]}: {df.iloc[df.shape[0] - 1 - x, df.shape[1] - 1]}")
    print(Fore.WHITE + "\n")


def top_market_cap(df):
    number_of_companies = 50
    Plot_MCap = Corrected_Market_Caps[:number_of_companies]
    Plot_Names = Tickers[:number_of_companies]
    List_Of_PCDaily = [df.iloc[df.index.values.tolist().index(Tickers[j]), df.shape[1] - 1] for j in range(number_of_companies)]
    labels = [f"{Plot_Names[x]}\n {List_Of_PCDaily[x]}%" for x in range(number_of_companies)]
    bold, end = "\033[1m", "\033[0m"
    Colors = []
    for x in List_Of_PCDaily:
        if x < -1.5: Colors.append("#FF0000")
        elif -1.5 <= x < -.75: Colors.append("#FF2400")
        elif -.75 <= x < 0: Colors.append("#F88379")
        elif x == 0: Colors.append("#FFFFFF")
        elif 0 < x <= .75: Colors.append("#98FB98")
        elif .75 < x <= 1.5: Colors.append("#0BDA51")
        else: Colors.append("#00FF00")
    print(Fore.BLUE + f"Top {number_of_companies} Market Cap Companies")
    print(Fore.WHITE)
    for x in range(number_of_companies):
        list_all_tickers = df.index.values.tolist()
        index = list_all_tickers.index(Tickers[x])
        if df.iloc[index, df.shape[1] - 1] >= 0:
            if abs(df.iloc[index, df.shape[1] - 1]) >= 1:
                print(bold + Fore.GREEN + f"{x + 1}: {Tickers[x]}: {df.iloc[index, df.shape[1] - 1]}" + Fore.WHITE + end)    
            else: print(Fore.GREEN + f"{x + 1}: {Tickers[x]}: {df.iloc[index, df.shape[1] - 1]}" + Fore.WHITE)
        else: 
            if abs(df.iloc[index, df.shape[1] - 1]) >= 1:
                print(bold + Fore.RED + f"{x + 1}: {Tickers[x]}: {df.iloc[index, df.shape[1] - 1]}" + Fore.WHITE + end)
            else: print(Fore.RED + f"{x + 1}: {Tickers[x]}: {df.iloc[index, df.shape[1] - 1]}" + Fore.WHITE)
    squarify.plot(Plot_MCap, label = labels, ec = "black", color = Colors, text_kwargs = {'fontsize': 8, 'color': 'black', 'fontweight': 'bold'})
    matplotlib.pyplot.title(f'SP{number_of_companies} Daily % Changes by Market Cap')
    matplotlib.pyplot.axis("off")
    matplotlib.pyplot.show()

top_gainers_and_losers(day_change_sorted)
top_market_cap(day_change_sorted)

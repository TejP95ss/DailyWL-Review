import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, date 
from colorama import Fore
import requests
from bs4 import BeautifulSoup
import squarify 
import matplotlib

Daily_Percent_Change = []
Corrected_Market_Caps = []
All_Tickers = []

for q in range(7):
    url = f"https://companiesmarketcap.com/usa/largest-companies-in-the-usa-by-market-cap/?page={q+1}/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')

    table = soup.find('table')
    body = table.find('tbody')
    all_ticker_divs = body.find_all("div", class_= "company-code")
    market_caps = table.find_all('td', class_ = "td-right")
    percentages = body.find_all('td', class_ =  "rh-sm")
    percentagesinlist = [word.text for word in percentages]
    redspans = body.find_all('span', class_ = "percentage-red")
    redspansinlist = [word.text for word in redspans]
    greenspans = body.find_all('span', class_ = "percentage-green")
    greenspansinlist = [word.text for word in greenspans]


    Tickers = [word.text for word in all_ticker_divs]
    All_Tickers = All_Tickers + Tickers
    Market_Caps = [word.text for word in market_caps]
    DailyPercents = []
    Market_Caps = Market_Caps[1:]
    for x in percentages:
        spanclass = x.find('span', class_ = "percentage-green")
        if spanclass == None:
            spanclass = x.find('span', class_ = "percentage-red")
            stringpercent = spanclass.text
            strippedpercent = stringpercent[0:len(stringpercent)-1]
            numberpercent = float(strippedpercent) * -1
            Daily_Percent_Change.append(numberpercent)
        else: 
            stringpercent = spanclass.text
            strippedpercent = stringpercent[0:len(stringpercent)-1]
            numberpercent = float(strippedpercent)
            Daily_Percent_Change.append(numberpercent)

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
startdate = enddate - timedelta(days=5)
endstringdate = enddate.strftime("%Y-%m-%d")
startstringdate = startdate.strftime("%Y-%m-%d")

Dictionary_For_df = {"Ticker" : All_Tickers, "1D Percent Change" : Daily_Percent_Change, "Market Cap." : Corrected_Market_Caps}
DataFrame = pd.DataFrame(Dictionary_For_df)
DataFrame_Sorted = DataFrame.sort_values(by="1D Percent Change")

def top_gainers_and_losers(df, num):
    print(f"Stats for {date.today()}-{datetime.now().strftime('%A')} \n")
    print(Fore.BLUE + "Top 15 Losers")
    print(Fore.WHITE)
    for x in range(num):
        print(Fore.RED + f"{x+1}: {df.iloc[x, 0]} (Market Cap: ${df.iloc[x, df.shape[1] - 1]} Billion): {df.iloc[x, df.shape[1] - 2]} %")
    print(Fore.BLUE + "\n")
    print("Top 15 Gainers")
    reversedf =  df.sort_values(by="1D Percent Change", ascending=False)
    print(Fore.WHITE)
    for x in range(num):
        print(Fore.GREEN + f"{x+1}: {reversedf.iloc[x, 0]} (Market Cap: ${reversedf.iloc[x, df.shape[1] - 1]} Billion): {reversedf.iloc[x, df.shape[1] - 2]} %")
    print(Fore.WHITE + "\n")

def DollarAmountFlows(df, num):
    DollarAmountInOut = [round(Corrected_Market_Caps[x] - (Corrected_Market_Caps[x] / (1 + ((Daily_Percent_Change[x]) / 100))), 2) for x in range(len(Corrected_Market_Caps))]
    df["Dollar Amount In/Out"] = DollarAmountInOut
    Sorted_df = df.sort_values(by="Dollar Amount In/Out", ascending=True)
    print(Fore.BLUE + "\nTop 10 Losers by Dollar Amount(in Billions)")
    print(Fore.WHITE)
    for x in range(num):
        print(Fore.RED + f"{x+1}: {Sorted_df.iloc[x, 0]} (Market Cap: ${Sorted_df.iloc[x, Sorted_df.shape[1] - 2]} Billion): {Sorted_df.iloc[x, Sorted_df.shape[1] - 1]}")
    print(Fore.BLUE + "\n")
    print("Top 10 Gainers by Dollar Amount(in Billions)")
    reversedf =  df.sort_values(by="Dollar Amount In/Out", ascending=False)
    print(Fore.WHITE)
    for x in range(num):
        print(Fore.GREEN + f"{x+1}: {reversedf.iloc[x, 0]} (Market Cap: ${reversedf.iloc[x, reversedf.shape[1] - 2]} Billion): {reversedf.iloc[x, reversedf.shape[1] - 1]}")
    print(Fore.WHITE + "\n")

def top_market_cap():
    number_of_companies = 100
    Plot_MCap = Corrected_Market_Caps[:number_of_companies]
    Plot_Names = All_Tickers[:number_of_companies]
    labels = [f"{x + 1}. {Plot_Names[x]}\n {Daily_Percent_Change[x]}%" for x in range(number_of_companies)]
    Colors = []
    for x in Daily_Percent_Change:
        if x < -1.5: Colors.append("#FF0000")
        elif -1.5 <= x < -.75: Colors.append("#FF4433")
        elif -.75 <= x < 0: Colors.append("#F88379")
        elif x == 0: Colors.append("#FFFFFF")
        elif 0 < x <= .75: Colors.append("#98FB98")
        elif .75 < x <= 1.5: Colors.append("#0BDA51")
        else: Colors.append("#00FF00")
    squarify.plot(Plot_MCap, label = labels, ec = "black", color = Colors, text_kwargs = {'fontsize': 7, 'color': 'black', 'fontweight': 'bold'})
    matplotlib.pyplot.title(f'SP{number_of_companies} Daily % Changes by Market Cap')
    matplotlib.pyplot.axis("off")
    matplotlib.pyplot.show()
    

top_gainers_and_losers(DataFrame_Sorted, 15)
DollarAmountFlows(DataFrame, 15)
top_market_cap()

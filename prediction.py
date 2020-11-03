import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf
from yahoofinancials import YahooFinancials
import plotly.graph_objs as go

import decompose as dc

#Veri Okuma
amazon_df = yf.download('AMZN', start='2017-01-01',progress=False)
amazon_df.index = pd.to_datetime(amazon_df.index)
#print(amazon_df.index)

#Hareketli Ortalama
close_app =amazon_df.iloc[:len(amazon_df)//2,3]
close_app.head()
#print(close_app.head())

rolling_app5 = close_app.rolling(window=5).mean() # rolling inişli çıkış hareketi 5 günlük
rolling_app14 = close_app.rolling(window=14).mean()
rolling_app21 = close_app.rolling(window=21).mean()

MAs = pd.concat([close_app, rolling_app5, rolling_app14, rolling_app21], axis=1)
MAs.columns = ['Close', 'Short', 'Mid', 'Long']
MAs.head()
print(MAs.head())

MAs.dropna(axis=0,inplace=True)
MAs.head(5)
print(MAs.head(5))

#Görselleştirme başlıyor...
fig,ax = plt.subplots(figsize=(12,4))
ax.plot(close_app.index, close_app, label='Amazon')
ax.plot(rolling_app5.index, rolling_app5, label='5 days rolling')
ax.plot(rolling_app14.index, rolling_app14, label='14 days rolling')
ax.plot(rolling_app21.index, rolling_app21, label='21 days rolling')
ax.legend(loc='upper left')
#plt.show()

optimum_length = np.abs(np.percentile(np.array(MAs['Mid']-MAs['Short']),10))
print(optimum_length) #Short ve Mid değerleri arasındaki farklılıkların en küçük %10. değeri bu değer. EN KÜÇÜK UZAKLIK

# Yüksek yükselişlere satış, yüksek düşüşlere alış tavsiyesi
# Percentile Yöntemi
# 5 ile 21 gün arasındaki tüm farklılıkları anlamlandırmak istiyorum.
def buy_sell(data, perc = 50):
    buy_sell = []
    buy_signal = []
    sell_signal = []
    flag = 42

    sm = np.abs(np.percentile(np.array(data["Short"] - data["Mid"]),perc)) # small/mid
    sl = np.abs(np.percentile(np.array(data["Short"] - data["Long"]),perc)) #small/long

    for i in range(0,len(data)):
        if(data["Short"][i] > data["Mid"][i]+sm) & (data["Short"][i] > data["Long"][i]+sl):
            buy_signal.append(np.nan)
            if flag != 1:
                sell_signal.append(data["Close"][i])
                buy_sell.append(data["Close"][i])
                flag = 1
            else:
                sell_signal.append(np.nan)
        elif (data["Short"][i] < data["Mid"][i] - sm) & (data["Short"][i] < data["Long"][i] - sl):
            sell_signal.append(np.nan)
            if flag != 0:
                buy_signal.append(data["Close"][i])
                buy_sell.append(-data["Close"][i])
                flag = 0
            else:
                buy_signal.append(np.nan)

        else:
            buy_sell.append(np.nan)
            sell_signal.append(np.nan)
            buy_signal.append(np.nan)

    operations = np.array(buy_sell)
    operations = operations[~np.isnan(operations)]

    neg = 0 # negatif
    pos = 0 # pozitif

    for i in range(len(operations)):
        if operations[i] < 0:
            neg = i
            break
    for i in range(1,len(operations)):
        if operations[-i > 0]:
            pos = i-1
            break

    operations = operations[neg:-pos]
    PL = np.sum(operations) # kar-zarar
    
    return(buy_signal, sell_signal, PL)

m = buy_sell(MAs)
MAs["BUY"] = m[0]
MAs["SELL"] = m[1]

plt.figure(figsize=(10,5))
plt.scatter(MAs.index, MAs["BUY"], color="green", label="BUY", marker='^', alpha=1)
plt.scatter(MAs.index, MAs["SELL"], color="red", label="SELL", marker='^', alpha=1)
plt.plot(MAs["Close"], label="Close Price", alpha=0.5)
plt.title("Close price buy and sell signals")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.legend(loc ="upper left")
plt.show() 


__author__ = 'qinfeizhang'

# coding:utf-8
import tushare as ts
import talib as ta
import numpy as np
import pandas as pd
import datetime
import sys

start_date = '2016-01-01'
end_date = '2016-11-04'


def get_stock_list():
    df = ts.get_stock_basics()
    return df


def MACD(close, fastperiod=12, slowperiod=26, signalperiod=9):
    datelen = len(close)

    EMASlow = []
    EMAFast = []
    macd = []  # diff
    macdsignal = []  # dea
    macdhist = []  # macd

    for i in range(datelen):
        if i == 0:
            EMASlow.append(close[i])
            EMAFast.append(close[i])
            macd.append(0)
            macdsignal.append(0)
            macdhist.append(0)
        else:
            EMASlow.append(EMASlow[i - 1] * (slowperiod - 1) / (slowperiod + 1) + close[i] * 2 / (slowperiod + 1))
            EMAFast.append(EMAFast[i - 1] * (fastperiod - 1) / (fastperiod + 1) + close[i] * 2 / (fastperiod + 1))
            macd.append(EMAFast[i] - EMASlow[i])
            macdsignal.append(
                macdsignal[i - 1] * (signalperiod - 1) / (signalperiod + 1) + macd[i] * 2 / (signalperiod + 1))

    return macd, macdsignal, macdhist


def Get_TA(df_code):
    operate_array1 = []
    total = len(df_code)

    count = 0
    for code in df_code.index:
        try:
            df = ts.get_hist_data(code, start=start_date, end=end_date).sort_index(axis=0, ascending=True)
            count += 1
            print("processing " + str(count) + " in " + str(total))
            dflen = df.shape[0]
            operate1 = 0

            if dflen > 35:
                (df, operate1) = Get_MACD(df)
        except Exception, e:
            print e
            operate1 = -100

        operate_array1.append(operate1)
    df_code['MACD'] = pd.Series(operate_array1, index=df_code.index)
    return df_code


def Get_MACD(df):
    macd, macdsignal, macdhist = ta.MACD(np.array(df['close']), fastperiod=12, slowperiod=26, signalperiod=9)
    SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
    SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
    SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
    # 13-15 DIFF  DEA  DIFF-DEA
    df['macd'] = pd.Series(macd, index=df.index)  # DIFF
    df['macdsignal'] = pd.Series(macdsignal, index=df.index)  # DEA
    df['macdhist'] = pd.Series(macdhist, index=df.index)  # DIFF-DEA
    dflen = df.shape[0]
    MAlen = len(SignalMA5)
    operate = 0
    if df.iat[(dflen - 1), 13] > 0 and df.iat[(dflen - 1), 14] > 0:
        if df.iat[(dflen - 1), 13] > df.iat[(dflen - 1), 14] and df.iat[(dflen - 2), 13] <= df.iat[(dflen - 2), 14]:
            if df.iat[(dflen - 1), 7] <= df.iat[(dflen - 1), 8] <= df.iat[(dflen - 1), 9]:
                if SignalMA5[MAlen - 1] >= SignalMA10[MAlen - 1] >= SignalMA20[MAlen - 1]:
                    operate = 1

    return (df, operate)


def output_csv(df, dist):
    # today = datetime.date.today()
    # current_day = today.strftime('%Y-%m-%d')
    reload(sys)
    df.to_csv(dist + end_date + 'stock.csv', encoding='utf-8')


# df = get_stock_list()
# Dist = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/result/macd_result/'
# df = Get_TA(df)
# output_csv(df, Dist)

df = ts.get_hist_data('002709', start=start_date, end=end_date).sort_index(axis=0, ascending=True)
macd, macdsignal, macdhist = MACD(np.array(df['close']), fastperiod=12, slowperiod=26, signalperiod=9)
# macd, macdsignal, macdhist = ta.MACD(np.array(df['close']), fastperiod=12, slowperiod=26, signalperiod=9)

df['macd'] = pd.Series(macd, index=df.index)  # DIFF
df['macdsignal'] = pd.Series(macdsignal, index=df.index)  # DEA
df['macdhist'] = pd.Series(macdhist, index=df.index)  # DIFF-DEA
# print df

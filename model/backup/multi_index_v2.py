__author__ = 'qinfeizhang'

# coding:utf-8
import tushare as ts
import talib as ta
import numpy as np
import pandas as pd
import datetime
import sys

start_date = '2016-01-01'
end_date = '2016-10-26'


def get_stock_list():
    df = ts.get_stock_basics()
    return df


def Get_TA(df_code):
    operate_array1 = []
    operate_array2 = []
    operate_array3 = []
    total = len(df_code)

    count = 0
    for code in df_code.index:
        try:
            df = ts.get_hist_data(code, start=start_date, end=end_date).sort_index(axis=0, ascending=True)
            count += 1
            print("processing " + str(count) + " in " + str(total))
            dflen = df.shape[0]
            operate1 = 0
            operate2 = 0
            operate3 = 0
            if dflen > 35:
                (df, operate1) = Get_MACD(df)
                (df, operate2) = Get_KDJ(df)
                (df, operate3) = Get_RSI(df)
        except Exception, e:
            print e
            operate1 = -100
            operate2 = -100
            operate3 = -100
        operate_array1.append(operate1)
        operate_array2.append(operate2)
        operate_array3.append(operate3)

    df_code['MACD'] = pd.Series(operate_array1, index=df_code.index)
    df_code['KDJ'] = pd.Series(operate_array2, index=df_code.index)
    df_code['RSI'] = pd.Series(operate_array3, index=df_code.index)
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


def Get_KDJ(df):
    slowk, slowd = ta.STOCH(np.array(df['high']), np.array(df['low']), np.array(df['close']), fastk_period=9,
                            slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    MA5 = ta.MA(df['close'], timeperiod=5, matype=0)
    MA10 = ta.MA(df['close'], timeperiod=10, matype=0)
    MA20 = ta.MA(df['close'], timeperiod=20, matype=0)

    # 16-17 K,D
    df['slowk'] = pd.Series(slowk, index=df.index)  # K
    df['slowd'] = pd.Series(slowd, index=df.index)  # D
    dflen = df.shape[0]
    operate = 0

    if df.iat[(dflen - 1), 16] > df.iat[(dflen - 1), 17] and df.iat[(dflen - 2), 16] < df.iat[(dflen - 2), 17] and \
                                    df['close'][-1] > MA5[-1] > MA10[-1] > MA20[-1]:
        hole_length = 0
        for i in range(dflen - 2):
            if df.iat[(dflen - 2 - i), 16] < df.iat[(dflen - 2 - i), 17]:
                hole_length += 1
        if hole_length < 5:
            operate += 1

    return (df, operate)


def Get_RSI(df):
    slowreal = ta.RSI(np.array(df['close']), timeperiod=14)
    fastreal = ta.RSI(np.array(df['close']), timeperiod=5)
    slowrealMA5 = ta.MA(slowreal, timeperiod=5, matype=0)
    slowrealMA10 = ta.MA(slowreal, timeperiod=10, matype=0)
    slowrealMA20 = ta.MA(slowreal, timeperiod=20, matype=0)
    fastrealMA5 = ta.MA(fastreal, timeperiod=5, matype=0)
    fastrealMA10 = ta.MA(fastreal, timeperiod=10, matype=0)
    fastrealMA20 = ta.MA(fastreal, timeperiod=20, matype=0)
    df['slowreal'] = pd.Series(slowreal, index=df.index)
    df['fastreal'] = pd.Series(fastreal, index=df.index)
    dflen = df.shape[0]
    MAlen = len(slowrealMA5)
    operate = 0
    if df.iat[(dflen - 1), 18] > 80 or df.iat[(dflen - 1), 19] > 80:
        operate -= 2
    elif df.iat[(dflen - 1), 18] < 20 or df.iat[(dflen - 1), 19] < 20:
        operate += 2

    if (df.iat[(dflen - 2), 18] <= 50 and df.iat[(dflen - 1), 18] > 50) or (
                    df.iat[(dflen - 2), 19] <= 50 and df.iat[(dflen - 1), 19] > 50):
        operate += 4
    elif (df.iat[(dflen - 2), 18] >= 50 and df.iat[(dflen - 1), 18] < 50) or (
                    df.iat[(dflen - 2), 19] >= 50 and df.iat[(dflen - 1), 19] < 50):
        operate -= 4

    if df.iat[(dflen - 1), 7] >= df.iat[(dflen - 1), 8] and df.iat[(dflen - 1), 8] >= df.iat[(dflen - 1), 9]:
        if (slowrealMA5[MAlen - 1] <= slowrealMA10[MAlen - 1] and slowrealMA10[MAlen - 1] <= slowrealMA20[MAlen - 1]) or \
                (fastrealMA5[MAlen - 1] <= fastrealMA10[MAlen - 1] and fastrealMA10[MAlen - 1] <= fastrealMA20[
                        MAlen - 1]):
            operate -= 1
    elif df.iat[(dflen - 1), 7] <= df.iat[(dflen - 1), 8] and df.iat[(dflen - 1), 8] <= df.iat[(dflen - 1), 9]:
        if (slowrealMA5[MAlen - 1] >= slowrealMA10[MAlen - 1] and slowrealMA10[MAlen - 1] >= slowrealMA20[MAlen - 1]) or \
                (fastrealMA5[MAlen - 1] >= fastrealMA10[MAlen - 1] and fastrealMA10[MAlen - 1] >= fastrealMA20[
                        MAlen - 1]):
            operate += 1

    if df.iat[(dflen - 1), 19] > df.iat[(dflen - 1), 18] and df.iat[(dflen - 2), 19] <= df.iat[(dflen - 2), 18]:
        operate += 10
    elif df.iat[(dflen - 1), 19] < df.iat[(dflen - 1), 18] and df.iat[(dflen - 2), 19] >= df.iat[(dflen - 2), 18]:
        operate -= 10
    return (df, operate)


def output_csv(df, dist):
    # today = datetime.date.today()
    # current_day = today.strftime('%Y-%m-%d')
    reload(sys)
    df.to_csv(dist + end_date + 'stock.csv', encoding='utf-8')


df = get_stock_list()
Dist = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/result/macd_result/'
df = Get_TA(df)
output_csv(df, Dist)

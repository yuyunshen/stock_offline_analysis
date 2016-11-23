__author__ = 'qinfeizhang'

# coding:utf-8
import tushare as ts
import talib as ta
import numpy as np
import pandas as pd
import datetime
import sys
import numpy as np

start_date = '2014-01-01'
end_date = '2016-11-15'


def get_stock_list():
    df = ts.get_stock_basics()
    return df


def KDJ(high, low, close, N=9, M1=3, M2=3):
    datelen = len(high)
    kdjarr = []
    slowk = []
    slowd = []
    for i in range(datelen):
        if i - N < 0:
            b = 0
        else:
            b = i - N + 1
        rsvhigh = high[b:i + 1]
        rsvlow = low[b:i + 1]
        rsvclose = close[b:i + 1]
        rsv = (float(rsvclose[-1]) - float(min(rsvlow))) / (float(max(rsvhigh)) - float(min(rsvlow))) * 100
        if i == 0:
            k = rsv
            d = rsv
        else:
            k = 1 / float(M1) * rsv + (float(M1) - 1) / M1 * float(kdjarr[-1][1])
            d = 1 / float(M2) * k + (float(M2) - 1) / M2 * float(kdjarr[-1][2])
        j = 3 * k - 2 * d
        kdjarr.append(list((rsv, k, d, j)))
        slowk.append(k)
        slowd.append(d)
    return slowk, slowd


def big_vol(volume, length=30, times=2):
    if length > len(volume):
        length = len(volume)

    operate = 0
    cur_volume = volume[-1]
    total_volume = 0
    for i in range(1, length):
        total_volume += volume[-(i + 1)]

    if cur_volume > times * volume[-2] or cur_volume > times * total_volume / (length - 1):
        operate = 1

    return operate


def Get_TA(df_code):
    operate_array1 = []
    operate_array2 = []
    total = len(df_code)

    count = 0
    for code in df_code.index:
        try:
            df = ts.get_hist_data(code, start=start_date, end=end_date, ktype='W').sort_index(axis=0, ascending=True)
            df_day = ts.get_hist_data(code, start=start_date, end=end_date).sort_index(axis=0, ascending=True)
            count += 1
            print("processing " + str(count) + " in " + str(total))
            dflen = df.shape[0]
            operate1 = 0
            operate2 = 0
            if dflen > 35:
                (df, operate1) = Get_KDJ(df, 3)
                operate2 = big_vol(df_day['volume'], 30, 2)

        except Exception, e:
            print e
            operate1 = -100
            operate2 = -100
        operate_array1.append(operate1)
        operate_array2.append(operate2)

    df_code['KDJ'] = pd.Series(operate_array1, index=df_code.index)
    df_code['BIGVOLUME'] = pd.Series(operate_array2, index=df_code.index)
    return df_code


def Get_KDJ(df, h_length=3):
    slowk, slowd = KDJ(df['high'], df['low'], df['close'], N=9, M1=3, M2=3)
    # 16-17 K,D
    df['slowk'] = pd.Series(slowk, index=df.index)  # K
    df['slowd'] = pd.Series(slowd, index=df.index)  # D

    dflen = df.shape[0]
    operate = 0
    if df['slowk'][-1] > df['slowd'][-1] and df['slowk'][-2] < df['slowd'][-2]:
        hole_length = 0
        for i in range(dflen - 2):
            if df['slowk'][dflen - 2 - i] < df['slowd'][dflen - 2 - i]:
                hole_length += 1
            else:
                break

        if hole_length < h_length:
            operate += 1

    return (df, operate)


def output_csv(df, dist):
    reload(sys)
    df.to_csv(dist + end_date + 'stock.csv', encoding='utf-8')

#
# df = get_stock_list()
# Dist = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/result/macd_result/'
# df = Get_TA(df)
# output_csv(df, Dist)


df = ts.get_hist_data('000838', start=start_date, end=end_date).sort_index(axis=0, ascending=True)
# print type(df['high'])
print df
# print df['volume']
# print big_vol(df['volume'], 30, 2)

# print df
# big_vol(df['volume'], 30)
# # print df
# operate1 = 0
# print KDJ(df['high'], df['low'], df['close'], N=9, M1=3, M2=3)
# (df, operate1) = Get_KDJ(df)

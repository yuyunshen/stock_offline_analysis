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
path = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data/'


def get_stock_list():
    df = ts.get_stock_basics()
    return df


def get_history_data(df_code):
    count = 0
    for code in df_code.index:
        try:
            df_week = ts.get_hist_data(code, start=start_date, end=end_date, ktype='W').sort_index(axis=0,
                                                                                                   ascending=True)
            df_day = ts.get_hist_data(code, start=start_date, end=end_date).sort_index(axis=0, ascending=True)
            output_csv(code, df_week, path, 'weekly')
            output_csv(code, df_day, path, 'daily')

            count += 1
            print count
        except Exception, e:
            print e


def output_csv(code, data, path, type):
    reload(sys)
    if type == 'weekly':
        data.to_csv(path + 'weekly/' + code + '.csv', encoding='utf-8')
    if type == 'daily':
        data.to_csv(path + 'daily/' + code + '.csv', encoding='utf-8')


df = get_stock_list()
get_history_data(df)

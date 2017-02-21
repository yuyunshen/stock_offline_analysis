__author__ = 'qinfeizhang'

import Model
import pandas
import numpy as np
import utils.Utils


class KDJHoleVolumnPrice(Model.Model):
    # return date, operate
    def big_vol(self, stock, length=30, times=2):
        dflen = stock.shape[0]
        date_operate = {}
        for i in range(dflen):
            j = dflen - i - 1
            operate = 0
            cur_volume = stock['volume'][j]
            total_volume = 0
            if (j + 1) >= length:
                for k in range(0, length):
                    total_volume += stock['volume'][j - k]
                if cur_volume > times * stock['volume'][j - 1] and cur_volume > times * total_volume / length:
                    operate = 1
            if operate == 1:
                date_operate[stock.index[j]] = operate

        return date_operate

    def price_small_range(self, stock, length=30, price_range=1.05):
        dflen = stock.shape[0]
        date_operate = {}
        for i in range(dflen):
            j = dflen - i - 1
            operate = 0
            cur_price = stock['close'][j]
            total_price = 0
            if (j + 1) >= length:
                for k in range(0, length):
                    total_price += stock['close'][j - k]
                if cur_price < price_range * total_price / length:
                    operate = 1
            if operate == 1:
                date_operate[stock.index[j]] = operate

        return date_operate

    def KDJ(self, high, low, close, N=9, M1=3, M2=3):
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

    # return date, operate
    def get_kdj_hole(self, stock, h_length=3):
        slowk, slowd = self.KDJ(stock['high'], stock['low'], stock['close'], N=9, M1=3, M2=3)
        # 16-17 K,D
        stock['slowk'] = pandas.Series(slowk, index=stock.index)  # K
        stock['slowd'] = pandas.Series(slowd, index=stock.index)  # D

        dflen = stock.shape[0]

        date_operate = {}
        for i in range(dflen):
            j = dflen - 1 - i
            operate = 0
            # if j<=0, do not judge the operate
            if j > 10 and stock['slowk'][j] > stock['slowd'][j] and stock['slowk'][j - 1] < stock['slowd'][j - 1]:
                hole_length = 0
                for k in range(j):
                    if stock['slowk'][j - 1 - k] < stock['slowd'][j - 1 - k]:
                        hole_length += 1
                    else:
                        break
                if hole_length < h_length:
                    operate += 1

            if operate == 1:
                date_operate[stock.index[j]] = operate

        return date_operate

    def algo(self, data_list):
        date_selected_stocks = {}
        cnt = 1
        for stock in data_list:
            # stock[0] name, stock[1] daily data, stock[2] weekly data
            print "processing stock " + str(cnt)
            cnt += 1
            try:
                date_len = len(stock[1])
                if date_len > 35:
                    operate_kdj_list = self.get_kdj_hole(stock[2], 3)  # weekly data
                    operate_vol_list = self.big_vol(stock[1], 30, 2)  # daily data
                    operate_price_list = self.price_small_range(stock[1], 30, 1.05) #daily data
                    for weekly_date in operate_kdj_list:
                        next_work_day = utils.Utils.get_next_five_work_day(weekly_date)
                        for daily_day in next_work_day:
                            if daily_day in operate_vol_list and daily_day in operate_price_list:
                                if daily_day not in date_selected_stocks:
                                    date_stocks_temp = list()
                                    date_stocks_temp.append(stock[0])
                                    date_selected_stocks[daily_day] = date_stocks_temp
                                else:
                                    date_selected_stocks[daily_day].append(stock[0])
            except Exception, e:
                print e

        return date_selected_stocks


if __name__ == '__main__':
    data_path = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data'
    # data_path_test = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data_test'
    a = KDJHoleVolumnPrice(data_path, '20160101')
    a.run()

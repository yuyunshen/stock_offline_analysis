__author__ = 'qinfeizhang'

import Model
import pandas
import numpy as np


class KDJ(Model.Model):
    # return date, operate
    def big_vol(self, volume, length=30, times=2):
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
    def get_kdj(self, stock, h_length=3):
        slowk, slowd = self.KDJ(stock['high'], stock['low'], stock['close'], N=9, M1=3, M2=3)
        # 16-17 K,D
        stock['slowk'] = pandas.Series(slowk, index=stock.index)  # K
        stock['slowd'] = pandas.Series(slowd, index=stock.index)  # D

        dflen = stock.shape[0]
        print dflen

        operate = {}
        if stock['slowk'][-1] > stock['slowd'][-1] and stock['slowk'][-2] < stock['slowd'][-2]:
            hole_length = 0
            for i in range(dflen - 2):
                if stock['slowk'][dflen - 2 - i] < stock['slowd'][dflen - 2 - i]:
                    hole_length += 1
                else:
                    break

            if hole_length < h_length:
                operate += 1

        # print stock.ix['2016-11-04']
        return operate

    def algo(self, data_list):
        stock_id_list = []
        operate_array_kdj = []
        operate_array_vol = []
        cnt = 1
        for stock in data_list:
            # stock[0] name, stock[1] daily data, stock[2] weekly data
            print "processing stock " + str(cnt)
            cnt += 1
            operate_kdj = 0
            operate_vol = 0
            try:
                date_len = len(stock[1])
                if date_len > 35:
                    operate_kdj = self.get_kdj(stock[2], 3)  # weekly data
                    operate_vol = self.big_vol(np.array(stock[1]['volume']), 30, 2)  # daily data
            except Exception, e:
                operate_kdj = -100
                operate_vol = -100
                print e
            stock_id_list.append(stock[0])
            operate_array_kdj.append(operate_kdj)
            operate_array_vol.append(operate_vol)
        result = pandas.DataFrame({'id': stock_id_list, 'kdj': operate_array_kdj, 'vol': operate_array_vol})

        return result


if __name__ == '__main__':
    # data_path = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data'
    data_path_test = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data_test'
    a = KDJ(data_path_test, '20160101')
    a.run()

__author__ = 'qinfeizhang'

import Model
import pandas
import numpy as np
import utils.Utils


class PriceSmallRangeBigVolumn(Model.Model):
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
            operate = 1
            total_price = 0
            if (j + 1) >= length:
                for k in range(0, length):
                    total_price += stock['close'][j - k]
                avg_price = total_price / length
                for k in range(0, length):
                    if stock['close'][j - k] > price_range * avg_price or stock['close'][
                                j - k] < avg_price / price_range:
                        operate = 0
                        break

                if operate == 1 and stock['close'][j] > stock['ma5'][j] > stock['ma10'][j] > stock['ma20'][j]:
                    operate = 1
                else:
                    operate = 0

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
                    operate_vol_list = self.big_vol(stock[1], 30, 2)  # daily data
                    operate_price_list = self.price_small_range(stock[1], 30, 1.05)  # daily data

                    for daily_day in operate_vol_list:
                        if daily_day in operate_price_list:
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
    # data_path = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data'
    data_path_test = '/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data_test'
    a = PriceSmallRangeBigVolumn(data_path_test, '20160101')
    a.run()

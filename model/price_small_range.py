__author__ = 'qinfeizhang'

import Model
import pandas
import numpy as np
import utils.Utils


class PriceSmallRange(Model.Model):
    def price_small_range(self, stock, length=20, price_range=1.05):
        dflen = stock.shape[0]
        date_operate = {}
        for i in range(dflen):
            j = dflen - i - 1
            operate = 0
            min_price = 1000000
            max_price = -1
            if (j + 1) >= length:
                for k in range(0, length):
                    if min(stock['close'][j - k], stock['open'][j - k]) < min_price:
                        min_price = min(stock['close'][j - k], stock['open'][j - k])
                    if max(stock['close'][j - k], stock['open'][j - k]) > max_price:
                        max_price = max(stock['close'][j - k], stock['open'][j - k])

                if max_price / min_price < price_range and stock['close'][j] >= stock['ma5'][j] >= stock['ma10'][j] >= \
                        stock['ma20'][j] and stock['volume'][j] >= stock['v_ma5'][j] >= stock['v_ma10'][j] >= \
                        stock['v_ma20'][j]:
                    operate = 1

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
                    operate_price_list = self.price_small_range(stock[1], 20, 1.05)  # daily data
                    for daily_day in operate_price_list:
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
    a = PriceSmallRange(data_path, '20160101')
    a.run()

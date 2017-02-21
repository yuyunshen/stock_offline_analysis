__author__ = 'qinfeizhang'

import os
import pandas
import sys
import utils.Utils
import numpy as np


class Model(object):
    def __init__(self, data_path, date_test):
        self.data_path = data_path
        self.date_test = date_test

    def load_data(self):
        data_list = list()
        data_dict = dict()
        for root, dirs, stock_names in os.walk(self.data_path + '/daily'):
            cnt = 1
            for stock_name in stock_names:
                stock = list()
                stock.append(stock_name.split('.')[0])
                # load daily data
                stock.append(pandas.read_csv(self.data_path + '/daily/' + stock_name, index_col='date'))
                # load weekly data
                stock.append(pandas.read_csv(self.data_path + '/weekly/' + stock_name, index_col='date'))
                data_list.append(stock)
                data_dict[stock[0]] = stock
                if cnt % 100 == 0:
                    print 'loading daily and weekly data ' + str(cnt)
                cnt += 1
        return data_list, data_dict

    # return: hashmap, key: date, value: stocks selected
    def run(self):
        data_list, data_dict = self.load_data()
        date_selected_stocks = self.algo(data_list)
        self.output_selected_stocks(date_selected_stocks)
        self.evaluate(data_dict, date_selected_stocks)
        # self.output_csv(result)

    def evaluate(self, data_dict, date_selected_stocks):
        print 'simulating'
        o_file = open(self.data_path + '/evaluate_stocks.csv', 'w')

        summary_result = dict()

        dates = date_selected_stocks.keys()
        dates.sort()
        for date in dates:
            o_file.write('\n\n' + date + '\n')
            stocks = date_selected_stocks[date]
            for stock in stocks:
                stock_data = data_dict[stock]
                date_end = utils.Utils.get_n_next_date(date, 7)
                eva_data_range = stock_data[1][date: date_end]
                price_change = np.array(eva_data_range['close'])
                o_file.write(stock + ': ' + str(price_change) + '\n')

                price_change_rate = (int)(100 * (price_change[-1] - price_change[0]) / price_change[0])
                if price_change_rate not in summary_result:
                    summary_result[price_change_rate] = 1
                else:
                    summary_result[price_change_rate] += 1

        o_file.write("\nsummary:\n")
        rates = summary_result.keys()
        rates.sort()
        for rate in rates:
            o_file.write(str(rate) + ': ' + str(summary_result[rate]) + '\n')

        o_file.close()

    def output_selected_stocks(self, date_selected_stocks):
        o_file = open(self.data_path + '/date_selected_stocks.csv', 'w')
        for date in date_selected_stocks:
            o_file.write(date + '\n')
            o_file.write(str(date_selected_stocks[date]) + '\n\n')
        o_file.close()

    def output_csv(self, result):
        reload(sys)
        result.to_csv(self.data_path + '/stock.csv', encoding='utf-8')

    # sub-class need to rewrite this function
    def algo(self, data_list):
        print 'runing algo'


if __name__ == '__main__':
    a = Model('/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data', '20160101')
    a.run()

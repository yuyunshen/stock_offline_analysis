__author__ = 'qinfeizhang'

import os
import pandas
import sys


class Model(object):
    def __init__(self, data_path, date_test):
        self.data_path = data_path
        self.date_test = date_test

    def load_data(self):
        data_list = []
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
                if cnt % 100 == 0:
                    print 'loading daily and weekly data ' + str(cnt)
                cnt += 1
        return data_list

    # return: hashmap, key: date, value: stocks selected
    def run(self):
        data_list = self.load_data()
        result = self.algo(data_list)
        self.evaluate()
        self.output_csv(result)

    def evaluate(self):
        print 'simulating'

    def output_csv(self, result):
        reload(sys)
        result.to_csv(self.data_path + '/stock.csv', encoding='utf-8')

    # sub-class need to rewrite this function
    def algo(self, data_list):
        print 'runing algo'


if __name__ == '__main__':
    a = Model('/Users/qinfeizhang/PycharmProjects/stock_offline_analysis/history_data', '20160101')
    a.run()

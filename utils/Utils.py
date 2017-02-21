__author__ = 'qinfeizhang'
from datetime import datetime
import datetime as dt


# get the next five work days, convert weekly date to daily date
def get_next_five_work_day(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    days = []
    for i in range(1, 8):
        day = date - dt.timedelta(days=-i)
        if day.isoweekday() != 6 and day.isoweekday() != 7:
            days.append(day.strftime('%Y-%m-%d'))

    return days


# get the n next date
def get_n_next_date(date_str, n = 30):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    days = []
    day = date - dt.timedelta(days=-n)
    return day.strftime('%Y-%m-%d')


if __name__ == '__main__':
    # print get_next_five_work_day('2016-11-11')
    print get_n_next_date('2016-01-01', 30)

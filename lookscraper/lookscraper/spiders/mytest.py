import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import math

def to_time( string):
    string = string.replace('over', '')
    string = string.replace('year', 'years')
    string = string.replace('month', 'months')
    string = string.replace('week', 'weeks')
    string = string.replace('day', 'days')
    string = string.replace('hour', 'hours')
    string = string.replace('minute', 'minutes')
    string = string.replace('ss', 's')

    parsed_s = [string.split()[:2]]
    print(parsed_s)
    time_dict = dict((fmt, float(amount)) for amount, fmt in parsed_s)
    if time_dict.get('months'):
        past_time = date.today() - relativedelta(months=time_dict['months'])
    elif time_dict.get('years'):
        past_time = datetime.datetime.now() - datetime.timedelta(days=time_dict['years'] * 365)
    else:
        dt = datetime.timedelta(**time_dict)
        past_time = datetime.datetime.now() - dt

    return past_time


print(to_time('over 4 year ago'))
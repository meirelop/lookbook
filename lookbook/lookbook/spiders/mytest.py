import datetime

s = "3 minute ago"
def to_time(string):
    string.replace('day', 'days')
    string.replace('hour', 'hours')
    string = string.replace('minute', 'minutes')
    print(string)

    # parsed_s = [string.split()[:2]]
    # time_dict = dict((fmt, float(amount)) for amount, fmt in parsed_s)
    # dt = datetime.timedelta(**time_dict)
    # past_time = datetime.datetime.now() - dt
    # return past_time

print(to_time(s))
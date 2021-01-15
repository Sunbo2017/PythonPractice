#coding=utf-8

import datetime
import os


current = datetime.datetime.now()
start = datetime.date(current.year, 1, 1)
last_day = datetime.date(current.year, current.month, current.day)
isfirst = start.weekday()
last_week = last_day.strftime('%W')
print(start)
print(last_day)
print(start.weekday())
print(last_day.strftime('%W'))
weeks = {}
if isfirst != 0:
    end = datetime.timedelta(7 - start.weekday() - 1)
    weeks[0] = [start, start + end]
start += datetime.timedelta(7 - start.weekday())
print(os.path.basename(r"D:\GoProject\src\xclarity-restapi"))
for i in range(0, int(last_week)):
    days = datetime.timedelta(weeks=i)
    end = start + days  # 每周的开始时间

    if i + 1 == int(last_week):
        weeks[i + 1] = [end, last_day]
    else:
        weeks[i + 1] = [end, end + datetime.timedelta(6)]
for i,week in weeks.items():
    print(i)
    print(week[0])
    print(week[1])
    datestr = week[0].strftime('%Y-%m-%d')
    print(datestr)
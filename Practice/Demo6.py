# coding=utf-8

from getpass import getpass
import datetime

names = ['Leo', 'Lili', 'Sam', 'Tom']
ages = [30, 20, 28, 25]
habits = ['Movies', 'Dance', 'Reading', 'Singing']
print zip(names, ages, habits)
for name, age, habit in zip(names, ages, habits):
    print '{0} is {1} old and like {2})'.format(name, age, habit)

username = raw_input('Username: ')
passwd = getpass('Passwd:')
print ('Logging In...')

print datetime.datetime.utcnow()

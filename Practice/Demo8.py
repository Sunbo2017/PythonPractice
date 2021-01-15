#coding=utf-8


class Sun:
    def __init__(self, name='Sun'):
        self.name = name

    def say_hi(self, say):
        print self.name, "say", say

    def run(self):
        print 'run fast'

if __name__ == '__main__':
    s = Sun('SUNBO')
    s.say_hi('boring...')
    print dir(s)
    print s.__module__

# coding=utf-8


def test():
    print "test"


def count():
    fs = []
    for i in range(1, 4):
        def f(j):
            def g():
                z = j * j
                return z
            return g
        r = f(i)
        fs.append(r)
    return fs


f1, f2, f3 = count()
print f1(), f2(), f3()

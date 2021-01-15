# coding=utf-8
import threading
import time


class ThreadTest1:
    def print_name(self, name):
        print(time.time())
        print(name)

    def test_thread(self):
        names = ['令狐冲', '张无忌', '郭靖', '杨过']
        for name in names:
            try:
                if name == '张无忌':
                    raise Exception
                threading.Thread(target=self.print_name(name))
            except Exception as e:
                print(e)


class ThreadTest2(threading.Thread):
    def __init__(self, name):
        super(ThreadTest2, self).__init__(name)
        self.name = name

    def run(self):
        self.print_name(self.name)

    def print_name(self, name):
        print(time.time())
        print(name)


if __name__ == '__main__':
    driver = ThreadTest1()
    driver.test_thread()
    time.sleep(10)

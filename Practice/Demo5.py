# coding=utf-8


class Dog(object):
     """ 一次模拟小狗的简单尝试 """

     def __init__(self, name, age):
         """ 初始化属性 name 和 age"""
         self.name = name
         self.age = age

     def sit(self):
         """ 模拟小狗被命令时蹲下 """
         print(self.name.title() + " is now sitting.")

     def roll_over(self):
         """ 模拟小狗被命令时打滚 """
         print(self.name.title() + " rolled over!")


my_dog = Dog('willie', 6)
print("My dog's name is " + my_dog.name.title() + ".")
print("My dog is " + str(my_dog.age) + " years old.")

my_dog.sit()
my_dog.roll_over()


class Car(object):

    def __init__(self, make, model, year):
        """ 初始化描述汽车的属性 """
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0

    def get_descriptive_name(self):
        """ 返回整洁的描述性信息 """
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        """ 打印一条指出汽车里程的消息 """
        print("This car has " + str(self.odometer_reading) + " miles on it.")

    def set_year(self, year):
        self.year = year


my_new_car = Car('audi', 'a4', 2016)
print(my_new_car.get_descriptive_name())
my_new_car.read_odometer()
my_new_car.odometer_reading = 100
my_new_car.read_odometer()
my_new_car.set_year(2017)
print my_new_car.get_descriptive_name()


class ElectricCar(Car):
    """ 初始化父类的属性 """
    def __init__(self, make, model, year, size):
        super(ElectricCar, self).__init__(make, model, year)
        self.size = size

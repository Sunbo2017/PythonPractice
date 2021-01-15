# coding=utf-8

for v in range(1, 5):
    print v
# 将数字转为列表
numbers = list(range(1, 10))
print numbers
# 指定间隔
double = list(range(0, 10, 2))
print double

squares = []
for v in range(1, 10):
    # ** 为乘方运算
    squares.append(v**2)
print squares
print min(squares)
print max(squares)
print sum(squares)

# 列表解析
cubes = [v**3 for v in range(0, 5)]
print cubes
cubes = [v**2 for v in (1, 2, 3, 4)]
print cubes

# 使用切片
cars = ["AE86", "GTR", "FR", "EVO3", "ZERO"]
print cars[1:4]
print cars[:4]
for car in cars[:4]:
    if car == "FR":
        print car.lower()
    else:
        print car.lower().title()

'''复制列表'''
newCars = cars[:]
print newCars
print "FR" in cars
print "fr" in cars
if "BMW" not in cars:
    cars.append("bmw".upper())
print cars




# coding=utf-8

print("hello world")
hello = "world"
print hello
animals = ["cat", "dog", "pig", "line", "tigger", "monkey"]
# 首字母大写
print animals[4].title()
# 修改列表元素
animals[2] = "big pig"
print animals
# 在列表末尾添加元素
animals.append("elephant")
print animals
# 在指定索引位置前插入元素
animals.insert(2, "snake")
print animals
del animals[4]
print animals[4]
# 删除；列表最后一个元素
print animals.pop()
print animals
# 根据value删除元素
animals.remove("dog")
print animals
# 临时排序
print sorted(animals)
print animals
# 永久排序
animals.sort()
print animals
# 反转列表元素
animals.reverse()
print animals
# 获取列表长度
print len(animals)
# 遍历列表
for a in animals:
    print a.title()
print "over"

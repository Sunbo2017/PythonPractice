# coding=utf-8


def hello():
    """打印输出"""
    print "hello python world"
    print "PEP8:函数或类与上一代码块要隔两行"


# 函数或类与上一代码块隔两行
hello()


def hello_(name="Lucy", age=23):
    print "\nhello,my name is ", name, "I am ", age, " years old."
    print "Are you OK?"


"""使用默认值"""
hello_()
"""位置实参"""
hello_("Jack", 26)
"""关键字实参"""
hello_(age=30, name="Mike")


def hello1(name, age=18, sex="M"):
    """有默认值的参数必须在无默认值参数后边"""
    print "\nhello,my name is ", name, "I am ", age, " years old."
    if sex == "M":
        print "I am a boy."
    else:
        print "I am a girl."


hello1(name="Lily", sex="W")


def sex(title):
    print "\n", title
    if title == "boy":
        return "M"
    else:
        return "W"


hello1("John", sex=sex("boy"))


def get_formatted_name(first_name, last_name):
    """ 返回整洁的姓名 """
    full_name = first_name + ' ' + last_name
    return full_name.title()


"""
while True:
    print("\nPlease tell me your name:")
    print("(enter 'q' at any time to quit)")
    f_name = input("First name: ")
    if f_name == 'q':
        break
    l_name = input("Last name: ")
    if l_name == 'q':
        break
    formatted_name = get_formatted_name(f_name, l_name)
    print("\nHello, " + formatted_name + "!")
"""


def greet_users(names):
    """ 向列表中的每位用户都发出简单的问候 """
    for name in names:
        msg = "Hello, " + name.title() + "!"
        print(msg)


print ""
usernames = ['hannah', 'ty', 'margot']
greet_users(usernames)


def print_models(unprinted_designs, completed_models):
    """
    模拟打印每个设计，直到没有未打印的设计为止
    打印每个设计后，都将其移到列表 completed_models 中
    """
    while unprinted_designs:
        current_design = unprinted_designs.pop()
        #  模拟根据设计制作 3D 打印模型的过程
        print("Printing model: " + current_design)
        completed_models.append(current_design)


def show_completed_models(completed_models):
    """ 显示打印好的所有模型 """
    print("\nThe following models have been printed:")
    for completed_model in completed_models:
        print(completed_model)


unprinted_designs = ['iphone case', 'robot pendant', 'dodecahedron']
completed_models = []
print ''
"""函数处理列表会永久改变列表内容"""
print_models(unprinted_designs, completed_models)
print "函数处理后列表内容：", unprinted_designs
show_completed_models(completed_models)
print ''
unprinted_designs = ['iphone case', 'robot pendant', 'dodecahedron', "lenovo"]
completed_models = []
"""传入列表副本，不会改变原列表内容"""
print_models(unprinted_designs[:], completed_models)
print "函数处理后列表内容：", unprinted_designs
show_completed_models(completed_models)


def make_pizza(*materials):
    """ 参数名前加*表示可接收任意数量参数，打印顾客点的所有配料 """
    print(materials)
    """实际上是将所有参数组成一个元组"""
    print type(materials)
    for m in materials:
        print m


make_pizza('pepperoni')
make_pizza('mushrooms', 'green peppers', 'extra cheese')


def make_pizza1(size, *toppings):
    """位置形参和任意数量形参一起使用时，任意数量形参必须在最后"""
    """ 概述要制作的比萨 """
    print("\nMaking a " + str(size) + "-inch pizza with the following toppings:")
    for topping in toppings:
        print("- " + topping)


make_pizza1(16, 'pepperoni')
make_pizza1(12, 'mushrooms', 'green peppers', 'extra cheese')


def build_profile(first, last, **user_info):
    """ 创建一个字典，其中包含我们知道的有关用户的一切 """
    profile = {}
    profile['first_name'] = first
    profile['last_name'] = last
    for key, value in user_info.items():
        profile[key] = value
    return profile


print '参数前加**表示可以接收任意数量的字典类型参数'
""" 参数前加**表示可以接收任意数量的字典类型参数 """
user_profile = build_profile('albert', 'einstein',
                             location='princeton',
                             field='physics')
print(user_profile)

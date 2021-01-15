# coding=utf-8

countries = {"China": "Beijing", "American": "Washington", "England": "London", "France": "Paris"}
print countries["England"]
# 添加新的键值对
countries["Russia"] = "Moscow"
print countries
del countries["American"]
print countries

languages = {
 'jen': 'python',
 'sarah': 'c',
 'edward': 'ruby',
 'phil': 'java',
}
print("phil's language is " + languages['phil'])

# 遍历字典
for k, v in languages.items():
    print k + "'s language is " + v

# 遍历所有key
for k in languages.keys():
    print k

# 遍历所有value
for v in languages.values():
    print v

# 字典列表
alien_0 = {'color': 'green', 'points': 5}
alien_1 = {'color': 'yellow', 'points': 10}
alien_2 = {'color': 'red', 'points': 15}
aliens = [alien_0, alien_1, alien_2]
print aliens
for alien in aliens:
    print(alien)

# 字典中存储列表
pizza = {
 'crust': 'thick',
 'toppings': ['mushrooms', 'extra cheese'],
}
print pizza
#  概述所点的比萨
print("You ordered a " + pizza['crust'] + "-crust pizza " + "with the following toppings:")
for topping in pizza['toppings']:
    print("\t" + topping)

# 字典中存储字典
users = {
 'aeinstein': {
  'first': 'albert',
  'last': 'einstein',
  'location': 'princeton',
 },
 'mcurie': {
  'first': 'marie',
  'last': 'curie',
  'location': 'paris',
 }
}
print users
for username, user_info in users.items():
    print("\nUsername: " + username)
    full_name = user_info['first'] + " " + user_info['last']
    location = user_info['location']
    print("\tFull name: " + full_name.title())
    print("\tLocation: " + location.title())

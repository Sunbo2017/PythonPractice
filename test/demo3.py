from datetime import datetime
import time

start_time = datetime.utcnow()
s_time = time.time()
m_list = [{'dem': {'systemName': 'sys111'}}, {'dem': {'deviceName': 'dev111'}}, {'dem': {'dev': 'dev111'}}]
for m in m_list:
    if 'systemName' in m['dem'].keys():
        system_name = m['dem']['systemName']
    elif 'deviceName' in m['dem'].keys():
        system_name = m['dem']['deviceName']
    else:
        system_name = "null"
    print(system_name)
for i in range(0, 3):
    print(i)
    time.sleep(1)

uuid = 'abcde'
uuid1 = list(uuid)
print(uuid1)

uuid2 = [uuid]
print(uuid2)

list1 = ['1', '2', '3']
list2 = ['5', '4', '3']
list3 = list1 + list2
list4 = list(set(list3))
print(list3)
print(list4)
end_time = datetime.utcnow()
e_time = time.time()
print('start time is {},end time is {},use {} seconds'.
      format(start_time, end_time, (e_time - s_time)))
print('start time is {},end time is {},use {} ms'.
      format(start_time, end_time, (end_time - start_time).seconds * 1000))

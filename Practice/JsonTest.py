#!/usr/bin/env python
#coding=utf-8

import json
import datetime

response = '{"InstanceId":"i-2zebjtu5uncrdievpqqi","RequestId":"52557A3A-5EC5-49DF-BE5B-244C9A28322B"}'
obj = json.loads(response)
print obj
print obj.get("InstanceId")

ips = [u'192.168.1.234', u'192.168.1.456']
nips = []
print str(ips)
for ip in ips:
    nips.append(ip.encode('utf-8'))
print str(nips)
print json.dumps(str(nips))

json_str = "['192.168.1.234', '192.168.1.456']"
# print json.loads(json_str)

now = datetime.datetime.utcnow()
time = datetime.datetime(2019, 4, 7, 4, 30, 3, 628556)
print (now-time).seconds

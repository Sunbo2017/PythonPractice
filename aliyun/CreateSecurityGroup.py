#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.CreateSecurityGroupRequest import CreateSecurityGroupRequest

client = AcsClient('LTAIwLKQlyeJbokl', '46UNWckqbFGXctFT19tyG1HXzTC51g', 'cn-qingdao')

request = CreateSecurityGroupRequest()
request.set_accept_format('json')

response = client.do_action_with_exception(request)
# python2:  print(response)
print(response)

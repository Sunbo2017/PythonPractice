#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest

client = AcsClient('LTAIJyMV61TqkUyr', 'p0HI4mgKQyR55M3fwlhudwWz9xuMFK', 'cn-beijing')

request = StopInstanceRequest()
request.set_accept_format('json')
request.set_InstanceId("i-2ze492eknq7kaqr2s9yv")

response = client.do_action_with_exception(request)
# python2:  print(response)
print(response)

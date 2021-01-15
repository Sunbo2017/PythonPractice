#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeAvailableResourceRequest import DescribeAvailableResourceRequest

client = AcsClient('LTAIJyMV61TqkUyr', 'p0HI4mgKQyR55M3fwlhudwWz9xuMFK', 'cn-beijing')

request = DescribeAvailableResourceRequest()
request.set_accept_format('json')

request.set_DestinationResource("InstanceType")
request.set_IoOptimized("optimized")
request.set_ZoneId("cn-beijing-a")

response = client.do_action_with_exception(request)
print(response)
#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstanceTypesRequest import DescribeInstanceTypesRequest

client = AcsClient('LTAIJyMV61TqkUyr', 'p0HI4mgKQyR55M3fwlhudwWz9xuMFK', 'cn-beijing')

request = DescribeInstanceTypesRequest()
request.set_accept_format('json')
request.set_InstanceTypeFamily("ecs.t1")
response = client.do_action_with_exception(request)
print(response)

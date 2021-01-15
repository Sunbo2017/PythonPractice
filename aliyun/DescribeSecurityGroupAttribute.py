#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupAttributeRequest import DescribeSecurityGroupAttributeRequest

client = AcsClient('LTAIwLKQlyeJbokl', '46UNWckqbFGXctFT19tyG1HXzTC51g', 'cn-beijing')

request = DescribeSecurityGroupAttributeRequest()
request.set_accept_format('json')

request.set_SecurityGroupId("sg-2zefs8mk0inooylan26w")

response = client.do_action_with_exception(request)
print(response)

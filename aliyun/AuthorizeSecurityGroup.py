#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.AuthorizeSecurityGroupRequest import AuthorizeSecurityGroupRequest

client = AcsClient('LTAIwLKQlyeJbokl', '46UNWckqbFGXctFT19tyG1HXzTC51g', 'cn-beijing')

request = AuthorizeSecurityGroupRequest()
request.set_accept_format('json')

request.set_Policy("accept")
request.set_NicType("intranet")
request.set_PortRange("6379/6379")
request.set_SourceCidrIp("0.0.0.0/0")
request.set_IpProtocol("tcp")
request.set_SecurityGroupId("sg-2zefs8mk0inooylan26w")

response = client.do_action_with_exception(request)
print(response)

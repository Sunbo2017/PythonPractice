#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.RebootInstanceRequest import RebootInstanceRequest

client = AcsClient('LTAIwLKQlyeJbokl', '46UNWckqbFGXctFT19tyG1HXzTC51g', 'cn-beijing')

request = RebootInstanceRequest()
request.set_accept_format('json')

request.set_InstanceId("i-2zed6jsnltwqb8ubsceu")

response = client.do_action_with_exception(request)
print(response)

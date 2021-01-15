#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest

client = AcsClient('LTAIDYZHBnIzHUTg', 'mT1ZJLSQgyAKTht4BkeHTeh4XjPqQa', 'cn-beijing')

request = DeleteInstanceRequest()
request.set_accept_format('json')
request.set_Force(True)
request.set_InstanceId("i-2zed4tisi44jrzkvrjg0")

response = client.do_action_with_exception(request)
print(response)

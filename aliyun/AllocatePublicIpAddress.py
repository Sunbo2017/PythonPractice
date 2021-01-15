#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.AllocatePublicIpAddressRequest import AllocatePublicIpAddressRequest

client = AcsClient('LTAIDYZHBnIzHUTg', 'mT1ZJLSQgyAKTht4BkeHTeh4XjPqQa', 'cn-beijing')

request = AllocatePublicIpAddressRequest()
request.set_accept_format('json')

request.set_InstanceId("i-2zeg9k9upc9avwt92q4e")

response = client.do_action_with_exception(request)
print(response)

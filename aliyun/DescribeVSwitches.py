#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkvpc.request.v20160428.DescribeVSwitchesRequest import DescribeVSwitchesRequest
import json

client = AcsClient('LTAIJyMV61TqkUyr', 'p0HI4mgKQyR55M3fwlhudwWz9xuMFK', 'cn-beijing')

request = DescribeVSwitchesRequest()
request.set_accept_format('json')
# request.set_ZoneId("cn-beijing-a")
request.set_VSwitchId("vsw-2zeuizgqzu6ef80yq8wa0")
response = client.do_action_with_exception(request)
print(response)
res_obj = json.loads(response)
vswitch = res_obj.get("VSwitches").get("VSwitch")[0]
zone_id = vswitch.get("ZoneId")
print zone_id

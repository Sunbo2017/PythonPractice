#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
import json

client = AcsClient('LTAIDYZHBnIzHUTg', 'mT1ZJLSQgyAKTht4BkeHTeh4XjPqQa', 'cn-beijing')

request = DescribeInstancesRequest()
request.set_accept_format('json')
instance_ids = ["i-2ze6kp0u4sppbs4w8ti5"]
# instance_ids = [u'i-2zefmx5g4wb34qki200q'.encode('utf-8')]
request.set_InstanceIds(instance_ids)

response = client.do_action_with_exception(request)
print(response)
res_obj = json.loads(response)
instances = res_obj.get("Instances").get("Instance")
print instances
for instance in instances:
    instance_name = instance.get('InstanceName')
    extra_server_id = instance.get('InstanceId')
    extra_server_status = instance.get('Status')
    extra_server_cpu = instance.get('Cpu', None)
    extra_server_memory = instance.get('Memory', None)
    zone_id = instance.get('ZoneId', None)
    instance_type = instance.get('InstanceType', None)
    create_time = instance.get('CreationTime', None)
    instance_charge_type = instance.get('InstanceChargeType', None)
    extra_server_public_ip = None
    extra_server_private_ip = ''
    extra_server_public_ips = instance.get('PublicIpAddress', None)
    if extra_server_public_ips:
        public_ips = extra_server_public_ips.get('IpAddress', None)
        if public_ips:
            extra_server_public_ip = public_ips[0]
    extra_server_private_ips = instance.get('VpcAttributes').get('PrivateIpAddress', None)
    if extra_server_private_ips:
        private_ips = extra_server_private_ips.get('IpAddress', None)
        if private_ips:
            for private_ip in private_ips:
                extra_server_private_ip += private_ip + ";"
    print extra_server_id
    print instance_name
    print zone_id
    print instance_type
    print create_time
    print instance_charge_type
    print extra_server_status
    print extra_server_cpu
    print extra_server_memory
    print extra_server_public_ip
    print extra_server_private_ip


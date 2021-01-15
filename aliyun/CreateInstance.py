#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.CreateInstanceRequest import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.AllocatePublicIpAddressRequest import AllocatePublicIpAddressRequest
import base64
import json

class EcsRedisDriver:

    def create_server(self):
        client = AcsClient('LTAIJyMV61TqkUyr', 'p0HI4mgKQyR55M3fwlhudwWz9xuMFK', 'cn-beijing')

        request = CreateInstanceRequest()
        request.set_accept_format('json')
        redis_path = "/etc/redis/redis.conf"
        userdate = self.make_userdata()
        request.set_accept_format('json')
        request.set_ImageId("m-2ze0bcvme2womu68fcr2")
        request.set_InstanceType("ecs.mn4.small")
        request.set_SecurityGroupId("sg-2ze67u2tlcqpydv83dfv")
        request.set_InstanceName("rest-agent")
        request.set_Description("rest agent test")
        request.set_HostName("rest-agent")
        request.set_Password("YUdi#331")
        request.set_UserData(userdate)
        request.set_IoOptimized("optimized")
        request.set_SystemDiskCategory("cloud_efficiency")
        # request.set_SystemDiskDiskName(None)
        request.set_SystemDiskSize(200)
        # request.set_DataDisks(None)
        request.set_InstanceChargeType("PostPaid")
        request.set_VSwitchId("vsw-2zeuizgqzu6ef80yq8wa0")
        request.set_InternetMaxBandwidthOut(100)

        response = client.do_action_with_exception(request)
        print(response)
        return response

    def get_password_template(self, password, path):
        password = password
        pass_input_str = "requirepass {}".format(password)
        template_str = '''
        sudo chmod 644 {1}
        echo "{0}" >> {1}
        '''.format(pass_input_str, path)
        return base64.b64encode(template_str)

    def make_userdata(self):
        ustr = '''#!/bin/sh
        echo "Hello World. The time is now $(date -R)!" | tee /usr/local/output.txt
        '''
        return base64.b64encode(ustr)

    def allocate_public_ip(self, instance_id):
        ''' 分配公网ip '''

        client = AcsClient('LTAIJyMV61TqkUyr', 'p0HI4mgKQyR55M3fwlhudwWz9xuMFK', 'cn-beijing')

        request = AllocatePublicIpAddressRequest()
        request.set_accept_format('json')

        request.set_InstanceId(instance_id)

        response = client.do_action_with_exception(request)
        print(response)

if __name__ == '__main__':
    driver = EcsRedisDriver()
    response = driver.create_server()

#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
import base64
import json

class EcsRedisDriver:

    def create_server(self):
        client = AcsClient('LTAIDYZHBnIzHUTg', 'mT1ZJLSQgyAKTht4BkeHTeh4XjPqQa', 'cn-beijing')

        request = RunInstancesRequest()
        request.set_accept_format('json')
        redis_path = "/etc/redis.conf"
        userdate = self.get_password_template("rds123", None)
        request = RunInstancesRequest()
        request.set_accept_format('json')
        request.set_ImageId("m-2zed4tisi44jrvmodaag")
        request.set_InstanceType("ecs.n4.large")
        request.set_SecurityGroupId("sg-2ze0x4gzi8h8fs5aksyh")
        request.set_InstanceName("test-ali527")
        request.set_Description("rest agent test")
        request.set_HostName("rest-agent")
        request.set_Password("YUdi#331")
        request.set_UserData(userdate)
        request.set_IoOptimized("optimized")
        request.set_SystemDiskCategory("cloud_efficiency")
        # request.set_SystemDiskDiskName(None)
        request.set_SystemDiskSize(20)
        # request.set_DataDisks(None)
        request.set_InstanceChargeType("PostPaid")
        request.set_VSwitchId("vsw-2zerw1p7ycdilqcbm0h94")
        request.set_InternetMaxBandwidthOut(100)

        response = client.do_action_with_exception(request)
        print(response)
        res_obj = json.loads(response)
        print res_obj.get("InstanceIdSets").get("InstanceIdSet")[0]

    def get_password_template(self, password, data_disks):
        template_str = '#!/bin/sh\n'
        if data_disks:
            data_disk = data_disks[0]
            device = data_disk.device
            target_path = '/var/lib/redis'
            fstab_path = '/etc/fstab'
            mount_str = '''
                    sudo mkfs.xfs {0}
                    mount {0} {1}
                    sudo echo {0} {1} xfs defaults 1 1  >> {2}
                    mount -a
                    '''.format(device, target_path, fstab_path)
            template_str += mount_str
        app_conf_path = '/opt/HybirdRedisGuestAgent/conf/app.conf'
        template_str += '''
                echo >> {1}
                echo 'redis_password={0}' >> {1}
                redis-cli CONFIG SET requirepass  {0}
                redis-cli -a {0} CONFIG REWRITE'''.format(password, app_conf_path, 29300)
        return base64.b64encode(template_str)

    def make_userdata(self):
        ustr = '''#!/bin/sh\n
        echo "Hello World. The time is now $(date -R)!" | tee /usr/local/output.txt
        '''
        return base64.b64encode(ustr)

if __name__ == '__main__':
    driver = EcsRedisDriver()
    driver.create_server()
    # print driver.get_password_template("Rds123", "/etc/redis.conf")

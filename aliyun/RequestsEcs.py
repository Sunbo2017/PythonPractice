import requests
from oslo_serialization import jsonutils
import base64

class EcsRedisDriver:
    def create_server(self, region, zone, image, instance_type, secure_group=None,
                      name=None, host_name=None, root_pass=None, db_pass=None,
                      system_disk=None, charge=None, vpc=None,):
        params = {}
        params.setdefault("application_id", default=None)
        params.setdefault("middleware", default=None)
        params.setdefault("env", default="TEST")
        params.setdefault("number", default=1)
        params.setdefault("owner", default="ECR")
        params.setdefault("region_id", default=region)
        params.setdefault("zone_id", default=zone)
        params.setdefault("image_id", default=image)
        params.setdefault("instance_type", default=instance_type)
        params.setdefault("security_group_id", default=secure_group)
        params.setdefault("vs_switch_id", default=vpc.vswitch)
        params.setdefault("instance_charge_type", default=charge.type)
        params.setdefault("system_disk_category", default=system_disk.category)
        params.setdefault("system_disk_size", default=system_disk.size)
        if db_pass:
            userdata = self.get_password_template(db_pass)
            params.setdefault("UserData", default=userdata)

        domain = "http://admin-job-api.lenovopcsd.com"
        url = domain + "/v1/components/ali/instances"
        data = jsonutils.dumps(params)
        request = requests.post(url, data)
        print(request.json())

    def get_password_template(self, password):
        password = password
        path = "/etc/redis.conf"
        pass_input_str = "requirepass {}".format(password)
        template_str = '''#!/bin/sh
        sudo chmod 644 {1}
        echo "{0}" >> {1}
        sudo systemctl restart redis'''.format(pass_input_str, path)
        return base64.b64encode(template_str)
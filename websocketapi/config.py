from oslo_config import cfg
CONF = cfg.CONF

api_opts = [
    cfg.StrOpt('host_ip',
               default='0.0.0.0',
               help='binding host ip. '),
    cfg.IntOpt('port',
               default=9000,
               help='binding host port. '),
    cfg.IntOpt('works',
               default=4,
               help='binding host port. ')




]
CONF.register_opts(api_opts,group='api')

rtmp_opts = [
    cfg.StrOpt('hostname',
               default='10.111.83.25',
               help='rtmp server host. '),
    cfg.IntOpt('port',
               default=31935,
               help='rtmp server port. ')
]
CONF.register_opts(rtmp_opts,group='rtmp')

log_opts = [
    cfg.StrOpt('file',
               default='/var/log/websocketapi.log',
               help='rtmp server host. '),
    cfg.StrOpt('level',
               default='debug',
               help='rtmp server port. ')
]
CONF.register_opts(log_opts,group='log')


device_mapping_opts = [
    cfg.StrOpt('server_name',
               help='The name of the device_mapping service in the k8s',
               default='devicemapping'),
cfg.StrOpt('version',
               help='The version of the device_mapping api',
               default='v1'),
    cfg.IntOpt('port', help='devicemapping api port',
               default='8889'
               ),
    
]
device_mapping_group = cfg.OptGroup(name='device_mapping')

CONF.register_group(device_mapping_group)

CONF.register_opts(device_mapping_opts,group=device_mapping_group)


def parse_args(argv,default_config_files=None):
    cfg.CONF(args=argv[1:],
             project='websocketapi',
             validate_default_values = True,
             default_config_files=default_config_files)


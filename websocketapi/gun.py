import os
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

debug = True
loglevel = 'debug'
bind = '0.0.0.0:9000'
pidfile='/var/log/gunicorn/scrumpid.log'
errorlog='/var/log/gunicorn/error.log'
accesslog='/var/log/gunicorn/access.log'

# processing num
workers = 2
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

x_forwarded_for_header = 'X-FORWARDED-FOR'


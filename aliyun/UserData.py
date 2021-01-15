#!/usr/bin/env python
#coding=utf-8
import base64


ustr = '''
#!/bin/sh\n
echo "Hello World. The time is now $(date -R)!" | tee /usr/local/output.txt
'''
print ustr
print base64.b64encode(ustr)

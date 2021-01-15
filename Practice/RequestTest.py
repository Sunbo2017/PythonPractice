import requests
import json

url = 'http://39.106.87.219:29300/v1/redis/ping'
user = 'KtnHY7x9JRJvAbpr'
pwd = 'doIfkjzqWUuipQp3'
r = requests.get(url=url, auth=(user, pwd), timeout=5)
print r
print r.text
result = json.loads(r.text)
print type(result)
print result['result']

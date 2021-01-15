#coding=utf-8

import os

repo = r"D:\GoProject\src\xclarity-restapi"
since = "2019-07-01"
until = "2019-08-01"
NAME_LOG = r' git -C {} log  --since={} --until={} --pretty=tformat:%ae  > {}'
GIT_LOG = r'git -C {} log --since={} --until={} --author={} --shortstat --pretty=tformat: --no-merges > {}'
authorfile = os.path.join(os.getcwd(), 'author.txt')
logfile = os.path.join(os.getcwd(), 'gitstats.txt')
name_log_command = NAME_LOG.format(repo, since, until, authorfile)
os.system(name_log_command)
names = []
with open(authorfile, 'r', encoding='utf-8') as logfilehandler:
    names = logfilehandler.readlines()
distict_names = list(set(names))
for name in distict_names:
    name = name.strip().replace(' ', '').replace(r'\n', '').replace(r'\t', '').replace(r'\r', '').strip()
    print(name)
    git_log_command = GIT_LOG.format(repo, since, until, name, logfile)
    os.system(git_log_command)
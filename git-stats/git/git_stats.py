#coding=utf-8

'''Analyse git branch commit log, for every version, every person.'''
import os
import sys

GIT_LOG = r'''git -C {} log  --since={} --until={} --format='%ae' | sort -u | while read name;
 do echo -en "$name,"; git log --since={} --until={} --author="$name" --numstat --pretty=tformat:
 --no-merges | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines, %s, removed lines, %s, 
 total lines, %s\n", add, subs, loc }' -; done >> {}'''

CSV_FILE_HEADER = ["User", "Since", "Until", "Project", "Added", "Remove", "Total"]

def exec_git(repo, since, until, logfile):
    '''Execute git log commant, save csv.'''
    git_log_command = GIT_LOG.format(repo, since, until, since, until, logfile)
    os.system(git_log_command)

if __name__ == "__main__":
    print('gitstats begin')
    if len(sys.argv) != 5:
        print('Invalid argv parameters.')
        exit(0)

    REPO = os.path.join(os.getcwd(), sys.argv[1])
    SINCE = sys.argv[2]
    UNTIL = sys.argv[3]
    CSV_FILE = os.path.join(os.getcwd(), sys.argv[4])
    LINES = exec_git(REPO, SINCE, UNTIL, CSV_FILE)
    print('gitstats done')
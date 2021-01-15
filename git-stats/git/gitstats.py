# coding=utf-8

'''Analyse git branch commit log, for every version, every person.'''
import os
import sys
import re
import csv
import datetime

GIT_LOG = r'git -C {} log --since={} --until={} --author={} --shortstat --pretty=tformat: --no-merges > {}'
NAME_LOG = r' git -C {} log  --since={} --until={} --pretty=tformat:%ae > {}'

REPATTERN_FULL = r"\s(\d+)\D+(\d+)\D+(\d+)\D+\n"
REPATTERN_INSERT_ONLY = r"\s(\d+)\D+(\d+)\sinsertion\D+\n"
REPATTERN_DELETE_ONLY = r"\s(\d+)\D+(\d+)\sdeletion\D+\n"

CSV_FILE_HEADER = ("Author", "Week", "Since", "Until", "Project", "Commit", "Insert", "Delete", "Total")

def exec_git(repo, since, until):
    '''Execute git log commant, return string array.'''
    logfile = os.path.join(os.getcwd(), 'gitstats.txt')
    authorfile = os.path.join(os.getcwd(), 'author.txt')
    name_log_command = NAME_LOG.format(repo, since, until, authorfile)
    os.system(name_log_command)
    with open(authorfile, 'r', encoding='utf-8') as namehandler:
        names = namehandler.readlines()
    distict_names = list(set(names))
    stats = {}
    for name in distict_names:
        name = name.strip().replace(' ', '').replace(r'\n', '').replace(r'\t', '').replace(r'\r', '').strip()
        git_log_command = GIT_LOG.format(repo, since, until, name, logfile)
        os.system(git_log_command)
        with open(logfile, 'r', encoding='utf-8') as logfilehandler:
            lines = logfilehandler.readlines()
            stat = parse_line(lines)
        stats[name] = stat
    return stats

def save_csv(stats, week, since, until, project, csvfile):
    '''save stats data to csv file.'''
    with open(csvfile, 'a+', encoding='utf-8', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        for author, stat in stats.items():
            writer.writerow([author, week, since, until, project, stat[0], stat[1], stat[2], stat[3]])

def parse_line(lines):
    '''Analyse git log and sort to csv file.'''
    prog_full = re.compile(REPATTERN_FULL)
    prog_insert_only = re.compile(REPATTERN_INSERT_ONLY)
    prog_delete_only = re.compile(REPATTERN_DELETE_ONLY)
    stat = [0, 0, 0, 0]
    for line in lines:
        insert, delete = int(0), int(0)
        result = prog_full.search(line)
        if result:
            insert = int(result.group(2))
            delete = int(result.group(3))
        else:
            result = prog_insert_only.search(line)
            if result:
                insert = int(result.group(2))
                delete = int(0)
            else:
                result = prog_delete_only.search(line)
                if result:
                    insert = int(0)
                    delete = int(result.group(2))
                else:
                    print('Regular expression fail!')
                    return
        loc = insert - delete
        stat[0] += 1
        stat[1] += insert
        stat[2] += delete
        stat[3] += loc
    return stat

def get_weeks():
    current = datetime.datetime.now()
    start = datetime.date(current.year, 1, 1)
    last_day = datetime.date(current.year, current.month, current.day)
    # last_day = datetime.date(current.year, 8, 1)
    isfirst = start.weekday()
    last_week = last_day.strftime('%W')
    weeks = {}
    if isfirst != 0:
        end = datetime.timedelta(7 - start.weekday() - 1)
        weeks[0] = [start, start + end]
    start += datetime.timedelta(7 - start.weekday())

    for i in range(0, int(last_week)):
        days = datetime.timedelta(weeks=i)
        end = start + days  # 每周的开始时间
        if i + 1 == int(last_week):
            weeks[i + 1] = [end, last_day]
        else:
            weeks[i + 1] = [end, end + datetime.timedelta(6)]
    return weeks

def run(path, csv_file):
    with open(csv_file, 'w', encoding='utf-8', newline="") as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        writer.writerow(CSV_FILE_HEADER)
    weeks = get_weeks()
    for i, week in weeks.items():
        since = week[0].strftime('%Y-%m-%d')
        until = week[1].strftime('%Y-%m-%d')
        STATS = exec_git(path, since, until)
        save_csv(STATS, i+1, since, until, os.path.basename(path), csv_file)


if __name__ == "__main__":
    print('gitstats begin')
    if len(sys.argv) != 3:
        print('Invalid argv parameters.')
        exit(0)
    REPO = os.path.join(os.getcwd(), sys.argv[1])
    CSV_FILE = os.path.join(os.getcwd(), sys.argv[2])
    run(REPO, CSV_FILE)
    print('gitstats done')
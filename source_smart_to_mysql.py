from multiprocessing import Pool
import time
import pymysql

host = '10.121.11.85'
port = 3306
user = 'root'
pwd = ''
smart_db = 'btit_disk_smart_data'


def db_connect():
    conn = pymysql.connect(host, user, pwd, smart_db)
    cursor = conn.cursor()
    return cursor


def source_smart(file_name):
    print('start source {}'.format(file_name))
    conn = pymysql.connect(host, user, pwd, smart_db)
    cursor = conn.cursor()
    try:
        with open(file_name) as f:
            for line in f:
                # 执行sql语句
                print(line)
                cursor.execute(line)
            # 提交到数据库执行
            conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
    print('source: {} successful'.format(file_name))


if __name__ == '__main__':
    print('start source............')
    start = time.time()
    pool = Pool()
    for i in range(1, 18):
        pool.apply_async(source_smart, ('smart_a{}'.format(i),))

    pool.close()
    pool.join()
    end = time.time()
    # 100w 条数据用时109秒 -> 一亿条大概200分钟
    print('time cost:{} minutes'.format((end-start)/60))

import pymysql
import pymongo
import time


def user_to_mongo():
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM users')
    data_list = []
    for row in cursor.fetchall():
        data = {
            'username': row[0],
            'password': row[1],
            'create_time': row[2],
            'enable': True,
            'email': '',
            'role': ''
        }
        data_list.append(data)
    mongo.users.insert_many(data_list)
    cursor.close()


def ffdcfile_to_mongo():
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM ffdcfile')
    data_list = []
    for row in cursor.fetchall():
        data = {
            'ffdc_id': row[0],
            'name': row[2],
            'upload_user': row[3],
            'upload_time': row[4],
            'status': '',
            'analyze_total_time': None,
            'result': row[6],
            'size': None,
            'label_status': row[7],
            'analyze_start_time': None,
            'analyze_finish_time': None,
            'md5': ''
        }
        data_list.append(data)
    mongo.ffdcfile.insert_many(data_list)
    cursor.close()


def labelinfo_to_mongo():
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM flaginfo')
    data_list = []
    for row in cursor.fetchall():
        data = {
            'label_username': row[0],
            'ffdc_id': '',
            'ffdc_source': row[2],
            'normal': row[3],
            'create_time': row[4],
            'update_time': row[5],
            'bug_id': row[6],
            'resolution': row[10],
            'resolution_other': '',
            'helpful_report_segments': row[11],
            'comments': row[12]
        }
        data_list.append(data)
    mongo.labelinfo.insert_many(data_list)
    cursor.close()


def loginfo_to_mongo():
    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM flaginfo')
    data_list = []
    for row in cursor.fetchall():
        data = {
            'label_username': row[1],
            'ffdc_id': '',
            'fault_component': row[3],
            'fault_component_other': '',
            'abnormal_logs': row[4],
            'abnormal_log_file': row[5],
            'abnormal_log_file_other': '',
            'boot_id': row[7],
            'sub_boot_id': row[9],
            'fault_boot_phase': row[10]
        }
        data_list.append(data)
    mongo.loginfo.insert_many(data_list)
    cursor.close()


if __name__ == '__main__':
    # connect to mysql database
    mysql = pymysql.connect(host='127.0.0.1', database='database', user='username', password='password')

    # connect to mongodb and obtain total lines in mysql
    mongo = pymongo.MongoClient('mongodb://ip').default
    mongo.authenticate('username', password='password')

    start_time = time.time()
    # select from mysql and insert into mongodb.
    user_to_mongo()
    ffdcfile_to_mongo()
    labelinfo_to_mongo()
    loginfo_to_mongo()

    end_time = time.time()
    deltatime = end_time - start_time
    totalhour = int(deltatime / 3600)
    totalminute = int((deltatime - totalhour * 3600) / 60)
    totalsecond = int(deltatime - totalhour * 3600 - totalminute * 60)
    # print(migrate data total time consuming.)
    print("Data Migrate of table_name Finished,Total Time Consuming: %d Hour %d Minute %d Seconds" % (
        totalhour, totalminute, totalsecond))
    mysql.close()

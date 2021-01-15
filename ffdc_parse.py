import os
import queue
import subprocess
import datetime
import clickhouse_driver
import xml.etree.ElementTree as ET

q = queue.Queue()


def download_tzz():
    today = datetime.date.today()
    formatted_today = today.strftime('%Y-%m-%d')
    # formatted_today = '2020-08-20'
    url = 'http://10.121.9.138/files/' + formatted_today + '/'
    # 1.wget to /data/files/<today>/
    retcode = subprocess.call("wget -P /data/ -r --no-parent  --reject='index.html*' -nH {}".format(url), shell=True)
    print('wget result code:{}'.format(retcode))
    return formatted_today


def parse_tzz(file_today):
    ch_client = get_click_house()
    file_path = '/data/files/' + file_today
    for parent, dirnames, filenames in os.walk(file_path, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            print('File path：%s\n' % file_path)
            q.put(file_path)

    while not q.empty():
        file = q.get()
        # FFDC_UUID
        file_name = file.split('/')[-1][0:-4]
        print('start parse {}'.format(file_name))

        # create dir /data/result/<today>/
        date_dir = '/data/result/{}'.format(file_today)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        # /data/result/<today>/<FFDC_UUID>
        result_path = "{}/{}".format(date_dir, file_name)
        # 2.parse ffdc
        retcode = subprocess.call("/opt/ffdc/ffdc_parser.pl {} -o {}/".format(file, result_path), shell=True)
        print('parse ffdc result code:{}'.format(retcode))

        # 3.run lure2
        retcode = subprocess.call("/opt/lure2/lure2 scan --logFile {}".format(result_path), shell=True)
        print('run lure2 result code:{}'.format(retcode))

        # 4.move result.xml to /data/result/<today>/<FFDC_UUID>
        retcode = subprocess.call("mv ./result.xml {}".format(result_path), shell=True)
        print('mv result.xml result code:{}'.format(retcode))

        # 5.parse result.xml
        rule_list = parse_xml('{}/result.xml'.format(result_path), file_name)
        save_results(ch_client, rule_list)


def parse_xml(xml_path, file_name):
    tree = ET.parse(xml_path)
    # root node
    root = tree.getroot()
    rules_text = root.find("RulesText")
    rule_list = []
    if rules_text:
        product_name = '{}-{}'.format(file_name.split('_')[0], file_name.split('_')[1])
        rules = rules_text.findall("RuleText")
        for rule in rules:
            rule_dict = {
                'ProductName': product_name,
                'lscRuleCategory': rule.find('lscRuleCategory').text,
                'dateOfLastFiring': rule.find('dateOfLastFiring').text,
                'lscRuleMessage': rule.find('lscRuleMessage').text,
                'messageLink': rule.find('messageLink').text,
                'lscRuleRequestNumber': rule.find('lscRuleRequestNumber').text,
                'lscSeverity': rule.find('lscSeverity').text,
                'tips': rule.find('tips').text,
                'solution': rule.find('solution').text,
                'date': datetime.date.today()
            }
            is_classified = rule.find('isClassified').text
            classified = 1
            if is_classified == 'true':
                classified = 0
            rule_dict['isClassified'] = classified
            print('rule_dict: {}'.format(rule_dict))
            rule_list.append(rule_dict)

    return rule_list


def get_click_house():
    ch_host = '10.121.221.19'
    ch_port = '9000'
    ch_db = 'ecrlab'
    ch_user = 'default'
    ch_pwd = ''
    client = clickhouse_driver.Client(host=ch_host, port=ch_port, database=ch_db, user=ch_user, password=ch_pwd)
    create_sql = '''CREATE TABLE if not exists ecrlab.lure2_result
                    (`ProductName` Nullable(String), `lscRuleCategory` Nullable(String), 
                    `dateOfLastFiring` Nullable(String), `lscRuleMessage` Nullable(String), 
                    `messageLink` Nullable(String), `isClassified` Int32, `lscRuleRequestNumber` Nullable(String), 
                    `lscSeverity` Nullable(String), `tips` Nullable(String), `solution` Nullable(String), `date` Date)
                    ENGINE = MergeTree() PARTITION BY date ORDER BY (date)
                    SETTINGS index_granularity = 8192;'''
    client.execute(create_sql)
    return client


def save_results(ch_client, rule_list):
    if rule_list:
        insert_sql = '''INSERT INTO ecrlab.lure2_result 
                        (ProductName, lscRuleCategory, dateOfLastFiring, lscRuleMessage,messageLink, 
                        isClassified, lscRuleRequestNumber, lscSeverity, tips, solution, date) 
                        VALUES'''
        ch_client.execute(insert_sql, rule_list)
        print('insert {} rows into lure2_result'.format(len(rule_list)))


if __name__ == '__main__':
    # file_dir = download_tzz()
    file_dir = 'dump'
    parse_tzz(file_dir)


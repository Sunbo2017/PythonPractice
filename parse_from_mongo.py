import pymongo
import pandas as pd
from datetime import datetime

mongodb_url = 'mongodb://localhost:27017'
smart_db = 'smart'
# smart_db = 'testPersister'
smart_collection = 'disk_smart_info'


def get_mongodb():
    mongo_client = pymongo.MongoClient(mongodb_url)
    db = mongo_client[smart_db]
    # username, password = 'sunbo', '123456'
    # db.authenticate(username, password)
    return db


def query_and_mock_data():
    db = get_mongodb()
    smart_col = db[smart_collection]
    query_body = {
        'disk_serial_number': 'SWN648LW',
        'disk_model': 'AL14SEB030N'
    }
    smart_dataset = smart_col.find(query_body)
    for data in smart_dataset:
        data['disk_serial_number'] = 'W4612ESL'
        data['disk_model'] = 'ST2000NX0253'
        # data['date'] = datetime.now()
        del data['_id']
        print('insert data: {}'.format(data))
        smart_col.insert_one(data)
        print('insert {}:{} successful...'.format(data['disk_model'], data['disk_serial_number']))


def query_and_parse_data():
    db = get_mongodb()
    smart_col = db[smart_collection]
    smart_dataset = smart_col.find()
    smart_dict = {
        'date': [],
        'serial_number': [],
        'model': [],
        'capacity_bytes': [],
        'failure': []
    }
    id_list = []
    for data in smart_dataset:
        date = data['date'].strftime("%Y/%m/%d")
        print(date)
        sn = data['disk_serial_number']
        model = data['disk_model']
        attrs = data['attrs']
        smart_dict['date'].append(date)
        smart_dict['serial_number'].append(sn)
        smart_dict['model'].append(model)
        smart_dict['capacity_bytes'].append(0)
        smart_dict['failure'].append(0)

        for attr in attrs:
            id = int(attr['Id'])
            value_key = 'smart_{}_normalized'.format(id)
            raw_key = 'smart_{}_raw'.format(id)
            value = attr['Value']
            raw = attr['RawValue'].split(' (')[0]
            if id not in id_list:
                id_list.append(id)
                smart_dict[value_key] = []
                smart_dict[raw_key] = []

            smart_dict[value_key].append(int(value))
            smart_dict[raw_key].append(int(raw))

    # print(smart_dict)
    return pd.DataFrame(smart_dict)


if __name__ == '__main__':
    # df = query_and_parse_data()
    # print(df)

    query_and_mock_data()
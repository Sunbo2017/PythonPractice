import clickhouse_driver


def connect_clickhouse(ch_host='10.121.221.14'):
    ch_port = '9000'
    ch_db = 'backblaze'
    ch_user = 'default'
    ch_pwd = ''
    client = clickhouse_driver.Client(host=ch_host, port=ch_port, database=ch_db, user=ch_user, password=ch_pwd)

    return client


def data_normalization_prepare(ch_client):
    table_info = ch_client.execute('DESCRIBE TABLE backblaze.disk_smart')
    # print(table_info)
    column_list = []
    for column in table_info:
        column_name = column[0]
        if column_name.startswith('smart'):
            # print(column_name)
            column_list.append(column_name)

    model_info = ch_client.execute('select model from backblaze.disk_smart group by model')
    # print(model_info)
    model_list = []
    for model in model_info:
        # print(model[0])
        model_list.append(model[0])

    return model_list, column_list


def create_new_normalized_table(ch_client, column_list):
    create_sql = '''CREATE TABLE IF NOT EXISTS backblaze.disk_smart_normalized 
                            (`model` String, `serial_number` String, `date` Date, `capacity_bytes` UInt64, `failure` UInt8)
                            ENGINE = MergeTree() PARTITION BY date ORDER BY (model, serial_number)
                            SETTINGS index_granularity = 8192;'''
    ch_client.execute(create_sql)
    for column in column_list:
        alter_sql = 'ALTER TABLE backblaze.disk_smart_normalized ADD COLUMN IF NOT EXISTS {} Float32'.format(
            column)
        ch_client.execute(alter_sql)


def data_normalization_api(src_ch_client, desc_ch_client, column_list):
    column_dict = {}
    num = 0
    for column in column_list:
        if column.find('normalize') > 0:
            continue
        group_sql = "select model, max({}), min({}) from backblaze.disk_smart group by model".format(column, column)
        group_val = src_ch_client.execute(group_sql)
        model_dict = {}
        for val in group_val:
            # key:model, val:tuple(model,max,min)
            model_dict[val[0]] = val
        column_dict[num] = model_dict
        num += 1
    # print(column_dict)
    offset = 10255500
    limit = 5000
    # query_sql = 'select * from backblaze.disk_smart order by date desc limit %(offset)s, %(limit)s'
    query_sql = 'select * from backblaze.disk_smart limit %(offset)s, %(limit)s'
    insert_sql = 'insert into backblaze.disk_smart_normalized values'
    while True:
        insert_raws = []
        results = src_ch_client.execute(query_sql, {'offset': offset, 'limit': limit})
        offset += 5000
        if len(results) <= 0:
            break
        for result in results:
            # result is a tuple of all fields
            date = result[0]
            serial_number = result[1]
            _model = result[2]
            capacity_bytes = result[3]
            failure = result[4]
            # new table fields order
            insert_raw = [date, serial_number, _model, capacity_bytes, failure]
            # iterate all fields except date,serial_number,model,capacity_bytes,failure
            for i in range(5, len(result)):
                if i % 2 == 0:
                    # raw
                    model_dict = column_dict[int(i / 2 - 3)]
                    max_val = model_dict[_model][1]
                    min_val = model_dict[_model][2]
                else:
                    # normalized
                    max_val = 253
                    min_val = 1

                val = result[i]
                # insert 0 if value is null or 0
                if val is None:
                    normalized_val = None
                elif max_val is None or min_val is None:
                    normalized_val = None
                elif max_val > min_val:
                    # 2 decimal places
                    normalized_val = round((val - min_val) / (max_val - min_val), 5)
                else:
                    normalized_val = 0
                insert_raw.append(normalized_val)
            insert_raws.append(insert_raw)
        # batch insert 5000 rows every time
        desc_ch_client.execute(insert_sql, insert_raws)
        print('insert batch successful {}'.format(offset))

    print('insert all successful')


if __name__ == '__main__':
    print('start data normalization')
    source_clickhouse_client = connect_clickhouse('10.121.221.14')
    model_list, column_list = data_normalization_prepare(source_clickhouse_client)

    # create table disk_smart_normalized,just need to execute once
    # create_new_normalized_table(ch_client, column_list)

    target_clickhouse_client = connect_clickhouse('10.121.221.19')
    data_normalization_api(source_clickhouse_client, target_clickhouse_client, column_list)

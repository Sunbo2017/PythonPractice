# -*- coding: utf-8 -*-
import binascii
import os
# import base64
import pymongo
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
# from kubernetes import client, config
import time
import datetime
import sys
import getopt
import uuid
import random

KEY_LENG = 16
ITERATIONS = 256000
machine_id_path = '/opt/lenovo/lxa/data/isddc/alert-manager/machine-id'
secret = 'lxco-alert-manager-secret'
ALERT_MANAGER_SECRET = "lxco-alert-manager-secret"
alert_manager_machine_id_path = "/opt/lenovo/lxa/data/isddc/alert-manager/machine-id"
mongodb_url = 'mongodb://lxco-mongo-service.default:27017'
database = 'ISDDC_DBSTORE'
events_col = 'Events'
alert_col = 'alert'


def decryptpassword(machine_id, encrypted_password, salt, iv):
    # grab the values from secret valume(which are already based64decoded once
    # it is mounted)

    # grab the machine id and hash it with PBKDF2 using the salt retrieved from
    # the secret volume
    hashedkey = binascii.hexlify(
        PBKDF2(machine_id, salt, KEY_LENG, count=ITERATIONS,
               hmac_hash_module=SHA256))
    # hashedkey = PBKDF2(machine_id, salt, KEY_LENG, count=ITERATIONS,
    # hmac_hash_module=SHA256).encode('hex')

    # decrypt the password using AES-GCM using the key plus the initialization
    # vector from the secret volume
    cipher = AES.new(hashedkey, AES.MODE_GCM, nonce=iv)
    decrypted_password = cipher.decrypt(binascii.unhexlify(encrypted_password))
    # decrypted_password = cipher.decrypt(encrypted_password.encode('hex'))
    # LOG.info("decrypted_password:{}".format(decrypted_password))

    # Finally log into mongddb with secret username and decrypted password
    return decrypted_password


def _read_from_file(file):
    with open(file) as f:
        return f.read().strip()
    return None


def get_machine_id(machine_id_path):
    return _read_from_file(machine_id_path)


def get_value(secret, file):
    path = os.path.join('/etc/', secret, file)
    # path = '/etc/' + secret + '/' + file
    if os.path.exists(path):
        return _read_from_file(path)
    else:
        return None


def get_username_and_pwd():
    encrypted_password = get_value(secret, "ISDDC_DBSTORE_password")
    mongodb_username = get_value(secret, "ISDDC_DBSTORE_username")
    salt = get_value(secret, "ISDDC_DBSTORE_salt")
    iv = get_value(secret, "ISDDC_DBSTORE_iv")
    machine_id = get_machine_id(machine_id_path)
    decrypt_password = decryptpassword(
        machine_id,
        encrypted_password.encode(encoding="utf-8"),
        salt.encode(encoding="utf-8"),
        iv.encode(encoding="utf-8"))
    return mongodb_username, decrypt_password.decode()


# def get_isddc_username_and_pwd():
#     config.load_incluster_config()
#     # config.load_kube_config()
#     alert_manager_secret = client.CoreV1Api().read_namespaced_secret(ALERT_MANAGER_SECRET, 'monitoring').data
#     mongodb_username = str(base64.b64decode(alert_manager_secret.get('ISDDC_DBSTORE_username')), 'utf-8').strip()
#     # LOG.info("username:{}".format(mongodb_username))
#     encrypted_password = str(base64.b64decode(alert_manager_secret.get('ISDDC_DBSTORE_password')), 'utf-8').strip().encode(encoding="utf-8")
#     # LOG.info("password:{}".format(encrypted_password))
#     salt = str(base64.b64decode(alert_manager_secret.get('ISDDC_DBSTORE_salt')), 'utf-8').strip().encode(encoding="utf-8")
#     # LOG.info("salt:{}".format(salt))
#     iv = str(base64.b64decode(alert_manager_secret.get('ISDDC_DBSTORE_iv')), 'utf-8').strip().encode(encoding="utf-8")
#     # LOG.info("iv:{}".format(iv))
#     alert_manager_machine_id = get_machine_id(alert_manager_machine_id_path)
#     # LOG.info("alert_manager_machine_id:{}".format(alert_manager_machine_id))
#     decrypt_password = decryptpassword(alert_manager_machine_id, encrypted_password, salt, iv).decode("utf-8")
#     # LOG.info("decrypt_password:{}".format(decrypt_password))
#     return mongodb_username, decrypt_password


def get_mongodb():
    mongo_client = pymongo.MongoClient(mongodb_url)
    db = mongo_client[database]
    username, password = get_username_and_pwd()
    print('username: {}, password: {}'.format(username, password))
    db.authenticate(username, password)
    return db


# add connectivityIssue mock data
def mock_events_data(lxca_uuid, resource_uuid, system_name, ip):
    event_body = {
        "tenant_id": "acd232fe2325lge90908fefe3a",
        "event_type": "event",
        "dimensions": {
            "sourceID": resource_uuid,
            "lxcaUUID": lxca_uuid,
            "serialnum": "",
            "eventID": "FQXHMDM0163J",
            "commonEventID": '',
            "eventClass": "Audit",
            "severity": "Informational",
            "userID": "USERID",
            "systemName": system_name,
            "systemType": "",
            "componentID": resource_uuid,
            "action": "None",
            "service": "None",
            "msgID": "IMM0153",
            "generatorType": "",
            "local": '',
            "sourceIP": ip,
            "resourceType": "Server",
            "sequenceNumber": "8645685"
        },
        "region": "xclarity_dc",
        "message": "Security: connectivity issue happened more than twice per hour in 4 hours in a row",
        "message_meta": {"args": ["USERID", "192.168.100.3"], "_id": ""},
        "sourceID": resource_uuid,
        "severity": "Warning",
        "eventID": "FQXHMDM0163J",
        "systemName": system_name,
        "ipAddress": ip
    }
    collection = get_mongodb()[events_col]
    now = int(time.time())
    # data for 3 day
    for i in range(random.randint(0, 10)):
        timestamp = now - i * 8 * 3600
        event_body['_id'] = uuid.uuid1()
        event_body['timestamp'] = timestamp * 1000
        collection.insert_one(event_body)
    # data for 2 month
    for i in range(1, random.randint(2, 5)):
        timestamp = now - i * 24 * 16 * 3600
        event_body['_id'] = uuid.uuid1()
        event_body['timestamp'] = timestamp * 1000
        collection.insert_one(event_body)

    print('mock connectivity issue data successful')


# add connectivityIssue mock data
def mock_alert_data(lxca_uuid, resource_uuid, system_name, ip):
    alert_body = {
        "alert_id": "FQXXOIS0002J:AC60E8DD4833D362A99FA89BD52E4514",
        "lxca_uuid": lxca_uuid,
        "manager_uuid": lxca_uuid,
        "event_id": "FQXXOIS0002J",
        "alarm_name": "repeatedSameEvents",
        "alarm_uuid": "1fe41cc0-c2bc-468e-91f4-f35a453a5bfb",
        "severity": "Warning",
        "alert_description": "repeated events happened in 3 5-minutes in a row",
        # "create_time": ISODate("2020-11-24T13:40:13.000Z"),
        "event_type": "alert",
        "reserved": True,
        "resource_uuid": resource_uuid,
        "resource_type": "device",
        "ip": ip,
        "system_name": system_name
    }

    collection = get_mongodb()[alert_col]
    now = datetime.datetime.utcnow()
    # repeated events data for 3 day
    for i in range(random.randint(0, 10)):
        timestamp = now - datetime.timedelta(hours=i * 8)
        alert_body['_id'] = uuid.uuid1()
        alert_body['create_time'] = timestamp
        collection.insert_one(alert_body)
    # repeated events data for 2 month
    for i in range(1, random.randint(2, 5)):
        timestamp = now - datetime.timedelta(i * 15)
        alert_body['_id'] = uuid.uuid1()
        alert_body['create_time'] = timestamp
        collection.insert_one(alert_body)

    print('mock repeated events data successful')

    alert_body['event_id'] = 'FQXXOIS0006J'
    # lost events data for 3 day
    for i in range(random.randint(0, 10)):
        timestamp = now - datetime.timedelta(hours=i * 8)
        alert_body['_id'] = uuid.uuid1()
        alert_body['create_time'] = timestamp
        alert_body['value'] = (i + 1) % 3 + 1
        collection.insert_one(alert_body)
    # lost events data for 2 month
    for i in range(1, random.randint(2, 5)):
        timestamp = now - datetime.timedelta(i * 15)
        alert_body['_id'] = uuid.uuid1()
        alert_body['create_time'] = timestamp
        alert_body['value'] = (i + 1) % 3 + 1
        collection.insert_one(alert_body)

    print('mock lost events data successful')


def main(argv):
    lxca_uuid = ''
    resource_uuid = ''
    system_name = ''
    ip = ''
    try:
        opts, args = getopt.getopt(argv, "hl:r:n:i:", ["lxca_uuid=", "resource_uuid=", "system_name=", "ip="])
    except getopt.GetoptError:
        print('add_mock_data.py -l <lxca_uuid> -r <resource_uuid> -n <system_name> -i <ip>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('add_mock_data.py -l <lxca_uuid> -r <resource_uuid> -n <system_name> -i <ip>')
            sys.exit()
        elif opt in ("-l", "--lxca_uuid"):
            lxca_uuid = arg
            print('lxca_uuid: {}'.format(lxca_uuid))
        elif opt in ("-r", "--resource_uuid"):
            resource_uuid = arg
            print('resource_uuid: {}'.format(resource_uuid))
        elif opt in ("-n", "--system_name"):
            system_name = arg
            print('system_name: {}'.format(system_name))
        elif opt in ("-i", "--ip"):
            ip = arg
            print('ip: {}'.format(ip))

    mock_events_data(lxca_uuid, resource_uuid, system_name, ip)
    mock_alert_data(lxca_uuid, resource_uuid, system_name, ip)


if __name__ == '__main__':
    main(sys.argv[1:])

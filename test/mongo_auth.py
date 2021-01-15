import base64
import os
import binascii
import pymongo
from bson.objectid import ObjectId
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

ITERATIONS = 256000
KEY_LENG = 16


def mongodb_auth():
    username = 'sunbo'
    password = '123456'
    url = 'mongodb://localhost:27017'
    mongo_client = pymongo.MongoClient(url)
    address = url.split('//')[1]
    host = address.split(':')[0]
    port = address.split(':')[1]
    print(address)
    print(host)
    print(port)
    db = mongo_client['testPersister']
    db.authenticate(username, password)

    collection = db['events']
    myset = set([1, 2, 3, 4, 5, 6])
    myset = list(myset)
    collection.insert_one({'name': 'test-insert', 'set': myset})
    cursor = collection.find()
    for document in cursor:
        print(document)
    result = collection.find_one({'_id': ObjectId('5db682a995cf3a1606ca8f04')})
    if result:
        print('true')
    print(result)


def encrypt_pwd(machine_id, password):
    machine_id = '2970ac54dddf7af7ce21a1265db6a8d1'
    secret = {}
    secret['password'] = binascii.hexlify(password.encode(encoding="utf-8"))

    # generate 32 random bytes salt
    # secret['salt'] = binascii.hexlify(get_random_bytes(32))
    secret['salt'] = '3e25f75f28341a2878024cc94ee410916c293fe9bd470045c70e8053e42ac5ae'.encode()

    # Generate a random 256 bit initialization vector.
    # secret['iv'] = binascii.hexlify(get_random_bytes(32))
    secret['iv'] = '9599360953dd415f4a3d7b2ff52af08aa99fe77a1420410121baecad40921ff8'.encode()

    # create a 256 bit key using machine id and the salt, hash it using PBKDF2
    hashedkey = binascii.hexlify(
        PBKDF2(machine_id, secret['salt'], KEY_LENG, count=ITERATIONS, hmac_hash_module=SHA256))
    print('hashkey is :', hashedkey)

    # create a cipher using hashed key
    cipher = AES.new(hashedkey, AES.MODE_GCM, nonce=secret['iv'])

    # encrypt the password with the generated 256 bit key
    # secret['encryptedpassword'] = binascii.hexlify(cipher.encrypt(secret['password']))
    en_pwd, digest = cipher.encrypt_and_digest(secret['password'])
    print(binascii.hexlify(en_pwd), binascii.hexlify(digest))
    # {'password': b'313233343536', 'salt': b'1938d68d601ee2c07bc083dd5c6b42dee20a5f4ac316b118e1037d08630e8955',
    # 'iv': b'2aca7800f8e1dd28da22a373182e4a6952d60d29eebdf1961cb646c049502172',
    # 'encryptedpassword': b'f13a5ef7677c5e4b5fdf95a0'}
    tag = binascii.hexlify(cipher.digest())
    print(secret)
    # print(secret['encryptedpassword'], tag)
    return secret


def decrypt_pwd(machine_id, encrypted_password, salt, iv):
    # grab the values from secret valume(which are already based64decoded once it is mounted)

    # grab the machine id and hash it with PBKDF2 using the salt retrieved from the secret volume
    pbkdf = PBKDF2(machine_id, salt, KEY_LENG, count=ITERATIONS, hmac_hash_module=SHA256)
    hashedkey = binascii.hexlify(PBKDF2(machine_id, salt, KEY_LENG, count=ITERATIONS, hmac_hash_module=SHA256))
    print('hashkey is: %s' % hashedkey)
    # decrypt the password using AES-GCM using the key plus the initialization vector from the secret volume
    cipher = AES.new(hashedkey, AES.MODE_GCM, nonce=iv)

    decrpted_password = cipher.decrypt(binascii.unhexlify(encrypted_password))

    # Finally log into mongddb with secret username and decrypted password
    return decrpted_password


def test_pwd():
    pwd = '123456'
    salt = '3e25f75f28341a2878024cc94ee410916c293fe9bd470045c70e8053e42ac5ae'
    print('byte slat is: ', salt.encode(encoding='utf-8'))
    iv = '9599360953dd415f4a3d7b2ff52af08aa99fe77a1420410121baecad40921ff8'
    en_pwd = '5f202f377e53833b59b8ca832e7b5b629476feca804780d1bf633e11'
    machine_id = '2970ac54dddf7af7ce21a1265db6a8d1'
    secret = encrypt_pwd(machine_id, pwd)
    hex_pwd = decrypt_pwd(machine_id,
                          en_pwd.encode(),
                          salt.encode(),
                          iv.encode())
    print(hex_pwd)
    byte_pwd = binascii.unhexlify(hex_pwd)
    print(byte_pwd)
    str_pwd = byte_pwd.decode()
    print(str_pwd)

# test_pwd()
mongodb_auth()
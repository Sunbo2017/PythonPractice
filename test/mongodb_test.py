import pymongo

mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
db = mongo_client['testPersister']
db.authenticate('sunbo', '123456')
collection = db['Events']
event = collection.find({'$and': [{'sourceID': '20E75A0C7E7411E898C30894EF66E08C'}, {'$or': [{'systemName': ''}, {'ipAddress': ''}]}]})
print(event)
# collection.update_many({'$and': [{'sourceID': '20E75A0C7E7411E898C30894EF66E08C'}, {'$or': [{'systemName': ''}, {'ipAddress': ''}]}]},
#                        {'$set': {'systemName': 'name1', 'ipAddress': '192.168.99.100'}})

ips = ['10.121.4.36', '192.168.99.100']
results = collection.delete_many({'ipAddress': {'$in': ips}})
for result in results:
    print(result['ipAddress'])

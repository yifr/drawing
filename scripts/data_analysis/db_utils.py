import pymongo
import certs # Local file containing certificates.
import json

DATABASE = 'laps'
UNAME = certs.mongo_uname
PASSWORD = certs.mongo_pwd

def open_connection():
    conn_str = "mongodb+srv://%s:%s@cluster0.aqpv0.mongodb.net/%s?retryWrites=true&w=majority" % (UNAME, PASSWORD, DATABASE)
    client = pymongo.MongoClient(conn_str)
    db = client[DATABASE]
    return db

def all_experiment_records(experiment_id):
    db = open_connection()
    collection = db[experiment_id]
    for record in collection.find({}):
        yield record

def record_exists(collection, data):
    user_id = data['metadata']['user_id']
    result = collection.find_one({'metadata.user_id': user_id})
    if not result:
        return False

    if result['metadata'].get('completed'):
        return True

def record(data):
    experiment_id = data['metadata']['experiment_id']
    user_id = data['metadata']['user_id']
    print(user_id)
    if user_id == 'admin':
        experiment_id = 'test'

    db = open_connection()
    collection = db[experiment_id]

    if record_exists(collection, data):
        return {'success': False, 'message': 'User already completed experiment'}

    result = collection.replace_one({'metadata.user_id': user_id}, data, upsert=True)

    print(result)

    if result:
        return {'success': True, 'message': 'Successfully updated record'}
    else:
        return {'sucess': False, 'message': 'Error updating record'}

def update_record(user_id, experiment_id, data):
    db = open_connection()
    collection = db[experiment_id]
    query = {'metadata.user_id': user_id}
    update = {'$set': data}
    result = collection.update_one(query, update)
    
    print(result)

    if result:
        return {'success': True, 'message': 'Successfully updated record'}
    else:
        return {'sucess': False, 'message': 'Error updating record'}

def get_record(user_id, experiment_id):
    db = open_connection()
    collection = db[experiment_id]
    res = collection.find_one({'metadata.user_id': user_id})
    return res

if __name__=='__main__':
    data = {"metadata":{"experiment_id":"TIAN_REPLICATION_0","group_type":"vertical","session_id":None,"study_id":None,"user_id":"admin"},"phases":["train","test"],"test":{"images":["S12_13_test_1.png","S12_13_test_2.png","S12_13_test_4.png","S12_13_test_5.png","S12_13_test_6.png","S12_13_test_7.png","S12_13_test_8.png","S12_13_test_9.png","S12_13_test_10.png","S12_13_test_11.png","S12_13_test_12.png"],"ui_components":["images","draw"]},"train":{"images":["S12_20.png","S12_39.png","S12_57.png","S12_79.png","S12_113.png","S12_124.png","S12_126.png","S12_133.png","S12_147.png","S12_155.png","S12_163.png","S12_200.png","S12_214.png"],"ui_components":["images","draw"],"strokes":[None],"user_descriptions":[""]}}
    record(data)

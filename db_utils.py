import pymongo
import certs
import json

DATABASE = 'laps'
UNAME = certs.mongo_uname
PASSWORD = certs.mongo_pwd  

def open_connection():
    conn_str = "mongodb+srv://%s:%s@cluster0.aqpv0.mongodb.net/%s?retryWrites=true&w=majority" % (UNAME, PASSWORD, DATABASE)
    client = pymongo.MongoClient(conn_str)
    db = client[DATABASE]
    return db

def record_exists(collection, data):
    user_id = data['meta']['prolific_pid']
    result = collection.find_one({'user_id', user_id})
    if not result:
        return False

    if result['meta']['experiment_completed']:
        return True

def record(data):
    experiment_id = data['meta']['experiment_id']
    user_id = data['meta']['user_id']
    db = open_connection()
    collection = db[experiment_id]

    with open('data_record.txt', 'w') as f:
        f.write(experiment_id)
        f.write(user_id)
        f.write(str(record_exists(collection, data)))
        f.write(str(collection))

    if record_exists(collection, data):
        return {'success': False, 'message': 'User already completed experiment'}

    result = collection.replace_one({'user_id', user_id}, data, upsert=True)
    if result:
        return {'success': True, 'message': 'Successfully updated record'}
    else:
        return {'sucess': False, 'message': 'Error updating record: ' + result}



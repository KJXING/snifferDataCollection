import pymongo
import json
import asyncio
import zmq
from zmq.asyncio import Context

my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_db_sniffer_data = my_client["snifferdata"]
my_col_raw_data = my_db_sniffer_data["rawdata"]
my_col_fingerprint_record = my_db_sniffer_data["fingerprintrecord"]
my_col_recordwithlable = my_db_sniffer_data["recordwithlable"]
my_col_virtual_sniffer_data_collection = my_db_sniffer_data["virtual_sniffer_data_collection"]


def storageDataToMongodb(collection, mac_address, json_data):
    if collection == "my_col_fingerprint_record":
        json_pkt = {
            "timestamp": json_data[0],
            "macAddress": mac_address,
            "pi1614df": json_data[1],
            "pi80331a": json_data[2],
            "pi999999": json_data[3]
        }
        my_col_fingerprint_record.insert_one(json_pkt)
    elif collection == "my_col_raw_data":
        my_col_raw_data.insert_one(json_data)
    elif collection == "recordwithlable":
        print(json_data)
        my_col_recordwithlable.insert_one(json_data)
    elif collection == "virtual_sniffer_data_collection":
        print(json_data)
        my_col_virtual_sniffer_data_collection.insert_one(json_data)

    # logging.info("insert successfully")
    # print(collection, "insert successfully")


async def processData():
    # i = 0
    # time_period = 0
    # start_time = datetime.now().timestamp() * 1000
    while True:
        msg = await s.recv_json()
        msgObj = json.loads(msg)

        storageJson = {
            'timestamp': msgObj['timestamp'],
            'macAddress': msgObj['macAddress'],
            'pi1614df': msgObj['pi1614df'],
            'pi80331a': msgObj['pi80331a'],
            'pi999999': msgObj['pi999999'],
            'pi5dd8a2': msgObj['pi5dd8a2'],
            'pi49772a': msgObj['pi49772a'],
            'xPosition': 7,
            'yPosition': 7,
        }
        storageDataToMongodb("virtual_sniffer_data_collection", msgObj['macAddress'], storageJson)


if __name__ == '__main__':
    all_device = {}
    ctx = Context.instance()
    s = ctx.socket(zmq.SUB)
    s.connect('tcp://127.0.0.1:5555')
    s.subscribe(b'')

    asyncio.get_event_loop().run_until_complete(processData())
    asyncio.get_event_loop().run_forever()

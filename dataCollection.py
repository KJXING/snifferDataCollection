import concurrent.futures
from datetime import datetime
import dataParser as func
import dataStorage
import socket
import logging
import queue
import threading
import time
import json
import zmq



def receiver(queue, event):
    """Pretend we're getting a number from the network."""
    print("running")
    while not event.is_set():
        data, addr = sock.recvfrom(1024)
        mac_address = func.getMacAddress(data)
        if "00:00:00" not in mac_address:
            radioInfo_raw = {
                'timestamp': datetime.now().timestamp() * 1000,
                'macAddress': mac_address,
                'RSSI': func.readInt8(data[20:21]),
                'ChannelFreq': func.readUInt16LE(data, 22),
                'snifferDeviceMac': func.formatMac(data.hex()[4:16]),
                'frameControl': func.BitArray(data[24:25]).bin
            }
            queue.put(radioInfo_raw)
        logging.info("Producer got message: %s", radioInfo_raw)

    logging.info("Producer received event. Exiting")


def processingData(queue, queue_position, event):
    """Pretend we're saving a number in the database."""
    start_time = datetime.now().timestamp() * 1000
    while not event.is_set() or not queue.empty():
        message = queue.get()

        # if message['macAddress'] not in all_devices.keys():
        #     all_devices.setdefault(message['macAddress'], [])
        #     all_devices[message['macAddress']].append(message['timestamp'])
        #     if message['snifferDeviceMac'] == sniffer_device['pi1614df']:
        #         all_devices[message['macAddress']].append(message['RSSI'])
        #         all_devices[message['macAddress']].append(0)
        #         all_devices[message['macAddress']].append(0)
        #     elif message['snifferDeviceMac'] == sniffer_device['pi80331a']:
        #         all_devices[message['macAddress']].append(0)
        #         all_devices[message['macAddress']].append(message['RSSI'])
        #         all_devices[message['macAddress']].append(0)
        #     elif message['snifferDeviceMac'] == sniffer_device['pi999999']:
        #         all_devices[message['macAddress']].append(0)
        #         all_devices[message['macAddress']].append(0)
        #         all_devices[message['macAddress']].append(message['RSSI'])
        # else:
        #     all_devices[message['macAddress']][0] = message['timestamp']
        #     if message['snifferDeviceMac'] == sniffer_device['pi1614df']:
        #         # print(message['snifferDeviceMac'], "pi1", all_devices[message['macAddress']])
        #         all_devices[message['macAddress']][1] = message['RSSI']
        #     elif message['snifferDeviceMac'] == sniffer_device['pi80331a']:
        #         all_devices[message['macAddress']][2] = message['RSSI']
        #         # print(message['snifferDeviceMac'], "pi2", all_devices[message['macAddress']])
        #     elif message['snifferDeviceMac'] == sniffer_device['pi999999']:
        #         all_devices[message['macAddress']][3] = message['RSSI']
        #         # print(message['snifferDeviceMac'], "pi3", all_devices[message['macAddress']])
        # if 0 not in all_devices[message['macAddress']]:
        #     list_length = len(all_devices)
        #     devices_info = {
        #         "timestamp": all_devices[message['macAddress']][0],
        #         "macAddress": message['macAddress'],
        #         "pi1614df": all_devices[message['macAddress']][1],
        #         "pi80331a": all_devices[message['macAddress']][2],
        #         "pi999999": all_devices[message['macAddress']][3],
        #     }
        #     queue_position.put(devices_info)
        #     all_devices.pop(message['macAddress'], None)
        #
        # time_period = datetime.now().timestamp() * 1000 - start_time
        # if time_period > 50:
        #     all_devices.clear()
        #     start_time = datetime.now().timestamp() * 1000

        logging.info(
            "Consumer storing message: (size=%d) %s", queue.qsize(), message
        )

    logging.info("Consumer received event. Exiting")


def positioning(queue, event):
    while not event.is_set() or not queue.empty():
        message = queue.get()
        print(message)

        socketZmq.send_json(json.dumps(message))
        print("send")

    logging.info("Positioning event. Existing")


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', 7774)
    sock.bind(server_address)
    context = zmq.Context()
    socketZmq = context.socket(zmq.PUB)
    socketZmq.bind("tcp://*:5555")
    sniffer_device = {
        'pi1614df': '7C:DD:90:EB:F0:B1',
        'pi80331a': '7C:DD:90:EB:F0:39',
        'pi999999': '7C:DD:90:EB:F0:67'
    }


    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    all_devices = {}
    pipeline = queue.Queue(maxsize=30)
    pipeline_position = queue.Queue(maxsize=20)
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(receiver, pipeline, event)
        executor.submit(processingData, pipeline, pipeline_position, event)
        executor.submit(positioning, pipeline_position, event)

        time.sleep(0.1)
        logging.info("Main: about to set event")
        # event.set()

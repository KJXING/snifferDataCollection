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
# import zmq



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
        # logging.info("Producer got message: %s", radioInfo_raw)

    logging.info("Producer received event. Exiting")


def processingData(queue, queue_position, event):
    """Pretend we're saving a number in the database."""
    windows_size_array = []
    # start_time = datetime.now().timestamp() * 1000
    while not event.is_set() or not queue.empty():
        message = queue.get()
        windows_size_array.append(message)

        if message['timestamp'] - windows_size_array[0]['timestamp'] > 50:
            windows_size_array.pop(0)

        fusion_matrix_list = fusion_sniffers_data(windows_size_array)

        print(fusion_matrix_list)

        logging.info(
            "Consumer storing message: (size=%d) %s", queue.qsize(), message
        )

    logging.info("Consumer received event. Exiting")


def positioning(queue, event):
    while not event.is_set() or not queue.empty():
        message = queue.get()
        print(message)

        # socketZmq.send_json(json.dumps(message))
        print("send")

    logging.info("Positioning event. Existing")


def fusion_sniffers_data(array):
    fusion_data_array = []
    device_list = []
    temp_dic = {}

    for item in array:
        if len(device_list) == 0:
            temp_dic["timestamp"] = item['timestamp']
            temp_dic["macAddress"] = item['macAddress']
            temp_dic[get_sniffer_hostname(item['snifferDeviceMac'])] = item['RSSI']
            device_list.append(temp_dic)
            # print("device_list:", device_list)
        else:
            for device_dic in device_list:
                if device_dic['macAddress'] == item['macAddress']:
                    temp_dic[get_sniffer_hostname(item['snifferDeviceMac'])] = item['RSSI']
                else:
                    temp_dic['timestamp'] = item['timestamp']
                    temp_dic['macAddress'] = item['macAddress']
                    temp_dic[get_sniffer_hostname(item['snifferDeviceMac'])] = item['RSSI']
                    device_list.append(temp_dic)
                    # temp_dic.clear()
        print(device_list)

    for device_dic in device_list:
        keys = device_dic.keys()
        if len(keys) == 7:
            fusion_data_array.append(device_dic)

    return fusion_data_array


def get_sniffer_hostname(interface_mac):
    global sniffer_device

    for key, value in sniffer_device.items():
        if interface_mac == value:
            return key
    return "not exist"


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', 7774)
    sock.bind(server_address)
    # context = zmq.Context()
    # socketZmq = context.socket(zmq.PUB)
    # socketZmq.bind("tcp://*:5555")
    sniffer_device = {
        'pi1614df': '7C:DD:90:EB:F0:B1',
        'pi80331a': '7C:DD:90:EB:F0:39',
        'pi999999': '7C:DD:90:EB:F0:67',
        'pi49772a': '7C:DD:90:EB:F0:59',
        'pi5dd8a2': '7C:DD:90:E1:FE:2B'
    }

    # windows_size_array = []

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

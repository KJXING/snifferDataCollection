from datetime import datetime
import socket
import time


def main():
    sniffer_node = 5
    target_devices_mac = ['84:C7:EA:29:A6:A5', 'C0:CC:F8:91:3F:43', '4C:49:E3:47:28:EA']
    sniffer_interface_mac = ['7c:dd:90:e1:fe:2b', '7c:dd:90:eb:f0:b1', '7c:dd:90:eb:f0:39', '7c:dd:90:eb:f0:67',
                             '7c:dd:90:eb:f0:59']
    sniffer_channel = ['2412']

    UDP_IP = "127.0.0.1"
    UDP_PORT = 7774
    message_head = "0200"
    snifferDeviceMac = "0200"
    message_end = "d0a6379cf3bede996c09b400"
    # MESSAGE = "0200" + "7cdd90ebf059" + "484ae9cb7ce0" + "d0a6379cf3bede996c09b400"
    MESSAGE = message_head + sniffer_interface_mac[0].replace(':', '') \
              + target_devices_mac[0].replace(':', '') + message_end

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        for target_device in target_devices_mac:
            for sniffer_interface in sniffer_interface_mac:
                MESSAGE = message_head + sniffer_interface.replace(':', '') + target_device.replace(':', '') + message_end
                sock.sendto(bytearray.fromhex(MESSAGE), (UDP_IP, UDP_PORT))
                print(datetime.now(), type(bytearray.fromhex(MESSAGE)), bytearray.fromhex(MESSAGE))
                time.sleep(0.005)
            time.sleep(0.01)


if __name__ == '__main__':
    main()

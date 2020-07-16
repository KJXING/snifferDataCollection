import socket
import time

def main():
    sniffer_node = 5
    target_devices_mac = []
    sniffer_interface_mac = ['7c:dd:90:e1:fe:2b', '7c:dd:90:e1:fe:1e', '7c:dd:90:e1:fe:3e', '7c:dd:90:e1:fe:4e', '7c:dd:90:e1:fe:6e']
    sniffer_channel = ['2412']

    UDP_IP = "127.0.0.1"
    UDP_PORT = 7774
    MESSAGE = "02007cdd90ebf059484ae9cb7ce0d0a6379cf3bede996c09b400"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
        print(MESSAGE)
        time.sleep(0.2)


if __name__ == '__main__':
    main()

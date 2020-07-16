import struct
from bitstring import BitArray


def readUInt16LE(bytes, offset):
    return ((bytes[offset] & 0xff) | (bytes[offset + 1] << 8)) << 16 >> 16


def formatMac(raw_mac):
    raw_mac = ":".join(["%s" % (raw_mac[i:i + 2]) for i in range(0, 12, 2)])
    return raw_mac.upper()


def getMacAddress(rawData):
    mac_address_temp = ''

    for x in range(16, 28):
        mac_address_temp += rawData.hex()[x]
    mac_address_temp = ":".join(["%s" % (mac_address_temp[i:i + 2]) for i in range(0, 12, 2)])

    return mac_address_temp.upper()


def getRssiValue(rawData):
    return rawData[20] - 256


def readInt8(bytes):
    if len(bytes) != 1:
        print("Wrong number of bytes (" + str(len(bytes)) + ") should be 1")
        return None
    data, = struct.unpack("<b", bytes)
    return data

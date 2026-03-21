#!/usr/bin/env python3
"""
Android 11+
ADB Wireless Debug: QR Pairing + Auto Connect (Windows stable)

Requirements:
  py -m pip install zeroconf qrcode[pil]
"""

import subprocess
import socket
import qrcode
from zeroconf import ServiceBrowser, Zeroconf

PAIR_TYPE = "_adb-tls-pairing._tcp.local."
CONNECT_TYPE = "_adb-tls-connect._tcp.local."

NAME = "debug"
PASS = "123456"

FORMAT_QR = "WIFI:T:ADB;S:%s;P:%s;;"

CMD_PAIR = "adb pair {ip}:{port} {code}"
CMD_CONNECT = "adb connect {ip}:{port}"
CMD_DEVICES = "adb devices -l"


class PairListener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if not info or not info.addresses:
            return

        ip = socket.inet_ntoa(info.addresses[0])
        print(f"\n[PAIR] {ip}:{info.port}")

        cmd = CMD_PAIR.format(ip=ip, port=info.port, code=PASS)
        subprocess.run(cmd, shell=True)

    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass


class ConnectListener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if not info or not info.addresses:
            return

        ip = socket.inet_ntoa(info.addresses[0])
        print(f"\n[CONNECT] {ip}:{info.port}")

        cmd = CMD_CONNECT.format(ip=ip, port=info.port)
        subprocess.run(cmd, shell=True)

    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass


def show_qr(text):
    qr = qrcode.QRCode(border=1)
    qr.add_data(text)
    qr.make(fit=True)
    qr.print_ascii(invert=True)


def main():
    text = FORMAT_QR % (NAME, PASS)

    print("\n=== ADB WIRELESS AUTO PAIR + CONNECT ===\n")
    show_qr(text)

    print("\nScan QR code on phone:")
    print("Settings → Developer options → Wireless debugging → Pair device with QR code\n")

    zeroconf = Zeroconf()

    ServiceBrowser(zeroconf, PAIR_TYPE, PairListener())
    ServiceBrowser(zeroconf, CONNECT_TYPE, ConnectListener())

    try:
        input("\nWaiting… (Press Enter to exit)\n\n")
    finally:
        zeroconf.close()
        subprocess.run(CMD_DEVICES, shell=True)


if __name__ == "__main__":
    main()

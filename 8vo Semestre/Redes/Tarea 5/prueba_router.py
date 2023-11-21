import sys
import socket

headers = sys.argv[1]
router_ip = sys.argv[2]
router_puerto = sys.argv[3]

socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketUDP.bind(('127.0.0.1', 8880))

with open('archivo.txt', 'r') as archivo:
    for linea in archivo:
        msg = (headers + ";" +linea.strip()).encode()
        socketUDP.sendto(msg, (router_ip, int(router_puerto)))
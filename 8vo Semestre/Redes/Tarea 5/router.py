import sys
import socket

router_IP = sys.argv[1]
router_puerto = sys.argv[2]
router_rutas = sys.argv[3]

socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketUDP.bind((router_IP, int(router_puerto)))

def parse_packet(ip_packet):
  splited_packet = ip_packet.decode().split(';')
  direccion_IP = splited_packet[0]
  puerto = int(splited_packet[1])
  msj = splited_packet[2]
  return [direccion_IP, puerto, msj]

def create_packet(parse_ip_packet):
  packet = ''
  packet += parse_ip_packet[0] + ';'
  packet += str(parse_ip_packet[1]) + ';'
  packet += parse_ip_packet[2]
  return packet

def check_routes(routes_file_name, destination_address):
  with open(routes_file_name, 'r', encoding='UTF-8') as rutas:
    reader = rutas.read()
    reader_splited = reader.split('\n')

  rutas = []
  for row in reader_splited:
    rutas.append(row.split(' '))
  
  ip = destination_address[0]
  port = destination_address[1]
  for ruta in rutas:
    if ip == ruta[0]:
      if int(ruta[1]) <= port <= int(ruta[2]):
        next_hop = (ruta[3], int(ruta[4]))
        return next_hop
  
  return None

while True:
  rcv, _ = socketUDP.recvfrom(100)
  parsed_rcv = parse_packet(rcv)
  if parsed_rcv[0] == router_IP and parsed_rcv[1] == int(router_puerto):
    print(parsed_rcv[2])
  else:
    next_hop = check_routes(router_rutas, (parsed_rcv[0], parsed_rcv[1]))
    if next_hop:
      print("Redirigiendo paquete\n" + rcv.decode() + "\ncon destino final " + parsed_rcv[0] + " " + str(parsed_rcv[1]) + " desde " + router_IP + " " + router_puerto + " hacia " + next_hop[0] + " " + str(next_hop[1]))
      socketUDP.sendto(rcv, next_hop)
    else:
      print("No hay rutas hacia " + parsed_rcv[0] + " " + str(parsed_rcv[1]) + " para paquete\n" + rcv.decode())
    
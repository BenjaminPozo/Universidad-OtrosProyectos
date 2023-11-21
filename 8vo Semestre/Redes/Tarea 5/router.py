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
  ttl = int(splited_packet[2])
  msj = splited_packet[3]
  return [direccion_IP, puerto, ttl, msj]

def create_packet(parse_ip_packet):
  packet = ''
  packet += parse_ip_packet[0] + ';'
  packet += str(parse_ip_packet[1]) + ';'
  packet += str(parse_ip_packet[2]) + ';'
  packet += parse_ip_packet[3]
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
  rutas_validas = []
  for ruta in rutas:
    if ip == ruta[0]:
      if int(ruta[1]) <= port <= int(ruta[2]):
        next_hop = (ruta[3], int(ruta[4]))
        rutas_validas.append(next_hop) 
  
  if len(rutas_validas) == 0:
    return None
  else:
    return rutas_validas

i = 0
while True:
  rcv, _ = socketUDP.recvfrom(100)
  parsed_rcv = parse_packet(rcv)
  if parsed_rcv[0] == router_IP and parsed_rcv[1] == int(router_puerto):
    if parsed_rcv[2] > 0:
      print(parsed_rcv[3])
    else:
      print("Se recibió paquete\n" + rcv.decode() + "\ncon TTL 0")
      continue
  else:
    if parsed_rcv[2] > 0:
      next_hops = check_routes(router_rutas, (parsed_rcv[0], parsed_rcv[1]))
      if next_hops:
        largo_hops = len(next_hops)
        if largo_hops - 1 < i:
          i = 0
        new_msg = create_packet([parsed_rcv[0], parsed_rcv[1], parsed_rcv[2] - 1, parsed_rcv[3]])
        print("Redirigiendo paquete\n" + new_msg + "\ncon destino final " + parsed_rcv[0] + " " + str(parsed_rcv[1]) + " desde " + router_IP + " " + router_puerto + " hacia " + next_hops[i][0] + " " + str(next_hops[i][1]))
        socketUDP.sendto(new_msg.encode(), next_hops[i])
        i += 1
      else:
        print("No hay rutas hacia " + parsed_rcv[0] + " " + str(parsed_rcv[1]) + " para paquete\n" + rcv.decode())
    else: 
      print("Se recibió paquete\n" + rcv.decode() + "\ncon TTL 0")
      continue
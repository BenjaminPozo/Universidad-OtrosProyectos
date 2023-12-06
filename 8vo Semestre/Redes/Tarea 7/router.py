import sys
import socket
import random as rn

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
  idp = int(splited_packet[3])
  offset = int(splited_packet[4])
  tamano = int(splited_packet[5])
  flag = int(splited_packet[6])
  msj  = splited_packet[7]
  return [direccion_IP, puerto, ttl, idp, offset, tamano, flag, msj]

def create_packet(parse_ip_packet):
  packet = ''
  packet += parse_ip_packet[0] + ';'
  packet += str(parse_ip_packet[1]).zfill(4) + ';'
  packet += str(parse_ip_packet[2]).zfill(3) + ';'
  packet += str(parse_ip_packet[3]).zfill(8) + ';'
  packet += str(parse_ip_packet[4]).zfill(8) + ';'
  packet += str(parse_ip_packet[5]).zfill(8) + ';'
  packet += str(parse_ip_packet[6]) + ';'
  packet += parse_ip_packet[7]
  return packet.encode()

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
      if int(ruta[1]) == port:
        next_hop = ((ruta[-3], int(ruta[-2])), ruta[-1])
        rutas_validas.append(next_hop) 
  
  if len(rutas_validas) == 0:
    return None
  else:
    return rutas_validas

def dividir_msj(mensaje, MTU):
    partes = []
    if len(mensaje) > MTU:
        i = 0
        while i < len(mensaje):
            partes.append(mensaje[i:i+MTU])
            i += MTU
    else:
        partes.append(mensaje)
    return partes

def fragment_IP_packet(IP_packet, MTU):
  if len(IP_packet) <= MTU:
    return [IP_packet]
  else:
    parsed_IP_packet = parse_packet(IP_packet)
    msj = parsed_IP_packet[7]
    partes_msj = dividir_msj(msj, MTU - 48)
    goffset = 0
    fragments = []
    for i in range(len(partes_msj)):
      itamano = len(partes_msj[i])
      goffset += itamano
      if i == (len(partes_msj) - 1):
        iflag = 0
      else:
        iflag = 1
      imsj = create_packet([parsed_IP_packet[0], parsed_IP_packet[1], parsed_IP_packet[2], 
                            parsed_IP_packet[3], goffset - itamano,itamano ,iflag, partes_msj[i]])
      fragments.append(imsj)
    return fragments

def reassemble_IP_packet(fragment_list):
  if len(fragment_list) == 1:
    parsed_fragment = parse_packet(fragment_list[0])
    if parsed_fragment[4] == 0 and parsed_fragment[6] == 0:
      return fragment_list[0]
    else: return None
  else:
    parsed_fragment_list = []
    for fragment in fragment_list:
      parsed_fragment = parse_packet(fragment)
      parsed_fragment_list.append(parsed_fragment)
    sorted_fragment_list =sorted(parsed_fragment_list, key=lambda x: x[4])
    
    if sorted_fragment_list[0][4] != 0 or sorted_fragment_list[0][6] == 0:
      return None
    
    i = 1
    next_offset = sorted_fragment_list[0][5]
    while i < len(sorted_fragment_list) - 1:
      if sorted_fragment_list[i][4] == next_offset and sorted_fragment_list[i][6] == 1:
        next_offset += sorted_fragment_list[i][5]
        i+=1
      else: return None
    
    if sorted_fragment_list[i][4] == next_offset and sorted_fragment_list[i][6] == 0:
      msj = ''
      for fragment in sorted_fragment_list:
        msj += fragment[7]
      packet = create_packet([sorted_fragment_list[0][0], sorted_fragment_list[0][1], 
                              sorted_fragment_list[0][2], sorted_fragment_list[0][3],
                              0, len(msj), 0, msj])
      return packet
    else: return None

def create_BGP_message():
  with open(router_rutas, 'r', encoding='UTF-8') as rutas:
    reader = rutas.read()
    reader_splited = reader.split('\n')
  
  rutas = []
  for row in reader_splited:
    rutas.append(row.split(' '))

  msj_bgp = 'BGP_ROUTES\n' + router_puerto + '\n'
  
  for ruta in rutas:
    ruta2 = ruta[1:-3]
    for i in range(len(ruta2) - 1):
      msj_bgp += ruta2[i] + ' '
    msj_bgp += ruta2[-1] + '\n'

  msj_bgp += 'END_BGP_ROUTES'
  return msj_bgp

def filtrar_puertos_repetidos(arr):
    numeros_dict = {}

    for elemento in arr:
        numeros = elemento.split()
        primer_numero = numeros[0]
        if primer_numero in numeros_dict:
            if len(elemento) < len(numeros_dict[primer_numero]):
                numeros_dict[primer_numero] = elemento
        else:
            numeros_dict[primer_numero] = elemento

    return list(numeros_dict.values())

def run_BGP():
  with open(router_rutas, 'r', encoding='UTF-8') as rutas:
    reader = rutas.read()
    reader_splited = reader.split('\n')

  rutas = []
  for row in reader_splited:
    rutas.append(row.split(' '))
  
  vecinos = []
  vecinos_puertos = []
  for ruta in rutas:
    if len(ruta[1:-3]) == 2:
      vecinos.append((ruta[-3], ruta[-2]))
      vecinos_puertos.append(ruta[-2])

  for vecino in vecinos:
    s_bgp = create_packet([vecino[0], int(vecino[1]), 100, rn.randint(0, 99999999), 0, 9, 0, 'START_BGP'])
    socketUDP.sendto(s_bgp, (vecino[0], int(vecino[1])))
    ruta_bgp = create_packet([vecino[0], int(vecino[1]), 100, rn.randint(0, 99999999), 0, 9, 0, create_BGP_message()])
    socketUDP.sendto(ruta_bgp, (vecino[0], int(vecino[1])))
  
  nuevas_rutas = []
  socketUDP.settimeout(10)
  while True:
    try:
      i = 0
      rcv, _ = socketUDP.recvfrom(100)
      parsed_rcv = parse_packet(rcv)
      if 'START_BGP' in parsed_rcv[7]:
        continue
      elif 'BGP_ROUTES' in parsed_rcv[7]:
        bgp_msg = parsed_rcv[7].split('\n')
        bgp_routes = bgp_msg[2:-1]
        
        for ruta_bgp in bgp_routes:
          puerto = ruta_bgp.split(' ')[0]
          for vecino in vecinos:
            if puerto not in vecinos_puertos and puerto != router_puerto:
              nueva_ruta = ruta_bgp + ' ' + router_puerto
              if nueva_ruta not in nuevas_rutas:
                nuevas_rutas.append(nueva_ruta)
                i += 1
      sin_rep = filtrar_puertos_repetidos(nuevas_rutas)
      
      if i > 0:
        bgp_msg2 = 'BGP_ROUTES\n'
        for elem in sin_rep:
          bgp_msg2 += elem + '\n'
        bgp_msg2 += 'END_BGP_ROUTES'
        bgp_msg2_final = create_packet([vecino[0], int(vecino[1]), 100, rn.randint(0, 99999999), 0, 9, 0, bgp_msg2])
        for vecino in vecinos:
          socketUDP.sendto(bgp_msg2_final, (vecino[0], int(vecino[1])))

    except TimeoutError: break
  socketUDP.settimeout(None)
  return sin_rep
  
i = 0
diccionario_id = {}
while True:
  rcv, _ = socketUDP.recvfrom(100)
  parsed_rcv = parse_packet(rcv)
  if parsed_rcv[0] == router_IP and parsed_rcv[1] == int(router_puerto):
    if parsed_rcv[2] > 0:
      if parsed_rcv[3] in diccionario_id:
        diccionario_id[parsed_rcv[3]].append(rcv)
      else:
        diccionario_id[parsed_rcv[3]] = [rcv]

      for id in diccionario_id:
        fragment_list = diccionario_id[id]
        reassembled_packet = reassemble_IP_packet(fragment_list)
        if reassembled_packet:
          msj = parse_packet(reassembled_packet)[7]
          print(msj)
          if 'START_BGP' in msj:
            sin_rep = run_BGP()
            with open(router_rutas, 'a', encoding='UTF-8') as rutas:
              for ruta_nueva in sin_rep:
                next_hop = ruta_nueva.split(' ')[-2]
                nueva_linea = '\n' + router_IP + ' ' + ruta_nueva + ' 127.0.0.1 ' + next_hop + ' 1000'
                rutas.write(nueva_linea) 

            with open(router_rutas, 'r', encoding='UTF-8') as rutas:
              contenido = rutas.read()
              print('Tabla de rutas actualizada')
              print(contenido)
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
        mtu = int(next_hops[i][1])
        rcv2 = create_packet([parsed_rcv[0], parsed_rcv[1], parsed_rcv[2] - 1, parsed_rcv[3],
                              parsed_rcv[4], parsed_rcv[5], parsed_rcv[6], parsed_rcv[7]])
        fragments = fragment_IP_packet(rcv2, mtu)
        for fragment in fragments:
          parsed_fragment = parse_packet(fragment)
          print("Redirigiendo paquete\n" + fragment.decode() + "\ncon destino final " + parsed_fragment[0] + " " + str(parsed_fragment[1]) + " desde " + router_IP + " " + router_puerto + " hacia " + next_hops[i][0][0] + " " + str(next_hops[i][0][1]))
          socketUDP.sendto(fragment, next_hops[i][0])
        i += 1
      else:
        print("No hay rutas hacia " + parsed_rcv[0] + " " + str(parsed_rcv[1]) + " para paquete\n" + rcv.decode())
    else: 
      print("Se recibió paquete\n" + rcv.decode() + "\ncon TTL 0")
      continue
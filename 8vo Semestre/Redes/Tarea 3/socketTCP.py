import socket
import random as rn

class SocketTCP:
  def __init__(self): 
    self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.direccionConexion = None
    self.direccion = None
    self.secuencia = None

  def parse_segment(self, msj):
    msjDividido = msj.split(b'|||')

    for i in range(len(msjDividido) - 1):
      msjDividido[i] = int(msjDividido[i].decode())
    return msjDividido

  def create_segment(self, parsedMsj):
    segment = b''
    for i in range(len(parsedMsj) - 1):
      segment += str(parsedMsj[i]).encode() + b'|||'
    segment += parsedMsj[-1]
    return segment
  
  def bind(self, address):
    self.socketUDP.bind(address)
    self.direccion = address

  def connect(self, address):
    self.secuencia = rn.randint(1, 99)
    handshakeMsj1 = self.create_segment([1, 0, 0, self.secuencia, b''])
    self.socketUDP.sendto(handshakeMsj1, address)
    rcvMsj, new_address = self.socketUDP.recvfrom(100)
    handshakeMsj2 = self.parse_segment(rcvMsj)
    if handshakeMsj2[0] == 1 and handshakeMsj2[1] == 1 and handshakeMsj2[3] == self.secuencia + 1:
      self.secuencia += 2
      handshakeMsj3 = self.create_segment([0, 1, 0, self.secuencia, b''])
      self.socketUDP.sendto(handshakeMsj3, new_address)
      self.direccionConexion = new_address

  def accept(self):
    rcvMsj, address = self.socketUDP.recvfrom(100)
    new_socket = SocketTCP()
    taken_address = True
    i = 1
    while taken_address:
      try:
        new_address = ('127.0.0.1', address[1] + i)
        taken_address = False
      except OSError:
        i += 1
    new_socket.bind(new_address)
    handshakeMsj1 = self.parse_segment(rcvMsj)

    if handshakeMsj1[0] == 1:
      new_socket.secuencia = handshakeMsj1[3] + 1
      handshakeMsj2 = new_socket.create_segment([1, 1, 0, new_socket.secuencia, b''])
      new_socket.socketUDP.sendto(handshakeMsj2, address)

      rcvMsj2, _ = new_socket.socketUDP.recvfrom(100)
      handshakeMsj3 = new_socket.parse_segment(rcvMsj2)
      if handshakeMsj3[0] == 0 and handshakeMsj3[1] == 1 and handshakeMsj3[3] == new_socket.secuencia + 1:
        new_socket.direccionConexion = address
        
        return new_socket, new_socket.direccion

#[SYN]|||[ACK]|||[FIN]|||[SEQ]|||[DATOS]
'''miSocket = SocketTCP()
coso = miSocket.parse_segment(b'1|||0|||0|||')
print(miSocket.create_segment(coso))'''
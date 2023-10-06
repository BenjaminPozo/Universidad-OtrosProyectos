import socket
import random as rn

class SocketTCP:
  def __init__(self): 
    self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.direccionDestino = None
    self.direccionOrigen = None
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
    self.direccionOrigen = address

  def connect(self, address):
    self.secuencia = rn.randint(1, 99)
    handshakeMsj1 = self.create_segment([1, 0, 0, self.secuencia, b''])
    self.socketUDP.sendto(handshakeMsj1, address)
    rcvMsj, _ = self.socketUDP.recvfrom(100)
    handshakeMsj2 = self.parse_segment(rcvMsj)
    if handshakeMsj2[0] == 1 and handshakeMsj2[1] == 1 and handshakeMsj2[3] == self.secuencia + 1:
      self.secuencia += 2
      handshakeMsj3 = self.create_segment([0, 1, 0, self.secuencia, b''])
      self.socketUDP.sendto(handshakeMsj3, address)
      self.direccionDestino = address

  def accept(self):
    rcvMsj, address = self.socketUDP.recvfrom(100)
    handshakeMsj1 = self.parse_segment(rcvMsj)

    if handshakeMsj1[0] == 1:
      self.secuencia = handshakeMsj1[3] + 1
      handshakeMsj2 = self.create_segment([1, 1, 0, self.secuencia, b''])
      self.socketUDP.sendto(handshakeMsj2, address)

      rcvMsj2, _ = self.socketUDP.recvfrom(100)
      handshakeMsj3 = self.parse_segment(rcvMsj2)
      if handshakeMsj3[0] == 0 and handshakeMsj3[1] == 1 and handshakeMsj3[3] == self.secuencia + 1:
        self.direccionDestino = address
        new_socket = SocketTCP()
        new_address = ('127.0.0.1', address[1] + 1)
        new_socket.bind(new_address)
        return new_socket, new_address

#[SYN]|||[ACK]|||[FIN]|||[SEQ]|||[DATOS]
'''miSocket = SocketTCP()
coso = miSocket.parse_segment(b'1|||0|||0|||')
print(miSocket.create_segment(coso))'''
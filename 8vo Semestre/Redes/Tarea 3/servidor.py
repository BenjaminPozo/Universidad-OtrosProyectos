import socket

socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_servidor.bind(('localhost', 8000))

while True:
  print('Esperando mensajes...')
  mensaje_reconstruido = b''
  while True:
    msg, address = socket_servidor.recvfrom(16)
    if msg == b'$$FIN$$         ':
      break
    else:
      mensaje_reconstruido+=msg

  print(mensaje_reconstruido.decode())
  socket_servidor.sendto(mensaje_reconstruido, address)
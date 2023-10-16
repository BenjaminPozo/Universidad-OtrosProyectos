import socketTCP

address = ('127.0.0.1', 8000)
server_socketTCP = socketTCP.SocketTCP()
server_socketTCP.bind(address)
connection_socketTCP, new_address = server_socketTCP.accept() 

buff_size = 16
full_message = connection_socketTCP.recv(buff_size)
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
else: print("Test 1: Failed")

buff_size = 19
full_message = connection_socketTCP.recv(buff_size)
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
else: print("Test 2: Failed")

buff_size = 14
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
else: print("Test 3: Failed")

connection_socketTCP.recv_close()

'''import socket

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
  socket_servidor.sendto(mensaje_reconstruido, address)'''
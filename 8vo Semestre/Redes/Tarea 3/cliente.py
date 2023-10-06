import socket
lineas = ''
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  try:
    lineas += input() + '\n'
  except EOFError:
    break
lineas = lineas.encode()
n_bytes = len(lineas)
if (len(lineas)%16) == 0:
  n_iteraciones = len(lineas)//16
else:
  n_iteraciones = ((len(lineas)//16) + 1)

i = 0
mensaje_dividido = []
while i < n_iteraciones:
  bytes_restantes = n_bytes - (i * 16)
  if bytes_restantes >= 16:
    mensaje_dividido.append(lineas[i*16:(i+1)*16])
  else:
    mensaje_dividido.append(lineas[i*16:len(lineas)])
  i+=1
for trozo in mensaje_dividido:
  socket_cliente.sendto(trozo, ('localhost', 8000))

socket_cliente.sendto(b'$$FIN$$         ', ('localhost', 8000))

msg, _ =socket_cliente.recvfrom(1000)
print(msg.decode())
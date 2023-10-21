import CongestionControl as cc

address = ('127.0.0.1', 8000)
server_socketTCP = cc.SocketTCP()
server_socketTCP.bind(address)
connection_socketTCP, new_address = server_socketTCP.accept() 

buff_size = 16
full_message = connection_socketTCP.recv(buff_size, "go_back_n")
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
else: print("Test 1: Failed")

buff_size = 19
full_message = connection_socketTCP.recv(buff_size, "go_back_n")
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
else: print("Test 2: Failed")

buff_size = 16
message_part_1 = connection_socketTCP.recv(buff_size, "go_back_n")
message_part_2 = connection_socketTCP.recv(buff_size, "go_back_n")
message_part_3 = connection_socketTCP.recv(buff_size, "go_back_n")
message_part_4 = connection_socketTCP.recv(buff_size, "go_back_n")
print("Test 3 received:", message_part_1 + message_part_2 + message_part_3 + message_part_4)
if (message_part_1 + message_part_2 + message_part_3 + message_part_4) == "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@".encode(): print("Test 3: Passed")
else: print("Test 3: Failed")

connection_socketTCP.recv_close()

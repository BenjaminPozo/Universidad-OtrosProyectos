import CongestionControl as cc

address = ('127.0.0.1', 8000)
client_socketTCP = cc.SocketTCP()
client_socketTCP.connect(address)

message = "Mensje de len=16".encode()
client_socketTCP.send(message, "go_back_n")

message = "Mensaje de largo 19".encode()
client_socketTCP.send(message, "go_back_n")

message = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@".encode()
client_socketTCP.send(message, "go_back_n")

client_socketTCP.close()

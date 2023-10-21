import socket
import random as rn
import slidingWindowCC as sw
import timerList as tl
SLOW_START = 0
CONGESTION_AVOIDANCE = 1

class SocketTCP:
  def __init__(self): 
    self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.direccionConexion = None
    self.direccion = None
    self.secuencia = None
    self.msj = b''

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
    self.secuencia = rn.randint(100, 200)
    handshakeMsj1 = self.create_segment([1, 0, 0, self.secuencia, b''])
    while True:
      try:
        self.socketUDP.sendto(handshakeMsj1, address)
        self.socketUDP.settimeout(5)
        rcvMsj, new_address = self.socketUDP.recvfrom(100)
        handshakeMsj2 = self.parse_segment(rcvMsj)
        if handshakeMsj2[0] == 1 and handshakeMsj2[1] == 1 and handshakeMsj2[3] == self.secuencia + 1:
          self.secuencia += 2
          handshakeMsj3 = self.create_segment([0, 1, 0, self.secuencia, b''])
          self.socketUDP.sendto(handshakeMsj3, new_address)
          self.direccionConexion = new_address
          print('Conexión establecida con ', self.direccionConexion)
          break
      except TimeoutError: continue

  def accept(self):
    while True:
        try:
            self.socketUDP.settimeout(5)
            rcvMsj, address = self.socketUDP.recvfrom(100)
            new_socket = SocketTCP()
            taken_address = True
            i = 1
            while taken_address:
                try:
                    new_address = ('127.0.0.1', address[1] + i)
                    new_socket.bind(new_address)
                    taken_address = False
                except OSError:
                    i += 1
            handshakeMsj1 = self.parse_segment(rcvMsj)

            if handshakeMsj1[0] == 1:
                new_socket.secuencia = handshakeMsj1[3] + 1
                handshakeMsj2 = new_socket.create_segment([1, 1, 0, new_socket.secuencia, b''])
                while True:
                    try:
                        new_socket.socketUDP.sendto(handshakeMsj2, address)
                        new_socket.socketUDP.settimeout(5)
                        rcvMsj2, _ = new_socket.socketUDP.recvfrom(100)
                        handshakeMsj3 = new_socket.parse_segment(rcvMsj2)
                        if handshakeMsj3[0] == 0 and handshakeMsj3[1] == 1 and handshakeMsj3[3] == new_socket.secuencia + 1:
                            new_socket.direccionConexion = address
                            new_socket.secuencia += 1
                            print('Conexión establecida con ', new_socket.direccionConexion, ' desde ', new_socket.direccion)
                            return new_socket, new_socket.direccion
                    except TimeoutError:
                        continue
        except TimeoutError: continue
  
  def send_using_stop_and_wait(self, message):
    primer_msg = self.create_segment([0,0,0, self.secuencia, str(len(message)).encode()])
    while True:
      try:
        self.socketUDP.sendto(primer_msg, self.direccionConexion)
        self.socketUDP.settimeout(10)
        primer_rcv, _ = self.socketUDP.recvfrom(100)
        parse_primer_rcv = self.parse_segment(primer_rcv)
        if parse_primer_rcv[1] == 1:
          self.secuencia += len(str(len(message)).encode())
          break
        else: continue
      except TimeoutError: continue

    largo = len(message)

    if largo < 16:
      msj = self.create_segment([0,0,0,self.secuencia, message])
      while True:
        try:
          self.socketUDP.sendto(msj, self.direccionConexion)
          self.socketUDP.settimeout(5)
          rcv, _ = self.socketUDP.recvfrom(100)
          parse_rcv = self.parse_segment(rcv)
          if parse_rcv[1] == 1:
            self.secuencia += largo
            break
          else: continue
        except TimeoutError: continue

    else:    
      if largo%16 == 0:
        n_iteraciones = largo//16
      else:
        n_iteraciones = (largo//16) + 1

      trozos_mensaje = []
      i = 0

      while i < n_iteraciones:
        bytes_restantes = largo - (i * 16)
        if bytes_restantes >= 16:
          trozos_mensaje.append(message[i*16:(i+1)*16])
        else:
          trozos_mensaje.append(message[i*16:])
        i+=1

      print(trozos_mensaje)

      for trozo in trozos_mensaje:
        msj_i = self.create_segment([0,0,0,self.secuencia, trozo])
        while True:
          try:  
            self.socketUDP.sendto(msj_i, self.direccionConexion)
            self.socketUDP.settimeout(5)
            rcv_i, _ = self.socketUDP.recvfrom(100)
            parse_rcv_i = self.parse_segment(rcv_i)
            if parse_rcv_i[1] == 1:
              self.secuencia += len(trozo)
              break
            else: continue
          except TimeoutError: continue

  def recv_using_stop_and_wait(self, buffer_size):
    if self.msj == b'':
      while True:
        try:
          self.socketUDP.settimeout(5)
          primer_mensaje, _ = self.socketUDP.recvfrom(18 + 16)
          primer_mensaje_parse = self.parse_segment(primer_mensaje)

          if primer_mensaje_parse[3] == self.secuencia:
            self.secuencia += len(primer_mensaje_parse[4])
            env_primer_mensaje = self.create_segment([0, 1, 0, self.secuencia, b''])
            self.socketUDP.sendto(env_primer_mensaje, self.direccionConexion)
            largo = int(primer_mensaje_parse[4].decode())
            break
          elif primer_mensaje_parse[3] < self.secuencia:
            env_primer_mensaje = self.create_segment([0, 1, 0, self.secuencia, b''])
            self.socketUDP.sendto(env_primer_mensaje, self.direccionConexion)
            largo = int(primer_mensaje_parse[4].decode())
            break
          else: continue
        except TimeoutError: continue

      if largo % 16 == 0:
        n_iteraciones = largo//16
      else:
        n_iteraciones = (largo//16) +1
      
      msj_recibido = b''
      i = 0

      while i < n_iteraciones:
        while True:
          try:
            self.socketUDP.settimeout(5)
            rcv_mensaje, _ = self.socketUDP.recvfrom(18 + 16)
            rcv_mensaje_parse = self.parse_segment(rcv_mensaje)

            if rcv_mensaje_parse[3] == self.secuencia:
              self.secuencia += len(rcv_mensaje_parse[4])
              enviar = self.create_segment([0,1,0,self.secuencia, b''])
              self.socketUDP.sendto(enviar, self.direccionConexion)
              msj_recibido += rcv_mensaje_parse[4]
              i+=1
              break

            elif rcv_mensaje_parse[3] < self.secuencia:
              enviar = self.create_segment([0,1,0,self.secuencia, b''])
              self.socketUDP.sendto(enviar, self.direccionConexion)
              break

            else: continue
          except TimeoutError: continue

      if largo <= buffer_size:
        return msj_recibido
      else:
        self.msj = msj_recibido[buffer_size:]
        return msj_recibido[:buffer_size]
        
    else:
      if buffer_size < len(self.msj):
        return self.msj[:buffer_size]
      else:
        msj = self.msj
        self.msj = b''
        return msj
      
  def close(self):
    msj_termino = self.create_segment([0,0,1,self.secuencia, b''])
    while True:
      try:
        self.socketUDP.sendto(msj_termino, self.direccionConexion)
        self.socketUDP.settimeout(5)
        msj_termino2, _ = self.socketUDP.recvfrom(100)
        msj_termino2_parse = self.parse_segment(msj_termino2)
        if msj_termino2_parse[1] == 1 and msj_termino2_parse[2] == 1 and msj_termino2_parse[3] == self.secuencia + 1:
          self.secuencia += 2
          msj_termino3 = self.create_segment([0,1,0,self.secuencia, b''])
          self.socketUDP.sendto(msj_termino3, self.direccionConexion)
          self.socketUDP.close()
          print('Conexión cerrada con: ', self.direccionConexion)
          break
        else: continue
      except TimeoutError:
        continue
  
  def recv_close(self):
    max_errores = 5
    cant_errores = 0
    while cant_errores < max_errores:
      try:
        self.socketUDP.settimeout(5)
        msj_termino1, _ = self.socketUDP.recvfrom(100)
        msj_termino1_parse = self.parse_segment(msj_termino1)
        if msj_termino1_parse[2] == 1 and msj_termino1_parse[3] == self.secuencia:
          self.secuencia += 1
          msj_termino2 = self.create_segment([0,1,1,self.secuencia,b''])
          cant_errores = 0
          while True:
            try:
              self.socketUDP.sendto(msj_termino2, self.direccionConexion)
              msj_termino3, _ = self.socketUDP.recvfrom(100)
              msj_termino3_parse = self.parse_segment(msj_termino3)
              if msj_termino3_parse[1] == 1 and msj_termino3_parse[3] == self.secuencia + 1:
                self.socketUDP.close()
                print('Conexión cerrada con ', self.direccionConexion)
                return
              else: return
            except TimeoutError: 
              cant_errores += 1
              if cant_errores == max_errores:
                self.socketUDP.close()
                print('Conexión cerrada con ', self.direccionConexion)
                break
              continue
      except TimeoutError: 
        cant_errores += 1
        continue
  
  def send_using_go_back_n(self, message):
    trozos = [message[i:i + 16] for i in range(0, len(message), 16)]
    ventana = sw.SlidingWindowCC(3, [len(message)] + trozos, self.secuencia)
    timer = tl.TimerList(10, 1)

    for i in range(3):
        if ventana.get_data(i) !=  None and ventana.get_sequence_number(i) != None:
          segm = self.create_segment([0,0,0,ventana.get_sequence_number(i), ventana.get_data(i)])
          self.socketUDP.sendto(segm, self.direccionConexion)
          if i == 0:
            timer.start_timer(0)

    while True:
      try:
        timeout = timer.get_timed_out_timers()
        if len(timeout) > 0:
          for i in range(3):
            if ventana.get_data(i) !=  None and ventana.get_sequence_number(i) != None:
              segm = self.create_segment([0,0,0,ventana.get_sequence_number(i), ventana.get_data(i)])
              self.socketUDP.sendto(segm, self.direccionConexion)
              if i == 0:
                timer.start_timer(0)
          
        resp, _ = self.socketUDP.recvfrom(34)
        parse_resp = self.parse_segment(resp)

      except BlockingIOError: continue

      else:
        if parse_resp[1] == 1 and parse_resp[3] == self.secuencia:
          timer.stop_timer(0)
          if ventana.get_data(1) == None:
            self.secuencia += len(ventana.get_data(0))
            return

          else:
            ventana.move_window(1)
            if ventana.get_data(2) != None:
              msj_i = self.create_segment([0,0,0,ventana.get_sequence_number(2), ventana.get_data(2)])
              self.socketUDP.sendto(msj_i, self.direccionConexion)

            self.secuencia = ventana.get_sequence_number(0)
            timer.start_timer(0)
        
        elif parse_resp[1] == 1 and parse_resp[3] > self.secuencia:
          timer.stop_timer(0)
          
          if parse_resp[3] == ventana.get_sequence_number(1):
            ventana.move_window(2)
            if ventana.get_data(0) == None: return
            else:
              self.secuencia = ventana.get_sequence_number(0)
              for i in range(2):
                if ventana.get_data(i + 1) != None: 
                  msj_i = self.create_segment([0,0,0,ventana.get_sequence_number(i+1), ventana.get_data(i+1)])
                  self.socketUDP.sendto(msj_i, self.direccionConexion)
                  if i == 0:
                    timer.start_timer(0)

          elif parse_resp[3] == ventana.get_sequence_number(2):
            ventana.move_window(3)
            if ventana.get_data(0) == None: return
            else:
              self.secuencia = ventana.get_sequence_number(0)
              for i in range(3):
                if ventana.get_data(i) != None: 
                  msj_i = self.create_segment([0,0,0,ventana.get_sequence_number(i), ventana.get_data(i)])
                  self.socketUDP.sendto(msj_i, self.direccionConexion)
                  if i == 0:
                    timer.start_timer(0)

  def recv_using_go_back_n(self, buff_size):
    if self.msj == b'':
      primer_msj, _ = self.socketUDP.recvfrom(34)
      primer_msj_parse = self.parse_segment(primer_msj)
      mensaje_recibido = b''
      if primer_msj_parse[3] == self.secuencia:
        
        msj_resp_1 = self.create_segment([0,1,0,self.secuencia, b''])
        self.socketUDP.sendto(msj_resp_1, self.direccionConexion)

        self.secuencia += len(primer_msj_parse[4])
        largo = int(primer_msj_parse[4].decode())

        if largo%16 == 0:
          n_iteraciones = largo//16
        else:
          n_iteraciones = (largo // 16) + 1
        
        i = 0
        while i < n_iteraciones:
          msj_i, _ = self.socketUDP.recvfrom(34)
          msj_i_parse = self.parse_segment(msj_i)

          if msj_i_parse[3] == self.secuencia:
            mensaje_recibido += msj_i_parse[4]
            
            resp_i = self.create_segment([0,1,0, self.secuencia, b''])
            self.socketUDP.sendto(resp_i, self.direccionConexion)
            self.secuencia += len(msj_i_parse[4])
            i += 1
        if len(mensaje_recibido) > buff_size:
          self.msj = mensaje_recibido[buff_size:]
          mensaje_recibido = mensaje_recibido[:buff_size]
        return mensaje_recibido

    else:
      if buff_size < len(self.msj):
        msj = self.msj[:buff_size]
        self.msj = self.msj[buff_size:]
        return msj
      else:
        msj = self.msj
        self.msj = b''
        return msj

  def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait(message)
        
        elif mode == "go_back_n":
          self.send_using_go_back_n(message)

  def recv(self, buff_size, mode="stop_and_wait"):
      if mode == "stop_and_wait":
          msg = self.recv_using_stop_and_wait(buff_size)
          return msg
      elif mode == "go_back_n":
        msg = self.recv_using_go_back_n(buff_size) 
        return msg

class CongestionControl:

  def __init__(self, MSS):
    self.current_state = SLOW_START
    self.mss = MSS
    self.cwnd = str(MSS).encode()
    self.ssthresh = None
    self.cant_acks = 0

  def get_cwnd(self):
    return int(float(self.cwnd.decode()))

  def get_MSS_in_cwnd(self):
    completeMSS = self.get_cwnd() // self.mss
    return completeMSS

  def event_ack_received(self):
    if self.current_state == SLOW_START:
      self.add1_mss()
      if self.ssthresh is not None: 
        if self.get_cwnd() >= self.ssthresh:
          self.current_state = CONGESTION_AVOIDANCE
          
    else:
      self.cant_acks += 1
      if self.cant_acks * (1 / self.get_MSS_in_cwnd()) == 1:
        self.add1_mss()
        self.cant_acks = 0

  def event_timeout(self):
    if self.current_state == SLOW_START:
      self.ssthresh = self.get_cwnd() // 2
      self.cwnd = str(self.mss).encode()
    else:
      self.ssthresh = self.get_cwnd() // 2
      self.cwnd = str(self.mss).encode()
      self.current_state = SLOW_START
    
  def is_state_slow_start(self):
    if self.current_state == SLOW_START: return True
    else: return False
    
  def is_state_congestion_avoidance(self):
    if self.current_state == CONGESTION_AVOIDANCE: return True
    else: return False

  def get_ssthresh(self):
    return self.ssthresh

  def add1_mss(self):
    cur_cwnd = self.get_cwnd()
    cur_cwnd += self.mss
    byte_cwnd = str(cur_cwnd).encode()
    self.cwnd = byte_cwnd

#[SYN]|||[ACK]|||[FIN]|||[SEQ]|||[DATOS]: 
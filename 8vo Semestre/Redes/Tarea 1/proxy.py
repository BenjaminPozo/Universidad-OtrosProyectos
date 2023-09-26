import socket
import json
import argparse

#El siguiente codigo hace que la ejecución reciba argumentos, en este caso --config (el json)
#Tambien se agrego un argumento help para ayudar al usuario
parser = argparse.ArgumentParser(description='Proxy de la tarea de redes')
parser.add_argument('--config', required=True, help='Ruta al archivo de configuración JSON')
args = parser.parse_args()

#Esto abre el json 
config_path = args.config
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

#Esto obtiene el nombre de usuario 
user_name = config.get('user_name', 'Usuario')

#Función que recibe el mensaje completo
def receive_full_mesage(connection_socket, buff_size, end_sequence, is_client):

    #Recibe el mensaje
    recv_message = connection_socket.recv(buff_size)

    #Se guarda en una variable
    full_message = recv_message

    #is_end_of_message guarda la posicion de la secuancia final y la diferencia del ultimo caracter de la secuencia 
    #hasta el final del mensaje
    is_end_of_message = contains_end_of_message(full_message, end_sequence)

    #Si no esta la secuencia entonces se ejecura el while
    while is_end_of_message[0] == -1:
        #Se recibe el mensaje de nuevo (lo que queda)
        recv_message = connection_socket.recv(buff_size)
        #Se agrega al mensaje anterior
        full_message += recv_message
        #Se calculo de nuevo is_end_of_message
        is_end_of_message = contains_end_of_message(full_message, end_sequence)
    #Si la funcion es invocada desde el lado del cliente simplemente se retorna el mensaje
    if is_client:
        return full_message
    #En caso contrario:
    else:
        #splited_msg guarda el mensaje divido en headers y body (eso lo hace la función parse_HTTP_message)
        splited_msg = parse_HTTP_message(full_message)
        #headers guarda los headers (es un diccionario)
        headers = splited_msg[0]
        #Se recorre el diccionario
        for header in headers:
            #La idea de esta parte es encontrar el header que tuviera el valor de Content-Length lo cual
            #es extraño ya que si quisiera el valor simplemente llamo al valor asociado a la llave b'Content-Length'
            #pero por alguna razón eso no funcionaba y la unica manera de encontrar el valor era
            #recorriendo el diccionario secuencialmente matando completamente la gracia de usar un diccionario
            if b'Content-Length' == header:
                content_length = headers[header]
        #Si is_end_of_message[1] es 0 significa que la secuencia de termino estaba al final de los headers y que no se
        #tomo ningun dato del body
        if is_end_of_message[1] == 0:
            #Se recibe el resto del mensaje (body)
            recv_message = connection_socket.recv(int(content_length.decode()))
            full_message += recv_message
        #Si is_end_of_message[1] no es 0 significa que algunos bytes del body se tomaron con los headers por lo que
        # no hay que considerarlos al momento de recibir el resto del mensaje 
        else:
            #Lo que llego con los headers
            body = splited_msg[1]
            #El resto del Body
            recv_message = connection_socket.recv(int(content_length.decode()) - is_end_of_message[1])
            #Todo junto
            full_message += body + recv_message
        
        return full_message


#Funcion que ve si el mensaje contiene el la secuencia de final
def contains_end_of_message(message, end_sequence):
    #Se usa find para encontrar la secuencia en el string, find retorna -1 si no esta la secuencia, usaremos eso
    position_find = message.find(end_sequence)
    #Retornamos una lista de 2 valores que contiene la posicion de la secuencia y cuanto falta desde el final de la secuencia
    # hasta el final del mensaje
    return [position_find, (len(message) - position_find - 4)]

#Funcion que divide el mensaje en headers y body
def parse_HTTP_message(http_message):
    
    #Dividimos el mensaje por el caracter \r\n\r\n que es el que divide a los headers del body, splited_msg es una lista
    splited_msg = http_message.split(b'\r\n\r\n')
    #Naturalmente el primer valor de la lista seran los headers, los cuales dividimos nuevamente para tener cada 
    #header por separado
    headers = splited_msg[0].split(b'\r\n')
    #diccionario que llenaremos con los valores de los headers
    dicc_headers = {}
    for header in headers:
        #Con esto dividimos los headers en llave y valor
        info = header.split(b': ')
        if len(info) > 1:
            #Asignamos como llave el nombre del header y a la definición su valor
            dicc_headers[info[0]] = info[1]
        else:
            #La startline es la unica linea que no será separada por lo que la guardamos como Startline
            dicc_headers[b'Startline'] = info[0]
    #Verificamos que haya algo en la otra parte del mensaje dividido (por \r\n\r\n)
    if(len(splited_msg) > 1):
        #Si es asi entonces lo asignamos a body
        body = splited_msg[1]
        #Creamos la lista de 2 elementos (diccionario, cuerpo)
        new_http_msg = [dicc_headers, body]
        return new_http_msg
    else:
        #De no ser asi entonces le damos un cuerpo vacio
        new_http_msg = [dicc_headers, b'']
        return new_http_msg

#Funcion que convierte una estructura en un mensaje completo, hace un mensaje por si la página está prohibida con el
#parametro is_forbbiden
def create_HTTP_message(new_http_msg, is_forbbiden):
    #Si el valor de is_forbbiden es true entonces:
    if is_forbbiden:
        #Variable que llenaremos
        headers = b''
        #Recorremos el diccionario
        for elemento in new_http_msg[0]:
            #Si estamos en la startline entonces guardamos en header el mensaje con el error 403
            if elemento == b'Startline':
                header = b'HTTP/1.1 403 Forbidden\r\n'
            #Si no entonces simplemente armamos la estructura de un header
            else:
                header = elemento + b': ' + new_http_msg[0][elemento] + b'\r\n'
            #Agregamos a la variable anterior
            headers += header
        #Agregamos \r\n ya que el ultimo header agregara \r\n para finalmente tener \r\n\r\n
        headers += b'\r\n'
        final_msg = headers
        return final_msg
    else:
        #Si no es prohibido entonces hacemos algo analogo solo que sin el error 403
        headers = b''
        for elemento in new_http_msg[0]:
            if elemento == b'Startline':
                header = new_http_msg[0][elemento] + b'\r\n'
            else:
                header = elemento + b': ' + new_http_msg[0][elemento] + b'\r\n'
            headers += header
        #Agregamos el header del enunciado con el Usuario del json
        headers += b'X-ElQuePregunta: ' + user_name.encode() + b'\r\n' 
        headers += b'\r\n'
        final_msg = headers
        return final_msg + new_http_msg[1]

#Funcion que obtiene la url de la startline
def get_url(startline):
    startline_str = startline.decode() 
    #Dividimos la startline por espacios
    startline_parts = startline_str.split(' ') 

    if len(startline_parts) > 1:
        #part1 tiene el segundo elemento de la lista que se crear al dividir por espacio
        #una startline normal por lo general es METODO PROTOCOLO+URL VERSION-HTTP 
        part1 = startline_parts[1]
        #Queremos solo la url por lo que dividimos por // para separar el protocolo de la url
        url = part1.split('//')
        if len(url) > 1:
            #Verificamos si la url termina con / (endw es un booleano)
            endw = url[1].endswith('/')
            if endw:
                #Si termina con / entonces dividimos y nos quedamos solo con la primera parte
                #ejemplo: http://example.com/ -> example.com
                final_url = url[1].split('/')
                return final_url[0]
            else:
                return url[1]

    return None

#Variables globales
buff_size = 4
end_of_message = b'\r\n\r\n'
new_socket_address = ('localhost', 8000)

print('Creando socket - Servidor')

#Se crea el socket y se configura para que se conecte a la dirección y soporte 3 clientes
server_like_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_like_socket.bind(new_socket_address)
server_like_socket.listen(3)

print('... Esperando clientes')
while True:
    try:
        #Se acepta el cliente
        new_socket, new_socket_address = server_like_socket.accept()
        #Se recibe el mensaje
        client_request = receive_full_mesage(new_socket, buff_size, end_of_message, True)
        #Se divide en headers y body
        splited_client_req = parse_HTTP_message(client_request)
        
        #El codigo que viene es por un problema con mi navegador ya que llegaban solicitudes extrañas
        #con metodos CONNECT, el proposito de esto es cambiarlo por GET -> no funcionó
        #A pesar de tener GET en lugar de CONNECT el código se cae igualmente
        #Se divide la startline por espacios y se toma el primer valor
        get = splited_client_req[0][b'Startline'].split(b' ')[0]
        #Si este valor no es GET entonces se reemplaza por este
        if get != b'GET':
            get_msg = b'GET '
            for i in range(1, len(splited_client_req[0][b'Startline'].split(b' '))):
                get_msg += splited_client_req[0][b'Startline'].split(b' ')[i]
            splited_client_req[0][b'Startline'] = get_msg
            client_request = create_HTTP_message(splited_client_req, False)
        
        print(f' -> Se ha recibido la siguiente peticion: {client_request}')

        #Se parsea el mensaje entregado
        new_msg = parse_HTTP_message(client_request)
        #Se comprueba que la url de la request no esté en la lista de paginas prohibidas
        for url in config["blocked"]:
            startline = new_msg[0][b'Startline']
            position_find = startline.find(url.encode())
            if position_find != -1:
                break
        #Si position_find es -1 entonces la pagina solicitada es valida
        if position_find == -1:
            #Obtenemos la url
            url = get_url(new_msg[0][b'Startline'])
            #Creamos el socket para hacer de cliente de cara al servidor
            client_like_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #Creamos la dirección con puerto 80
            address = (url, 80)
            #Nos conectamos
            client_like_socket.connect(address)
            #Creamos un mensaje http con is_forbbiden Falso
            client_send_msg = create_HTTP_message(new_msg, False)
            #Lo enviamos
            client_like_socket.send(client_send_msg)
            #Recibimos el mensaje del servidor
            server_response = receive_full_mesage(client_like_socket, buff_size, end_of_message, False)
            #Lo dividimos
            splited_server_response = parse_HTTP_message(server_response)
            #Tomamos el mensaje censurado como el body
            censored_msg = splited_server_response[1]
            #Buscamos el largo del contenido (Anteriormente tuve problemas con encontrar este valor de la manera 
            # que queria, por alguna razón aqui si funciona)
            content_length = int(splited_server_response[0][ b'Content-Length'].decode())
            #Dado que en el json las palabras prohibidas estan en listas que tienen diccionarios de una palabra tenemos que
            #descomponer el json
            for item in config["forbidden_words"]:
                #Vemos las palabras prohibidas y su reemplazo
                for f_word, replace in item.items():
                    #Buscamos la palabra prohibida
                    find = censored_msg.find(f_word.encode())
                    #Si find no es -1 entonces la palabra si está
                    if find != -1:
                        #Cambiamos el content_length ya que es posible que las palabras de reemplazo sean mas largas
                        #(o mas cortas) que la original
                        content_length = content_length - len(f_word.encode()) + len(replace.encode()) + 1
                        #Reemplazamos la palabra con replace
                        censored_msg = censored_msg.replace(f_word.encode(), replace.encode())
            #Cambiamos el valor de content_length
            splited_server_response[0][ b'Content-Length'] = (str(content_length)).encode()
            #Creamos el mensaje final
            final_server_response = create_HTTP_message([splited_server_response[0], censored_msg], False)
            #Se envia el mensaje
            new_socket.send(final_server_response)

        else:
            #Si la pagina esta dentro de la lista de prohibidas entonces se hace un mensaje de error y se envia
            error_msg = create_HTTP_message(new_msg, True)
            new_socket.send(error_msg)
        
        #Cerrar la conexion
        new_socket.close()
        print(f"conexion con {new_socket_address} ha sido cerrada")
    #Esto es porque no funcionaba interrumpir el proceso cuando algo iba mal (ctrl+c no funcionaba)
    except KeyboardInterrupt:
        print("Interrupcion detectada. Cerrando el servidor.")
        server_like_socket.close()
        break
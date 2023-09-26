import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion
from dnslib.dns import CLASS, QTYPE
import dnslib

# Direccion del servidor DNS raiz
ROOT_DNS_SERVER = ('192.33.4.12', 53)

# Función que guarda el mensaje DNS en un diccionario de diccionarios
def parse_dns_msg(msg):

    # Se usa dnslib para separar el mensaje
    dns_msg = DNSRecord.parse(msg)
    # Se crean 4 claves que no necesitan un diccionario adicional: Consulta, cantidad de elementos de respuesta, autorización y adicional
    dns_dic = {
            "Qname": dns_msg.q.qname,
            "ANCOUNT": dns_msg.header.a,
            "NSCOUNT": dns_msg.header.auth,
            "ARCOUNT": dns_msg.header.ar
        }

    # Si es que hay elementos de consulta entonces procede
    if dns_msg.header.a > 0:
        # Se crea un diccionario con los valores más relevantes
        answer_section = {
            "all_resource_records": dns_msg.rr,
            "first_answer": dns_msg.get_a(),
            "domain_name_in_answer": dns_msg.get_rname(),
            "answer_class": CLASS.get(dns_msg.get_a().rclass),
            "answer_type":  QTYPE.get(dns_msg.get_a().rtype),
            "answer_rdata": dns_msg.get_a().rdata
        }
        #Se guarda el diccionario
        dns_dic["Answer"] = answer_section
    else:
        #Si no hay elementos de respuesta entonces se guarda un diccionario vacio
        dns_dic["Answer"] = {}

    #Analogo con la seccion de respuesta
    if dns_msg.header.auth > 0:
        authority_section_list = dns_msg.auth 

        if len(authority_section_list) > 0:
            authority_section_RR_0 = authority_section_list[0]
            auth_type = QTYPE.get(authority_section_RR_0.rtype)
            auth_class = CLASS.get(authority_section_RR_0.rclass)
            auth_time_to_live = authority_section_RR_0.ttl
            authority_section_0_rdata = authority_section_RR_0.rdata

            authority_section = {
                "authority_section_RR_0": authority_section_RR_0,
                "auth_type": auth_type,
                "auth_class": auth_class,
                "auth_time_to_live": auth_time_to_live,
                "authority_section_0_rdata": authority_section_0_rdata
            }

            #Las lineas de abajo dan valores a ciertas llaves dependiendo del tipo de elemento que es en esta seccion
            if isinstance(authority_section_0_rdata, dnslib.dns.SOA):
                primary_name_server = authority_section_0_rdata.get_mname() 
                authority_section["primary_name_server"] = primary_name_server
                authority_section["name_server_domain"] = None

            elif isinstance(authority_section_0_rdata, dnslib.dns.NS): 
                name_server_domain = authority_section_0_rdata 
                authority_section["name_server_domain"] = name_server_domain
                authority_section["primary_name_server"] = None

            dns_dic["Authority"] = authority_section

    else:
        dns_dic["Authority"] = {}

    #Analogo a las secciones anteriores
    if dns_msg.header.ar > 0:
        additional_records = dns_msg.ar  
        first_additional_record = additional_records[0]
        ar_class = CLASS.get(first_additional_record.rclass)
        ar_type = QTYPE.get(first_additional_record.rclass)

        additional_section = {
            "additional_records": dns_msg.ar,
            "first_additional_record": first_additional_record,
            "ar_class": ar_class,
            "ar_type": ar_type
        }

        if ar_type == 'A': 
            first_additional_record_rname = first_additional_record.rname 
            first_additional_record_rdata = first_additional_record.rdata 
            additional_section["first_additional_record_rname"] = first_additional_record_rname
            additional_section["first_additional_record_rdata"] = first_additional_record_rdata
        
        dns_dic["Additional"] = additional_section
    else:
        dns_dic["Additional"] = {}

    return dns_dic

#Funcion que recibe un mensaje DNS y devuelve la respuesta del servidor que lo resuelve
def resolver(mensaje_consulta, debug=False):

    # Sockets que se conectan con el servidor raiz
    root_dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    root_dns_sock.sendto(mensaje_consulta, ROOT_DNS_SERVER)
    response, _ = root_dns_sock.recvfrom(4096)

    #La respuesta del servidor raiz se le aplica un parse
    parsed_response = parse_dns_msg(response)
    
    #Si hay elementos answer se verifica si este es tipo 'A', si es asi se retorna
    if (len(parsed_response["Answer"]) > 0):
        if parsed_response["Answer"]["answer_type"] == 'A':
            return response

    #Si no pasa lo anterior, se verifica si hay elementos 'Authority' y se verifica que sea de tipo NS
    if (len(parsed_response["Authority"]) > 0):
        if (parsed_response["Authority"]["auth_type"] == 'NS'):
            #De ser asi se verifica si hay elementos additional
            if (len(parsed_response["Additional"]) > 0):
                #De ser asi se recorren los elemetnos hasta dar con uno que sea tipo A
                for i in parsed_response["Additional"]["additional_records"]:
                    if QTYPE.get(i.rclass) == 'A':
                        #Si es tipo A se muestra en el debug y se envia el mensaje original al servidor que tiene la respuesta
                        server_ip = str(parsed_response["Additional"]["first_additional_record_rdata"])
                        if debug:
                            print(f"(debug) Consultando '{parsed_response['Qname']}' a '{parsed_response['Additional']['first_additional_record_rname']}' con dirección IP '{server_ip}'")
                        dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        dns_sock.sendto(mensaje_consulta, (server_ip.encode(), 53))
                        responseq, _ = dns_sock.recvfrom(4096)
                        return responseq
                
                #Si nada de lo anterior funciona se toma un dominio de la seccion auth
                name_server = str(parsed_response["Authority"]["name_server_domain"])
                if debug:
                    print(f"(debug) Consultando IP para '{name_server}'")
                #Se crea una query para el dominio elegido y se hace recursión
                query = DNSRecord(DNSHeader(qr=0, opcode=0, aa=0, tc=0, rd=1), q=DNSQuestion(name_server, QTYPE.A)).pack()
                resolver(query, debug=debug)                
    #Si absolutamente nada de lo anterior ocurre entonces se ignora el mensaje
    return b''

#Se crea el socket de nuestro servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 8000))

#Bucle para que entren mensajes
while True:
    print('Esperando mensajes...')
    message, address = sock.recvfrom(4000)
    response = resolver(message, True)
    sock.sendto(response, address)
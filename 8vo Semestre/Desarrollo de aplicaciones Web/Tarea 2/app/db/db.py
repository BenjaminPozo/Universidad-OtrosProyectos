import pymysql
from flask import Flask, render_template, jsonify, request, redirect, url_for

def getConnection():
  conn = pymysql.connect(
    db='tarea2',
    user='cc5002',
    passwd='programacionweb',
    host='localhost',
    port=3306,
    charset='utf8'
  )
  return conn

def get_regiones():
  conn = getConnection()
  sql = "SELECT * FROM region"
  cursor = conn.cursor()
  cursor.execute(sql)
  regiones = cursor.fetchall()
  resultado = []
  for idR, region in regiones:
    resultado.append(region)
  return resultado
  
def get_regiones_comunas():
    conn = getConnection()
    sql = """
      SELECT region.nombre, comuna.nombre FROM
        region
        JOIN comuna
        ON region.id = comuna.region_id;
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    regionesComunas = cursor.fetchall()

    regiones = {}

    for region, comuna in regionesComunas:
      if region in regiones:
        regiones[region].append(comuna)
      else:
        regiones[region] = [comuna]
  
    return regiones

def get_tipo_artesania():
  conn = getConnection()
  sql = "SELECT * FROM tipo_artesania"
  cursor = conn.cursor()
  cursor.execute(sql)
  tipos = cursor.fetchall()
  resultado = []
  for idT, tipo in tipos:
    resultado.append(tipo)
  return resultado

def crear_artesano(comuna, descripcion, nombre, email, celular, tipos, fotos):
  conn = getConnection()
  cursor = conn.cursor()
  sqlid = "SELECT id from comuna WHERE UPPER(nombre) LIKE UPPER(%s)"
  cursor.execute(sqlid, ('%' + comuna + '%',))
  comunaId = cursor.fetchone()[0]
  sql = """
      INSERT INTO artesano 
      (comuna_id, descripcion_artesania, nombre, email, celular) 
      VALUES (%s,%s,%s,%s,%s)    
  """
  cursor.execute(sql, (comunaId, descripcion, nombre, email, celular,))
  conn.commit()

  sql3 = "SELECT id FROM artesano ORDER BY id DESC LIMIT 1"
  cursor.execute(sql3)
  id_artesano = cursor.fetchone()[0]

  for tipo in tipos:
    sql4 = "SELECT id FROM tipo_artesania WHERE UPPER(nombre) = UPPER(%s)"
    cursor.execute(sql4, (tipo,))
    id_tipo = cursor.fetchone()[0]
    sql5 = "INSERT INTO artesano_tipo (artesano_id, tipo_artesania_id) VALUES (%s,%s)"
    cursor.execute(sql5, (id_artesano, id_tipo,))
    conn.commit()
  print(fotos)
  for foto in fotos:
    sql6 = "INSERT INTO foto (ruta_archivo, nombre_archivo, artesano_id) VALUES ('/static/uploads',%s,%s)"
    cursor.execute(sql6, (foto, id_artesano,))
    conn.commit()

def get_fotos_artesano(id_artesano):
  conn = getConnection()
  cursor = conn.cursor()
  sql = """SELECT nombre_archivo
          FROM artesano JOIN foto ON artesano.id = foto.artesano_id
          AND artesano.id = %s
        """
  cursor.execute(sql, (id_artesano, ))
  fotos = cursor.fetchall()
  fotos_array = []
  for foto in fotos:
    fotos_array.append(foto[0])
  return fotos_array

def get_artesanos(start_index):
  conn = getConnection()
  cursor = conn.cursor()
  sql = """SELECT AR.id, AR.nombre, AR.celular, AR.comuna, TA.nombre FROM
            (SELECT * FROM
            (SELECT artesano.id, artesano.nombre, celular, email, comuna.nombre AS comuna
            FROM artesano JOIN comuna on comuna_id = comuna.id
            ORDER BY id DESC LIMIT 5 OFFSET %s) AS A
            JOIN
            artesano_tipo AS T
            ON A.id = T.artesano_id) AS AR
            JOIN 
            tipo_artesania AS TA
            ON AR.tipo_artesania_id = TA.id"""
  cursor.execute(sql, (start_index, ))
  artesanos = cursor.fetchall()
  grouped_data = {}

  for item in artesanos:
      id, name, phone, location, value = item
      if id in grouped_data:
          grouped_data[id][4].append(value)
      else:
          grouped_data[id] = (id, name, phone, location, [value])

  result = list(grouped_data.values())
  
  artesanos_tipos = []
  for artesano in result:
    tipo = ''
    for material in artesano[4]:
      tipo += material + ', '
    tipo = tipo[:-2]
    nuevo_artesano = (*artesano[:4], tipo)
    artesanos_tipos.append(nuevo_artesano)
  artesano_final = []
  for artesano in artesanos_tipos:
    fotos_artesano = get_fotos_artesano(artesano[0])
    nuevas_fotos = []
    for foto in fotos_artesano:
      nuevas_fotos.append(url_for('static', filename=f"uploads/{foto}"))
    nuevo_artesano = (*artesano, nuevas_fotos)
    artesano_final.append(nuevo_artesano)
  return artesano_final
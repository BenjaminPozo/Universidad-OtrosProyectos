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

def get_deportes():
  conn = getConnection()
  sql = "SELECT * FROM deporte"
  cursor = conn.cursor()
  cursor.execute(sql)
  deportes = cursor.fetchall()
  resultado = []
  for idR, deporte in deportes:
    resultado.append(deporte)
  return resultado

def crear_hincha(comuna, adicional, nombre, email, celular, deportes, transporte):
  conn = getConnection()
  cursor = conn.cursor()
  sqlid = "SELECT id from comuna WHERE UPPER(nombre) LIKE UPPER(%s)"
  cursor.execute(sqlid, ('%' + comuna + '%',))
  comunaId = cursor.fetchone()[0]
  sql = """
      INSERT INTO hincha 
      (comuna_id, modo_transporte, nombre, email, celular, comentarios) 
      VALUES (%s,%s,%s,%s,%s,%s)    
  """
  cursor.execute(sql, (comunaId, transporte, nombre, email, celular, adicional))
  conn.commit()

  sql3 = "SELECT id FROM hincha ORDER BY id DESC LIMIT 1"
  cursor.execute(sql3)
  id_hincha = cursor.fetchone()[0]

  for deporte in deportes:
    sql4 = "SELECT id FROM deporte WHERE UPPER(nombre) = UPPER(%s)"
    cursor.execute(sql4, (deporte,))
    id_deporte = cursor.fetchone()[0]
    sql5 = "INSERT INTO hincha_deporte (hincha_id, deporte_id) VALUES (%s,%s)"
    cursor.execute(sql5, (id_hincha, id_deporte,))
    conn.commit()

def get_hinchas(start_index):
  conn = getConnection()
  cursor = conn.cursor()
  sql = """SELECT h1.id, h1.nombre, h1.comuna, h1.modo_transporte, h1.celular, h2.deporte FROM
            (SELECT hincha.id,hincha.nombre, comuna.nombre as comuna, hincha.modo_transporte, hincha.celular FROM 
            hincha JOIN comuna
            ON (hincha.comuna_id = comuna.id)
            ORDER BY hincha.id DESC LIMIT 5 OFFSET %s
            ) AS h1
            JOIN
            (SELECT hincha_deporte.hincha_id, deporte.nombre as deporte FROM deporte JOIN hincha_deporte ON deporte.id = hincha_deporte.deporte_id) AS h2
            ON h1.id = h2.hincha_id"""
  cursor.execute(sql, (start_index, ))
  hinchas = cursor.fetchall()
  grouped_data = {}

  for item in hinchas:
      id, nombre, comuna, transporte, celular, deporte = item
      if id in grouped_data:
          grouped_data[id][5].append(deporte)
      else:
          grouped_data[id] = (id, nombre, comuna, transporte, celular, [deporte])

  result = list(grouped_data.values())

  hinchas_final = []
  for item in result:
    nuevo_hincha = list(item[:5])
    deporte_fin = ''
    for deporte in item[5]:
      deporte_fin += deporte + ', '
    deporte_fin = deporte_fin[:-2]
    nuevo_hincha.append(deporte_fin)
    hinchas_final.append(nuevo_hincha)
  return hinchas_final

def get_hincha_info(id):
  conn = getConnection()
  cursor = conn.cursor()
  sql = """SELECT h3.id, h3.nombre, h3.region, h3.comuna, h3.modo_transporte, h3.email, h3.celular, 
            h3.comentarios, deporte.nombre as deporte FROM 
            (SELECT h2.id, h2.nombre, region.nombre as region, h2.comuna, h2.modo_transporte, h2.email, h2.celular, h2.comentarios, 
            hincha_deporte.deporte_id FROM 
            (SELECT h1.id, h1.nombre, comuna.nombre AS comuna, h1.modo_transporte, h1.email, h1.celular, h1.comentarios, 
            comuna.region_id FROM
            (SELECT * FROM hincha WHERE id = %s) AS h1 JOIN
            comuna ON comuna.id = h1.comuna_id) AS h2 JOIN region ON region.id = h2.region_id
            JOIN hincha_deporte ON hincha_deporte.hincha_id = h2.id) AS h3 JOIN deporte ON h3.deporte_id = deporte.id"""
  cursor.execute(sql, (id, ))
  hincha = list(cursor.fetchall())
  hincha_fin = list(hincha[0])[:8]
  deportes = ''
  for item in hincha:
    deportes += item[8] + ', '
  deportes = deportes[:-2]
  hincha_fin.append(deportes)
  return hincha_fin

def info_grafico_hinchas():
  conn = getConnection()
  cursor = conn.cursor()
  sql = """SELECT deporte.nombre, t1.conteo FROM
          (SELECT hincha_deporte.deporte_id, COUNT(*) as conteo FROM hincha_deporte GROUP BY hincha_deporte.deporte_id) as t1
          JOIN
          deporte ON deporte.id = t1.deporte_id"""
  cursor.execute(sql)
  datos = cursor.fetchall()
  datos_fin = []
  for deporte, count in datos:
    data = {
      'deporte': deporte,
      'count': count
    }
    datos_fin.append(data)
  return datos_fin

def info_grafico_artesano():
  conn = getConnection()
  cursor = conn.cursor()
  sql = """SELECT tipo_artesania.nombre, t1.conteo FROM
            (SELECT artesano_tipo.tipo_artesania_id, COUNT(*) as conteo FROM artesano_tipo GROUP BY artesano_tipo.tipo_artesania_id) AS t1
            JOIN tipo_artesania ON tipo_artesania.id = t1.tipo_artesania_id"""
  cursor.execute(sql)
  datos = cursor.fetchall()
  tipos_fin = []
  for tipo, count in datos:
    data = {
      "tipo": tipo,
      "count": count
    }
    tipos_fin.append(data)
  return tipos_fin
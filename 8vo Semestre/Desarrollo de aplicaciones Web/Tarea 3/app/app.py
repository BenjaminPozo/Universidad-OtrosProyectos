from flask import Flask, render_template, jsonify, request, redirect, url_for
from db import db
from utils import validations as vd
import os
from flask_paginate import Pagination
import hashlib
from werkzeug.utils import secure_filename
import filetype

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.secret_key = 's3cr3t_k3y'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
regionesComunas = db.get_regiones_comunas()
regiones = db.get_regiones()
tipos = db.get_tipo_artesania()
deportes = db.get_deportes()

@app.route('/get_data', methods=['GET'])
def get_data():
    data = regionesComunas
    return jsonify(data=data)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/agregar-hincha')
def agregar_hincha():
  data = {
    "regiones" : regiones,
    "deportes" : deportes
  }
  return render_template('registrar-hincha.html', data=data)

@app.route('/ver-hinchas')
def ver_hinchas():
  conn = db.getConnection()
  cursor = conn.cursor()

  sql = "SELECT COUNT(*) AS total FROM hincha"
  cursor.execute(sql)
  count = cursor.fetchone()[0]

  page_num = request.args.get('page', 1, type=int)
  per_page = 5

  start_index = (page_num - 1) * per_page

  query = ""
  hinchas = db.get_hinchas(start_index)

  end_index = min(start_index + per_page, count)

  if end_index > count:
    end_index = count
  
  data = {
    "hinchas" : hinchas
  }

  pagination = Pagination(page=page_num, total=count, per_page=per_page)

  return render_template('lista-hinchas.html', data = data, pagination=pagination)

@app.route('/agregar-artesano')
def agregar_artesano():
  data = {
    "regiones" : regiones,
    "tipos" : tipos
  }
  return render_template('registrar-artesano.html', data=data)

@app.route('/ver-artesanos')
def ver_artesanos():
  conn = db.getConnection()
  cursor = conn.cursor()

  sql = "SELECT COUNT(*) AS total FROM artesano"
  cursor.execute(sql)
  count = cursor.fetchone()[0]

  page_num = request.args.get('page', 1, type=int)
  per_page = 5

  start_index = (page_num - 1) * per_page

  query = ""
  print(start_index)
  artesanos = db.get_artesanos(start_index)

  end_index = min(start_index + per_page, count)

  if end_index > count:
    end_index = count
  
  data = {
    "artesanos" : artesanos
  }

  pagination = Pagination(page=page_num, total=count, per_page=per_page)

  return render_template('lista-artesanos.html', data = data, pagination=pagination)

@app.route("/post-artesano", methods=["POST"])
def post_artesano():
  region = request.form.get("selectRegion")
  comuna = request.form.get("selectComuna")
  tipos = request.form.getlist('tipo-artesania')
  descripcion = request.form.get("descripcion")
  nombre = request.form.get("nombre")
  email = request.form.get("email")
  celular = request.form.get("celular")
  fotos = request.files.getlist("fotos")
  fotos_array = []
  if fotos:
    for foto in fotos:
      _filename = hashlib.sha256(
          secure_filename(foto.filename).encode("utf-8")
      ).hexdigest()
      _extension = filetype.guess(foto).extension
      img_filename = f"{_filename}.{_extension}"

      # Guardar la imagen 
      fotos_array.append(img_filename)
      foto.save(os.path.join(app.config["UPLOAD_FOLDER"], img_filename))

  valid = True
  valid &= vd.validate_name(nombre)
  valid &= vd.validate_region(region)
  valid &= vd.validate_comuna(comuna)
  valid &= vd.validate_email(email)
  valid &= vd.validate_phone(celular)
  valid &= vd.validate_tipos(tipos)

  if valid:
    db.crear_artesano(comuna, descripcion, nombre, email, celular, tipos, fotos_array)
    return redirect(url_for("index"))

@app.route("/post-hincha", methods=["POST"])
def post_hincha():
  region = request.form.get("selectRegion")
  comuna = request.form.get("selectComuna")
  deportes = request.form.getlist('deporte')
  adicional = request.form.get("adicional")
  nombre = request.form.get("nombre")
  email = request.form.get("email")
  celular = request.form.get("celular")
  transporte = request.form.get("selectTransporte")

  valid = True
  valid &= vd.validate_name(nombre)
  valid &= vd.validate_region(region)
  valid &= vd.validate_comuna(comuna)
  valid &= vd.validate_email(email)
  valid &= vd.validate_phone(celular)
  valid &= vd.validate_tipos(deportes)
  valid &= vd.validate_transporte(transporte)
  if transporte == None:
    valid &= False

  if valid:
    db.crear_hincha(comuna, adicional, nombre, email, celular, deportes, transporte)
    return redirect(url_for("index"))
  
@app.route("/informacion-artesano")
def informacion_artesano():
  return render_template('informacion-artesano.html')

@app.route("/informacion_hincha/<int:hincha_id>")
def informacion_hincha(hincha_id):
  hincha_info = db.get_hincha_info(hincha_id)
  print(hincha_info)
  return render_template('informacion-hincha.html', hincha_info=hincha_info)

@app.route('/obtener_datos_hincha', methods=['GET'])
def obtener_datos_hincha():
  datos = db.info_grafico_hinchas()
  return jsonify(datos)  

@app.route('/obtener_datos_artesano', methods=['GET'])
def obtener_datos_artesano():
  datos = db.info_grafico_artesano()
  return jsonify(datos)  

@app.route("/estadisticas")
def estadisticas():
  return render_template('estadisticas.html')

if __name__ == '__main__':
  app.run(debug=True)
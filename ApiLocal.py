# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict
from flask_cors import CORS  # Importa CORS
from flask_migrate import Migrate


app = Flask(__name__)

CORS(app)  # Habilita CORS para toda la aplicación


# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.environ.get("DATABASE_URL")

# Corregir formato si es necesario
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Crear la instancia de Migrate
migrate = Migrate(app, db)    

# Definir el modelo de datos para los animales
class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Agregar un ID único
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    foto = db.Column(db.String(200), nullable=True)  # Foto del animal
    fecha_nacimiento = db.Column(db.String(50), nullable=True)  # Fecha de nacimiento
    
    # Relación con las vacunas
    vacunas = db.relationship('Vacuna', backref='animal', lazy=True)

class Vacuna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)  # Relación con Animal


# Crear la base de datos
#with app.app_context():
#    db.create_all()

@app.route('/')
def home():
    return "Bienvenido a la API de animales"


# Endpoint para obtener todos los animales
@app.route('/animales', methods=['GET'])
def obtener_animales():
    animales = Animal.query.all()
    resultado = {
        animal.nombre: {
            "id": animal.id,
            "tipo": animal.tipo,
            "raza": animal.raza,
            "color": animal.color,
            "foto": animal.foto,
            "fecha_nacimiento": animal.fecha_nacimiento,
            "vacunas": {vacuna.nombre: vacuna.fecha for vacuna in animal.vacunas}  # Vacunas del animal
        } for animal in animales
    }
    return jsonify(resultado)


# Endpoint para obtener un animal espec?fico por nombre
@app.route('/animales/<string:nombre>', methods=['GET'])
def obtener_animal(nombre):
    animal = Animal.query.filter_by(nombre=nombre).first()
    if not animal:
        return jsonify({"mensaje": "Animal no encontrado"}), 404

    resultado = {
        animal.nombre: {
            "id": animal.id,
            "tipo": animal.tipo,
            "raza": animal.raza,
            "color": animal.color,
            "foto": animal.foto,
            "fecha_nacimiento": animal.fecha_nacimiento,
            "vacunas": {vacuna.nombre: vacuna.fecha for vacuna in animal.vacunas}
        }
    }
    return jsonify(resultado)

# Buscar animales por tipo, color o raza
@app.route('/animales/buscar', methods=['GET'])
def buscar_animales():
    tipo = request.args.get('tipo')
    color = request.args.get('color')
    raza = request.args.get('raza')

    query = Animal.query

    if tipo:
        query = query.filter(Animal.tipo == tipo)
    if color:
        query = query.filter(Animal.color == color)
    if raza:
        query = query.filter(Animal.raza == raza)

    animales = query.all()

    return jsonify([animal.as_dict() for animal in animales]), 200


# Endpoint para agregar un animal
@app.route('/animales', methods=['POST'])
def agregar_animal():
    datos = request.json
    # Verificar si el animal con el nombre ya existe
    if Animal.query.filter_by(nombre=datos["nombre"]).first():
        return jsonify({"mensaje": "Ya existe un animal con ese nombre"}), 400

    nuevo_animal = Animal(
        nombre=datos["nombre"],
        tipo=datos["tipo"],
        raza=datos["raza"],
        color=datos["color"],
        foto=datos.get("foto", None),
        fecha_nacimiento=datos.get("fecha_nacimiento", None)
    )
    db.session.add(nuevo_animal)
    db.session.commit()
    return jsonify({"mensaje": "Animal agregado correctamente"}), 201



# Endpoint para actualizar un animal por nombre
@app.route('/animales/<string:nombre>', methods=['PUT'])
def actualizar_animal(nombre):
    animal = Animal.query.get(nombre)
    if not animal:
        return jsonify({"mensaje": "Animal no encontrado"}), 404

    datos = request.json
    animal.tipo = datos.get("tipo", animal.tipo)
    animal.raza = datos.get("raza", animal.raza)
    animal.color = datos.get("color", animal.color)
    animal.nombre = datos.get("nombre", animal.nombre)

    db.session.commit()
    return jsonify({"mensaje": "Animal actualizado correctamente"})

# Endpoint para eliminar un animal por nombre (requiere autenticaci?n)
@app.route('/animales/<string:nombre>', methods=['DELETE'])
def eliminar_animal(nombre):
    clave_secreta = "API_CLAVE"  # Define una clave de autenticaci?n
    clave_usuario = request.headers.get("Authorization")

    if clave_usuario != clave_secreta:
        return jsonify({"mensaje": "No tienes permisos para eliminar animales"}), 403

    animal = Animal.query.get(nombre)
    if not animal:
        return jsonify({"mensaje": "Animal no encontrado"}), 404

    db.session.delete(animal)
    db.session.commit()
    return jsonify({"mensaje": "Animal eliminado correctamente"})

# Endpoint para agregar una vacuna a un animal
@app.route('/animales/<int:id>/vacunas', methods=['POST'])
def agregar_vacuna(id):
    animal = Animal.query.get(id)
    if not animal:
        return jsonify({"mensaje": "Animal no encontrado"}), 404

    datos = request.json
    nueva_vacuna = Vacuna(
        nombre=datos["nombre"],
        fecha=datos["fecha"],
        animal_id=id
    )
    db.session.add(nueva_vacuna)
    db.session.commit()
    return jsonify({"mensaje": "Vacuna agregada correctamente"}), 201

# Endpoint para obtener las vacunas de un animal
@app.route('/animales/<int:id>', methods=['GET'])
def obtener_animal_por_id(id):
    animal = Animal.query.get(id)
    if not animal:
        return jsonify({"mensaje": "Animal no encontrado"}), 404

    # Incluir las vacunas dentro de los datos del animal
    resultado = {
        "id": animal.id,
        "nombre": animal.nombre,
        "tipo": animal.tipo,
        "raza": animal.raza,
        "color": animal.color,
        "foto": animal.foto,
        "fecha_nacimiento": animal.fecha_nacimiento,
        "vacunas": {vacuna.nombre: vacuna.fecha for vacuna in animal.vacunas}  # Vacunas del animal
    }

    return jsonify(resultado)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)

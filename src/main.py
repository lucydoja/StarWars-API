"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Favorites
import datetime

## Nos permite hacer las encripciones de contraseñas
from werkzeug.security import generate_password_hash, check_password_hash

## Nos permite manejar tokens por authentication (usuarios) 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
#Este es para encriptar
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    
    result = list(map(lambda x: x.serialize_user(), users))

    return jsonify(result), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise APIException('This user is not in the database', status_code=404)
    result = user.serialize_user()

    return jsonify(result), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planetas = Planets.query.all()
    result = list(map(lambda x: x.serialize_planet(), planetas))

    return jsonify(result), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planeta = Planets.query.get(planet_id)
    if planeta is None:
        raise APIException('This planet doesnt exist', status_code=404)
    result = planeta.serialize_planet()

    return jsonify(result), 200

#You only have to do this once
@app.route('/planets', methods=['POST'])
def add_planet():
    lista=[]
    for i in range(1,11):
        people = requests.get(f"https://www.swapi.tech/api/planets/{i}").json()["result"]["properties"]
        lista.append(people)
    
    for request_body in lista:
        planeta = Planets(name=request_body["name"], population=request_body["population"], terrain=request_body["terrain"], diameter=request_body["diameter"], rotation_period=request_body["rotation_period"], orbital_period=request_body["orbital_period"], gravity=request_body["gravity"], url=request_body["url"], climate=request_body["climate"], surface_water=request_body["surface_water"], created=request_body["created"], edited=request_body["edited"])
        db.session.add(planeta)
        db.session.commit()

    return jsonify("Planets were added"), 200

@app.route('/people', methods=['GET'])
def get_people():
    personas = People.query.all()
    result = list(map(lambda x: x.serialize_people(), personas))

    return jsonify(result), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    persona = People.query.get(people_id)
    if persona is None:
        raise APIException('This person doesnt exist', status_code=404)
    result = persona.serialize_people()
    return jsonify(result), 200

#You only have to do this once
@app.route('/people', methods=['POST'])
def add_people():
    lista=[]
    for i in range(1,11):
        people = requests.get(f"https://www.swapi.tech/api/people/{i}").json()["result"]["properties"]
        lista.append(people)
    
    for request_body in lista:
        persona = People( name=request_body["name"], height=request_body["height"], mass=request_body["mass"], hair_color=request_body["hair_color"], skin_color=request_body["skin_color"], eye_color=request_body["eye_color"], birth_year=request_body["birth_year"], url=request_body["url"], created=request_body["created"], edited=request_body["edited"], homeworld=request_body["homeworld"], gender=request_body["gender"])
        db.session.add(persona)
        db.session.commit()

    return jsonify("Characters were added"), 200

@app.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()
    
    if user is None:
        raise APIException('This user is not in the database', status_code=404)
    
    user_id = user.id
    todos = Favorites.query.all()
    lista_favs = list(map(lambda x: x.serialize_favorites(), todos))
    user_favs = list(filter( lambda x: x["user_id"] == user_id , lista_favs))
    if len(lista_favs) == 0:
        result = []
        
    else :
        favoritos = list(map( lambda x: x["fav_name"], user_favs))
        result = favoritos
        
    
    return jsonify(result), 200
    

@app.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()
    
    if user is None:
        raise APIException('This user is not in the database', status_code=404)

    user_id = user.id
    personas = People.query.all()
    people = list(map(lambda x: x.serialize_people(), personas))

    planetas = Planets.query.all()
    planets = list(map(lambda x: x.serialize_planet(), planetas))

    # recibir info del request
    request_body = request.get_json()
    fav= Favorites.check_existance("algo", request_body["fav_name"], planets, people)
    if fav is None:
        raise APIException('This planet or character doesnt exist', status_code=404)
    favorito = Favorites(user_id = user_id, fav_name=fav)
    db.session.add(favorito)
    db.session.commit()

    #mandarlos favs de nuevo
    todos = Favorites.query.all()
    lista_favs = list(map(lambda x: x.serialize_favorites(), todos))
    user_favs = list(filter( lambda x: x["user_id"] == user_id , lista_favs))
    if len(lista_favs) == 0:
        result = []
        
    else :
        favoritos = list(map( lambda x: x["fav_name"], user_favs))
        result = favoritos

    return jsonify(result), 200

@app.route('/favorites/<fav_name>', methods=['DELETE'])
@jwt_required()
def del_favorite(fav_name):
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        raise APIException('This user is not in the database', status_code=404)

    user_id = user.id
    fav = Favorites.query.filter_by(fav_name=fav_name, user_id=user_id).first()
    if fav is None:
        raise APIException('Favorite not found', status_code=404)

    db.session.delete(fav)
    db.session.commit()

    #mandarlos favs de nuevo
    todos = Favorites.query.all()
    lista_favs = list(map(lambda x: x.serialize_favorites(), todos))
    user_favs = list(filter( lambda x: x["user_id"] == user_id , lista_favs))
    if len(user_favs) == 0:
        result = []
        
    else :
        favoritos = list(map( lambda x: x["fav_name"], user_favs))
        result = favoritos

    return jsonify(result), 200

@app.route('/Allfavorites', methods=['DELETE'])
@jwt_required()
def del_favorites():
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        raise APIException('This user is not in the database', status_code=404)

    user_id = user.id
    
    #borrarlos
    user_favs = Favorites.query.filter_by(user_id=user_id)
    for items in user_favs:
        db.session.delete(items)
        db.session.commit()

    #mandarlos favs de nuevo
    todos = Favorites.query.all()
    lista_favs = list(map(lambda x: x.serialize_favorites(), todos))
    user_fav = list(filter( lambda x: x["user_id"] == user_id , lista_favs))
    if len(user_fav) == 0:
        result = [] 
        
    else :
        favoritos = list(map( lambda x: x["fav_name"], user_fav))
        result = favoritos

    return jsonify(result), 200

@app.route('/register', methods=["POST"])
def user_register():
    if request.method == 'POST':
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        user_name = request.json.get("user_name", None)
        first_name = request.json.get("first_name", None)
        last_name = request.json.get("last_name", None)

        if not email:
            return jsonify("Email is required"), 400
        if not password:
            return jsonify("Password is required"), 400
        if not user_name:
            return jsonify("Username is required"), 400
        if not first_name:
            return jsonify("First name is required"), 400
        if not last_name:
            return jsonify("Last name is required"), 400

        correo = User.query.filter_by(email=email).first()
        if correo:
            return jsonify("This email is already registered"), 400
        usuario = User.query.filter_by(user_name=user_name).first()
        if usuario:
            return jsonify("Username already in use"), 400

        #tenemos que guardar el password de forma encriptada
        hashed_password = generate_password_hash(password)
        user = User( email=email, password=hashed_password, user_name=user_name, first_name=first_name, last_name=last_name)

         #Otra forma de llamar las propiedades de una clase
        '''
        user = User()
        user.email = email'''
        
        db.session.add(user)
        db.session.commit()

        return jsonify("Thanks. Your register was successful"), 200

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user_name= request.json.get("user_name", None)
        password = request.json.get("password", None)

        if not user_name:
            return jsonify("Username is required"), 400
        if not password:
            return jsonify("Password is required"), 400

        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify("Username/Password are incorrect"), 401
           

        #funcion check le meto el valor a comparar que es el pass del user en la clase, luego el valor que recibo
        if not check_password_hash(user.password, password):
            return jsonify("Username/Password are incorrect"), 401

        # crear el token
        expiracion = datetime.timedelta(days=1)
        access_token = create_access_token(identity=user.user_name, expires_delta=expiracion)

        #esto permite agarrar el token generado del otro lado 
        data = {
            
            "token": access_token,
            "expires": expiracion.total_seconds()*1000,
            
        }

        return jsonify(data), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

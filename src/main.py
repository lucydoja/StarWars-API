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
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

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

    return jsonify("Planets added"), 200

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

    return jsonify("Characters added"), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    todos = Favorites.query.all()
    lista_favs = list(map(lambda x: x.serialize_favorites(), todos))
    user_favs = list(filter( lambda x: x["user_id"] == user_id , lista_favs))
    favoritos = list(map( lambda x: {"fav_id" : x["id"], "fav_name" : x["fav_name"]}, user_favs))
    result={
        "user_id" : user_id,
        "favoritos" : favoritos,
    }
    return jsonify(result), 200
    

@app.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise APIException('This user is not in the database', status_code=404)

    personas = People.query.all()
    people = list(map(lambda x: x.serialize_people(), personas))

    planetas = Planets.query.all()
    planets = list(map(lambda x: x.serialize_planet(), planetas))

    # recibir info del request
    request_body = request.get_json()
    favorito = Favorites(user_id = user_id, fav_name=Favorites.check_existance("algo", request_body["fav_name"], planets, people))
    db.session.add(favorito)
    db.session.commit()

    return jsonify("Favorite added"), 200

@app.route('/favorites/<int:favo_id>', methods=['DELETE'])
def del_favorite(favo_id):

    # recibir info del request
    
    fav = Favorites.query.get(favo_id)
    if fav is None:
        raise APIException('Favorite not found', status_code=404)

    db.session.delete(fav)

    db.session.commit()

    return jsonify("Favorite deleted"), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

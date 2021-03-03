from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    favorites = db.relationship('Favorites', lazy=True)
    

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize_user(self):
        return {
            "id": self.id,
            "user_name" : self.user_name,
            "first_name" : self.first_name,
            "last_name" : self.last_name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }



class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fav_name = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<Favorites %r>' % self.id

    def serialize_favorites(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fav_name": self.fav_name
        }

    def check_existance(self, variable, planets, people, favorites):
        planetas = list(filter(lambda x : x["name"]==variable, planets))
        personas = list(filter(lambda x : x["name"]==variable, people))
        favoritos = list(filter(lambda x : x==variable, favorites))
        return variable if  len(planetas) > 0 or len(personas) > 0 and len(favoritos)==0 else None



    
class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    population = db.Column(db.String(250))
    terrain = db.Column(db.String(250))
    diameter = db.Column(db.String(250))
    rotation_period = db.Column(db.String(250))
    orbital_period = db.Column(db.String(250))
    gravity = db.Column(db.String(250))
    climate = db.Column(db.String(250))
    surface_water = db.Column(db.String(250))
    created = db.Column(db.String(250))
    edited = db.Column(db.String(250))
    url = db.Column(db.String(250), unique=True, nullable=False)

    def __repr__(self):
        return '<Planets %r>' % self.id

    def serialize_planet(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "terrain" : self.terrain,
            "diameter" : self.diameter,
            "rotation_period" : self.rotation_period,
            "orbital_period" : self.orbital_period,
            "gravity" : self.gravity,
            "climate" : self.climate,
            "surface_water" : self.surface_water,
            "created" : self.created,
            "edited" : self.edited,
            "url" : self.url
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    height = db.Column(db.String(250))
    mass = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    skin_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    birth_year = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    created = db.Column(db.String(250))
    edited = db.Column(db.String(250))
    homeworld = db.Column(db.String(250))
    url = db.Column(db.String(250), unique=True, nullable=False)
    
    def __repr__(self):
        return '<People %r>' % self.id

    def serialize_people(self):
        return {
            "id": self.id,
            "name": self.name,
            "height" : self.height,
            "mass" : self.mass,
            "hair_color" : self.hair_color,
            "skin_color" : self.skin_color,
            "eye_color" : self.eye_color,
            "birth_year" : self.birth_year,
            "gender" : self.gender,
            "created" : self.created,
            "edited" : self.edited,
            "homeworld" : self.homeworld,
            "url" : self.url
        }
    
    


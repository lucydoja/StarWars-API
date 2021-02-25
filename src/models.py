from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
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
    



class Planets(db.Model):
    id = db.Column(db.String(250), primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    population = db.Column(db.String(250))
    terrain = db.Column(db.String(250))
    diameter = db.Column(db.String(250))
    rotation_period = db.Column(db.String(250))
    orbital_period = db.Column(db.String(250))
    gravity = db.Column(db.String(250))
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
            "url" : self.url
        }

class People(db.Model):
    id = db.Column(db.String(250), primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    height = db.Column(db.String(250))
    mass = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    skin_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    birth_year = db.Column(db.String(250))
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
            "url" : self.url
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planet_name = db.Column(db.String(250), db.ForeignKey('Planets.name'))
    planet_id = db.Column(db.String(250), db.ForeignKey('Planets.id'))
    people_name = db.Column(db.String(250), db.ForeignKey('People.name'))
    people_id = db.Column(db.String(250), db.ForeignKey('People.id'))
    

    def __repr__(self):
        return '<Favorites %r>' % self.id

    def serialize_favorites(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_name": self.planet_name,
            "planet_id" : self.planet_id,
            "people_name" : self.people_name,
            "people_id" : self.people_id
        }


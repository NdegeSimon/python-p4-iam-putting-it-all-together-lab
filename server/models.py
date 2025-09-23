from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, ForeignKey, FLOAT

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    _password_hash =db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)


    recipes = db.relationship('Recipe', back_populates = 'user')

    serialize_rules = ('-recipes.user',)

    def __repr__(self):
        return f'< User {self.id} {self.username}'
    

    @hybrid_property
    def password_hash(self):
        raise AttributeError("password hashes may not be viewd")
    
    @password_hash.setter
    def password_hash(self,password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')


    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    instructions = db.Column(db.String, nullable = False)
    minutes_to_complete = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates = 'recipes')
    serialize_rules = ('-user.recipes',)

    def __repr__(self):
        return f'<Recipe {self.id} {self.title}>'
    


    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
          raise ValueError("Instructions must be at least 50 characters long")
        return instructions



    
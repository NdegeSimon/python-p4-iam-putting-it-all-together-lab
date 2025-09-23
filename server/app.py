from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = User(
               username = data.get('username'),
               image_url =data.get('image_url'),
               bio = data.get('bio')
            )
            user.password_hash = data.get('password')
            db.session.add(user)
            db.session.commit()
            session ['user_id'] = user.id
            return user.to_dict(),201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422



class CheckSession(Resource):
    def get (self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']) .first()
            return user.to_dict(), 200
        return {'error': '401 Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username = username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'error': '401 Unauthorized'} , 401

class Logout(Resource):
    def delete(self):
       if session.get('user_id'):
           session['user_id'] = None
           return {}, 204
       return {
           'error': '401 Unauthorized'
       }, 401
    

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': '401 Unauthorized'}, 401
        recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
        return recipes, 200
    
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': '401 Unauthorized'}, 401
        data = request.get_json()
        try:
            recipe = Recipe(
                title = data.get('title'),
                instructions = data.get('instructions'),
                minutes_to_complete = data.get('minutes_to_complete'),
                user_id = user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 422
        

        

        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
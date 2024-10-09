#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)

    def patch(self, id):
        # Find the plant by ID
        plant = Plant.query.filter_by(id=id).first()

        # If the plant does not exist, return a 404 error
        if not plant:
            return make_response(jsonify({'error': 'Plant not found'}), 404)

        # Get JSON data from the request
        data = request.get_json()

        # Validate that the 'is_in_stock' field is provided in the request
        if 'is_in_stock' not in data:
            return make_response(jsonify({'error': '"is_in_stock" field is required'}), 400)

        try:
            # Update the plant's 'is_in_stock' field
            plant.is_in_stock = data['is_in_stock']

            # Commit the changes to the database
            db.session.commit()

            # Return the updated plant data as JSON
            return make_response(jsonify(plant.to_dict()), 200)

        except Exception as e:
            # In case of an error, rollback the transaction
            db.session.rollback()
            # Return an error response with the exception message
            return make_response(jsonify({'error': str(e)}), 500)
        
    def delete(self, id):
        # Find the plant by ID
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            # If the plant is not found, return a 404 response
            return make_response(jsonify({'error': 'Plant not found'}), 404)
        
        try:
            # Delete the plant from the database
            db.session.delete(plant)
            db.session.commit()

            # Return an empty response with a 204 No Content status code
            return make_response('', 204)
        except Exception as e:
            # Rollback the transaction in case of an error
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to delete plant', 'message': str(e)}), 500)

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

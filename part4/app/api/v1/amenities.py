from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new amenity"""
        try:
            amenity_data = api.payload
            new_amenity = facade.create_amenity(amenity_data)
            return {'id': new_amenity.id, 'name': new_amenity.name}, 201
        except ValueError as error:
            return {'error': str(error)}, 400

    def get(self):
        """Retrieve a list of all amenities"""

        all_amenities = facade.get_all_amenities()

        amenities_list = [amenity.to_dict() for amenity in all_amenities]

        return amenities_list, 200

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')

    def get(self, amenity_id):
        """Get amenity details by ID"""

        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            api.abort(404, 'Amenity not found')

        return amenity.to_dict(), 200

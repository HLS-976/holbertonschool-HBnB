from app.services import facade
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('admin', description='Admin operations')

user_model = api.model(
    'User', {
        'first_name': fields.String(
            required=True, description='First name of the user'),
        'last_name': fields.String(
            required=True, description='Last name of the user'),
        'password': fields.String(
            required=True, description='User\'s password'),
        'email': fields.String(
            required=True, description='Email of the user'),
        'is_admin': fields.Boolean(description='Admin flag',
                                   exemple=True)
    }
)

@api.route('/users/')
class AdminUserCreate(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.doc(security='token')
    @jwt_required()
    def post(self):
        """Create a new user (Admin only)"""
        user_data = api.payload
        print("Payload received:", api.payload)
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        email = user_data.get('email')

        # Check if email is already in use
        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400


        try:
            new_user = facade.create_user(user_data)
            return {
                'id': new_user.id,
                'message': 'User successfully created'
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except TypeError as e:
            return {'error': str(e)}, 400


@api.route('/users/<user_id>')
class AdminUserModify(Resource):
    @api.expect(user_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.doc(security='token')
    @jwt_required()
    def put(self, user_id):
        user_data = api.payload
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        email = user_data.get('email')

        # Ensure email uniqueness
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        try:
            updated_user = facade.update_user(user_id, user_data)
            return {
                'id': updated_user.id,
                'message': 'User successfully updated'
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except TypeError as e:
            return {'error': str(e)}, 400


@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.doc(security='token')
    @jwt_required()
    def post(self):
        amenity_data = api.payload
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # amenity_data = request.json
        name = amenity_data.get('name')

        # Check if amenity name is already in use
        if facade.get_amenity_by_name(name):
            return {'error': 'Amenity name already exists'}, 400

        try:
            new_amenity = facade.create_amenity(amenity_data)
            return {
                'id': new_amenity.id,
                'message': 'Amenity successfully created'
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except TypeError as e:
            return {'error': str(e)}, 400


@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.doc(security='token')
    @jwt_required()
    def put(self, amenity_id):
        amenity_data = api.payload
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            updated_amenity = facade.update_amenity(amenity_id, amenity_data)
            return {
                'id': updated_amenity.id,
                'message': 'Amenity successfully updated'
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except TypeError as e:
            return {'error': str(e)}, 400
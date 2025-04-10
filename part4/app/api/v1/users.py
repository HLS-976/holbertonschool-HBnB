import re
from app import bcrypt
from app.services import facade
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user"""
        user_data = api.payload

        # Validate first and last name
        if not user_data['first_name'].strip():
            api.abort(400, "First name must be a non-empty string")

        if not user_data['last_name'].strip():
            api.abort(400, "Last name must be a non-empty string")

        # Validate email
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\.[a-zA-Z]{2,})?$"
        if not re.match(email_pattern, user_data['email']):
            api.abort(400, "Invalid email format")

        if facade.get_user_by_email(user_data['email']):
            api.abort(400, "Email already registered")


        try:
            new_user = facade.create_user(user_data)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))

        return new_user.display(), 201

    @api.response(200, "Successfully retrieved user list")
    def get(self):
        """Retrieve all users"""
        users = facade.get_all_users()
        return [{"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "email": user.email} for user in users], 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.doc(security='token')
    @jwt_required()
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }, 200

    @api.doc(security='token')
    @jwt_required()
    @api.expect(user_model)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def put(self, user_id):
        """Update user"""
        user_data = api.payload
        current_user = facade.get_user(get_jwt_identity())

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        if not current_user.is_admin and str(user.id) != str(current_user.id):
            return {'error': 'Unauthorized action'}, 403

        if 'email' in user_data or 'password' in user_data:
            return {'error': 'You cannot modify email or password'}, 400

        try:
            user.update(user_data)
            updated_user = facade.update_user(user_id, user.display())
        except (ValueError, TypeError) as e:
            api.abort(400, f"Error: {str(e)}")

        return updated_user.display(), 200

    @api.doc(security='token')
    @jwt_required()
    @api.response(204, 'User successfully deleted')
    @api.response(404, 'User not found')
    def delete(self, user_id):
        """Delete user"""
        current_user = facade.get_user(get_jwt_identity())

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        if not current_user.is_admin and str(user.id) != str(current_user.id):
            return {'error': 'Unauthorized action'}, 403

        facade.delete_user(user_id)
        return '', 204

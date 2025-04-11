from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

api = Namespace('admin', description='Admin operations')

user_model_admin = api.model('User', {
    'first_name': fields.String(required=True, description="User first name", example="John"),
    'last_name': fields.String(required=True, description="User last name", example="Doe"),
    'email': fields.String(required=True, description="User email", example="john@email.com"),
    'password': fields.String(required=True, description="User password", example="Johnd0e!")
})

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

place_model = api.model('Place', {
        'title': fields.String(required=True, description='Title of the place', example='Great house'),
        'description': fields.String(description='Description of the place', example='A nice place to stay'),
        'price': fields.Float(required=True, description='Price per night', example=100.0),
        'latitude': fields.Float(required=True, description='Latitude of the place', example=-75.102),
        'longitude': fields.Float(required=True, description='Longitude of the place', example=-122.4194)
})

review_model_admin = api.model('Review', {
    'text': fields.String(description='Text of the review', example="Pablo is the best thank you"),
    'rating': fields.Integer(description='Rating of the place (1-5)', example=5),
})

"""User admin"""
@api.route('/users/')
class AdminUserCreate(Resource):
    @api.expect(user_model_admin)
    @api.response(201, 'User successfully created')
    @api.response(403, 'Admin privileges required')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    @api.doc(security="token")
    
    def post(self):

        current_user = get_jwt_identity()

        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload
        email = user_data.get('email')

        if facade.get_user_by_email(email):
            api.abort(400, 'Email already registered')

        try:
            new_user = facade.create_user(user_data)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))

        return new_user.to_dict(), 201

@api.route('/users/<user_id>')
class AdminUserModify(Resource):
    @api.expect(user_model_admin)
    @api.response(201, 'User successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'User not found')
    @jwt_required()
    @api.doc(security="token")

    def put(self, user_id):

        current_user = get_jwt_identity()

        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        
        user = facade.get_user(user_id)

        if not user:
            api.abort(404, 'User not found')

        user_data = api.payload
        email = user_data.get('email')

        # Ensure email uniqueness
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        try:
            user.update(user_data)
            updated_user = facade.update_user(user_id, user.to_dict())
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))

        return updated_user.to_dict(), 201

"""Places admin"""
@api.route('/places/<place_id>')
class AdminPlaceModify(Resource):
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @jwt_required()
    @api.doc(security="token")

    def put(self, place_id):

        current_user = get_jwt_identity()

        if not current_user.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        place_data = api.payload
        place = facade.get_place(place_id)

        if not place:
            api.abort(404, "Place not found")

        amenities = []

        if 'amenities' in place_data:
            amenities = place_data.pop("amenities")

        if "owner_id" in place_data:
            api.abort(400, 'Invalid input data')

        try:
            place.update(place_data)
            facade.update_place(place_id, place.to_dict(), amenities)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))
        
        return {
            "title": place.title,
            "description": place.description,
            "price": place.price,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "owner_id": place.owner_id
            }, 200
    
    @api.response(200, 'Place deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @jwt_required()
    
    def delete(self, place_id):
       
        current_user = get_jwt_identity()

        place = facade.get_place(place_id)

        if not current_user.get('is_admin'):
            api.abort(403, 'Admin privileges required')
            
        if not place:
            api.abort(404, "Place not found")

        facade.delete_place(place_id)
        return {"message": "Place deleted successfully"}, 200
    
"""Review admin"""
@api.route('/review/<review_id>')
class AdminReviewModify(Resource):

    @api.expect(review_model_admin)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')    
    @jwt_required()
    @api.doc(security="token")

    def put(self, review_id):

        current_user = get_jwt_identity().get('id')
        admin_user = facade.get_user(current_user)
        review = facade.get_review(review_id)

        if not admin_user or not admin_user.is_admin:
            api.abort(403, 'Admin privileges required')

        if not review:
            api.abort(404, "Review not found")

        review_data = api.payload

        valid_inputs = ["rating", "text"]
        for input in valid_inputs:
            if input not in review_data:
                api.abort(400, "Invalid input data")

        try:
            review.update(review_data)
            facade.update_review(review_id, review_data)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))

        return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review._user_id,
                'place_id': review._place_id
            }, 200
    
    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    @api.doc(security="token")

    def delete(self, review_id):

        current_user = get_jwt_identity()

        if not current_user.get('is_admin'):
            api.abort(403, 'Admin privileges required')
        
        review = facade.get_review(review_id)
        
        if not review:
            api.abort(404, "Review not found")

        facade.delete_review(review_id)
        
        return {"message": "Review deleted successfully"}, 200


"""amenities admin"""
@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    @api.doc(security="token")
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()

    def post(self):
        current_user = get_jwt_identity()
        amenity_data = api.payload
    
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        existing_amenity = facade.get_amenity_by_name(amenity_data['name'])

        if existing_amenity:
            api.abort(400, 'Amenity already registered')
        
        try:
            new_amenity = facade.create_amenity(amenity_data)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))
            
        return new_amenity.to_dict(), 201


@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    @jwt_required()
    @api.doc(security="token")

    def put(self, amenity_id):
        current_user = get_jwt_identity()
        amenity_data = api.payload

        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            api.abort(404, "Amenity not found")
        
        existing_amenity = facade.get_amenity_by_name(amenity_data['name'])

        if existing_amenity and existing_amenity.id != amenity.id:
            api.abort(400, "Amenity name already exists")

        try:
            updated_amenity = facade.update_amenity(amenity_id, amenity_data)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))
        return updated_amenity.to_dict(), 200

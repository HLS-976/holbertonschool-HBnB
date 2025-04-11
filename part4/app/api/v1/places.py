from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db

api = Namespace('places', description='Place operations')


# Define the place model for input validation and documentation
place_model = api.model('Place', {
        'title': fields.String(required=True, description='Title of the place', example='Great house'),
        'description': fields.String(description='Description of the place', example='A nice place to stay'),
        'price': fields.Float(required=True, description='Price per night', example=100.0),
        'latitude': fields.Float(required=True, description='Latitude of the place', example=-75.102),
        'longitude': fields.Float(required=True, description='Longitude of the place', example=-122.4194)
})                           

place_update_model = api.model('Place Update', {
        'title': fields.String(description='Title of the place', example='Great house at the beach'),
        'description': fields.String(description='Description of the place', example='A nice place for holidays'),
        'price': fields.Float(description='Price per night', example=150.0),
        'latitude': fields.Float(description='Latitude of the place', example=-75.102),
        'longitude': fields.Float(description='Longitude of the place', example=-122.4194),
        'amenities': fields.List(fields.String(description='List of amenity IDs'), example=["99493758-3936-4aac-8a07-835b84ce02ef"])
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.doc(security="token")
    @jwt_required()

    def post(self):
        """Register a new place"""

        current_user = get_jwt_identity().get('id')
        user = facade.get_user(current_user)
        
        if not user:
            api.abort(403, "Unauthorized action")

        place_data = api.payload
        place_data["owner_id"] = user.id
        amenities = place_data.pop("amenities", [])

        try:    
            new_place = facade.create_place(place_data, amenities)
            place_dict = new_place.to_dict()
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))

        return place_dict, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        return [
            {
                "id": all_place.id,
                "title": all_place.title,
                "price": all_place.price,
                "latitude": all_place.latitude,
                "longitude": all_place.longitude,
            } for all_place in places
        ],200


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')

    def get(self, place_id):
        """Get place details by ID"""

        place = facade.get_place(place_id)
        
        if not place:
            api.abort(404, "Place not found")

        user_data = place.owner.to_dict()
        reviews_data = [review.to_dict() for review in place.reviews]
        amenities_data = [amenity.to_dict() for amenity in place.place_amenities]            

        return {'id': place.id,
                'title': place.title,
                'descripton': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'owner': user_data,
                'amenities': amenities_data,
                'reviews': reviews_data
                }, 200

    @jwt_required()
    @api.expect(place_update_model)
    @api.response(200, 'Place updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    @api.doc(security="token")

    def put(self, place_id):
        """Update a place's information"""

        current_user = get_jwt_identity()
        place = facade.get_place(place_id)

        if not place:
            return {'message': 'Invalid input data'}, 400
        
        if current_user['id'] != place.owner_id:
            return{'error': 'Unauthorized action'}, 403
        
        place_data = api.payload

        if 'amenities' in place_data:
            amenities = []
            amenities = place_data.pop("amenities")
        
        if "owner_id" in place_data:
            api.abort(400, 'Invalid input data')

        try:
            place.update(place_data)
            facade.update_place(place_id, place.to_dict(), amenities)
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))
        
        return {"message": "Place updated successfully"}, 200


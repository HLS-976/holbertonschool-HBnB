from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db

api = Namespace('reviews', description='Review operations')


review_model = api.model('Review', {
        'text': fields.String(required=True, description='Text of the review', example="Super cool!"),
        'rating': fields.Integer(required=True, description='Rating of the place (1-5)', example=5),
        'place_id': fields.String(required=True, description='ID of the place', example="32491cac-9dfa-4c76-bcd6-499421c5c269")
})

review_update_model = api.model('Review Update', {
    'text': fields.String(description='Text of the review', example="Pablo is the best thank you"),
    'rating': fields.Integer(description='Rating of the place (1-5)', example=5),
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    @api.doc(security="token")

    def post(self):
        """Register a new review"""

        current_user = get_jwt_identity().get('id')
        user = facade.get_user(current_user)
        
        review_data = api.payload
        
        place = facade.get_place(review_data.get("place_id"))
        
        if not place:
            api.abort(400, "Invalid place")
        
        if not user or user.id == place.owner_id:
            api.abort(403, "Unauthorized action")
        
        review_data["user_id"] = user.id

        place_reviews = facade.get_reviews_by_place(place.id)
        if any(review.user_id == user.id for review in place_reviews):
            api.abort(400, "Place already reviewed")
        
        review_data["place_id"] = place.id

        try:
            new_review = facade.create_review(review_data)
            review_dict = new_review.to_dict()
        except (ValueError, TypeError) as e:
            api.abort(400, str(e))

        return review_dict, 201

    @api.response(200, 'List of reviews retrieved successfully')

    def get(self):
        """Retrieve a list of all reviews"""

        reviews = facade.get_all_reviews()
        return [
            {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user_id,
                'place_id': review.place_id
            } for review in reviews
        ], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')

    def get(self, review_id):
        """Get review details by ID"""

        try:
            review = facade.get_review(review_id)
            if not review:
                return {'error': 'Review not found'}, 404
            
            return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user_id,
                'place_id': review.place_id
            }, 200
        except ValueError as error:
            return {'error': str(error)}, 400

    @api.expect(review_update_model)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Review not found')
    @jwt_required()
    @api.doc(security="token")

    def put(self, review_id):
        """Update a review's information"""

        current_user = get_jwt_identity().get('id')
        user = facade.get_user(current_user)        
        review = facade.get_review(review_id)
        
        if not review:
            api.abort(404, "Review not found")

        if not user or user.id != review.user_id:
            api.abort(403,'Unauthorized action')

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

        return {"message": "Review updated successfully"}, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    @api.doc(security="token")

    def delete(self, review_id):
        """Delete a review"""

        cur_user = get_jwt_identity()
        user = facade.get_user(cur_user)
        review = facade.get_review(review_id)
        
        if not review:
            api.abort(404,"Review not found")

        if not user or user.id != review.user_id:
            api.abort(403,'Unauthorized action')

        facade.delete_review(review_id)
        return {"message": "Review deleted successfully"}, 200


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""

        place = facade.get_place(place_id)

        if not place:
            api.abort(404, 'Place not found')
        
        reviews = facade.get_reviews_by_place(place.id)

        place_reviews = [
            {key: value for key, value in review.to_dict().items() if key not in ["user_id", "place_id"]}
            for review in reviews
        ]

        return place_reviews, 200

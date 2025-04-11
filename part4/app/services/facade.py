from app.models.user import User
from app.models.review import Review
from app.models.place import Place
from app.models.amenity import Amenity
from app.persistence.repository import UserRepository, PlaceRepository
from app.persistence.repository import ReviewRepository, AmenityRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()
        self.place_repo = PlaceRepository()

    # User methods
    def create_user(self, user_data):
        password = user_data.pop('password')
        user = User(**user_data)
        user.hash_password(password)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    def delete_user(self, user_id):
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        self.user_repo.delete(user)
        return user

    # Place Methods
    def create_place(self, place_data):
        place = Place(**place_data)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)
    
    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        return self.place_repo.update(place_id, place_data)

    def delete_place(self, place_id):
        return self.place_repo.delete(place_id)

    # Review Methods
    def create_review(self, review_data):
        review = Review(**review_data)
        return self.review_repo.add(review)

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def delete_review(self, review_id):
        return self.review_repo.delete(review_id)

    # Amenity Methods
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def delete_amenity(self, amenity_id):
        return self.amenity_repo.delete(amenity_id)
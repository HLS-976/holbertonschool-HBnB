from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository
from app import db

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        return self.model.query.filter_by(email=email).first()
    
class PlaceRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Place)
    def add(self, place, amenities):
        db.session.add(place)

        if amenities:
            amenities_ids = []
            for amenity_id in amenities:
                amenity = Amenity.query.filter_by(id=amenity_id).first()
                if amenity:
                    amenities_ids.append(amenity)
                else:
                    raise ValueError(f"Amenity {amenity_id} not found")

            place.place_amenities.extend(amenities_ids)

        db.session.flush()
        db.session.commit()
        return place
    
    def update(self, place_id, place_data, amenities):
        place = self.get(place_id)
        if place:
            for key, value in place_data.items():
                setattr(place, key, value)

            if amenities:
                place.place_amenities = []
                amenities_ids = []
                for amenity_id in amenities:
                    amenity = Amenity.query.filter_by(id=amenity_id).first()
                    if amenity:
                        amenities_ids.append(amenity)
                    else:
                        raise ValueError(f"Amenity {amenity_id} not found")

                place.place_amenities.extend(amenities_ids)

            db.session.flush()
            db.session.commit()
            return place
        return None
    
    def delete(self, place_id):
        place = self.get(place_id)
        if place:
            Review.query.filter(Review.place_id == place_id).delete(synchronize_session=False)
            
            db.session.delete(place)
            db.session.commit()

    def get_place(place_id, options=None):
        place = Place.query.filter_by(id=place_id)
        if options:
            place = place.options(*options)
        return place.first()

class AmenitiesRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Amenity)

class ReviewRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Review)

    def get_review_by_place(self, place_id):
        return self.model.query.filter_by(place_id=place_id).all()

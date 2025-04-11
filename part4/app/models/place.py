from app import db
from .basemodel import BaseModel
from sqlalchemy.orm import validates, relationship
from .relation import place_amenity


class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="places")
    reviews = relationship('Review', backref='places', lazy=True)
    place_amenities = db.relationship('Amenity', secondary=place_amenity, lazy='subquery', backref=db.backref('places', lazy=True))

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)

    @validates('title')
    def validate_title(self, key, value):
        if not value:
            raise TypeError("Title is required")
        if not isinstance(value, str):
            raise TypeError("Title value is not valid")
        if len(value) > 100:
            raise ValueError("Title is too long")
        return value

    @validates('description')
    def validate_description(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Description value is not valid")
        return value

    @validates('price')
    def validate_price(self, key, value):
        if not value:
            raise TypeError("Price is required")
        if not isinstance(value, (float, int)):
            raise TypeError("Price value is not valid")
        if value < 0:
            raise ValueError("Price must be a positive number")
        return value

    @validates('latitude')
    def validate_latitude(self, key, value):
        if not value:
            raise TypeError("Latitude is required")
        if not isinstance(value, float):
            raise TypeError("Latitude is not valid")
        if value < -90 or value > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return value

    @validates('longitude')
    def validate_longitude(self, key, value):
        if not value:
            raise TypeError("Longitude is required")
        if not isinstance(value, float):
            raise TypeError("Longitude is not valid")
        if value < -180 or value > 180:
            raise ValueError("Longitude must be between -180 and 180")
        return value
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

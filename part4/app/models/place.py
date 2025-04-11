import uuid
from app import db
from part4.app.models.basemodel import Baseclass
from sqlalchemy.orm import relationship, validates
from app.models.place_amenity import place_amenity
from sqlalchemy import Column, String, Float, Integer, ForeignKey


class Place(Baseclass):
    """
    Place class representing a location available for rent.
    """
    __tablename__ = 'places'

    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, default=0)

    # Relationships
    owner = relationship('User', back_populates='places')
    reviews = relationship('Review',
                           back_populates='place',
                           cascade="all, delete-orphan")
    amenities = db.relationship('Amenity', secondary=place_amenity,
                                lazy='subquery',
                                backref=db.backref('places', lazy=True))

    @validates('title')
    def validate_title(self, key, value):
        """Ensures title is a valid string and within limits."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Title must be a non-empty string")
        if len(value) > 100:
            raise ValueError("Title must be 100 characters or fewer")
        return value

    @validates('price')
    def validate_price(self, key, value):
        """Ensures price is a positive number."""
        if not isinstance(value, (float, int)) or value <= 0:
            raise ValueError("Price must be a positive number")
        return float(value)

    @validates('latitude')
    def validate_latitude(self, key, value):
        """Ensures latitude is within valid range."""
        if not isinstance(value, (float, int)) or not (-90.0 <= value <= 90.0):
            raise ValueError("Latitude must be between -90 and 90")
        return float(value)

    @validates('longitude')
    def validate_longitude(self, key, value):
        """Ensures longitude is within valid range."""
        if not isinstance(value,
                          (float, int)) or not (-180.0 <= value <= 180.0):
            raise ValueError("Longitude must be between -180 and 180")
        return float(value)

    @validates('rating')
    def validate_rating(self, key, value):
        """Ensures rating is between 1 and 5 if set."""
        if value is not None and \
        (not isinstance(value, int) or not (1 <= value <= 5)):
            raise ValueError("Rating must be an integer between 1 and 5")
        return value

    def to_dict(self):
        """Converts the Place object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_id": self.owner_id,
            "rating": self.rating
        }

    def __str__(self):
        return f"Place: {self.title} (Owner ID: {self.owner_id})"

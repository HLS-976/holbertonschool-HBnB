from .basemodel import BaseModel
from app import db
from sqlalchemy.orm import validates


class Review(BaseModel):
    __tablename__ = 'reviews'

    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    

    @validates('text')
    def validate_text(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Text is not valid")
        if not value:
            raise TypeError("Text is required")
        return value

    @validates('rating')
    def validate_rating(self, key, value):
        if not value:
            raise TypeError("Rating is required")
        if not isinstance(value, int):
            raise TypeError("Rating is not valid")
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5")
        return value
    
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "user_id": self.user_id,
            "place_id": self.place_id
        }

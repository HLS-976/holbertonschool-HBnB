from app import db, bcrypt
from .basemodel import BaseModel
from sqlalchemy.orm import validates, relationship
import re

class User(BaseModel):     
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    places = relationship('Place', backref='users', lazy=True)
    
    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password"""
        return bcrypt.check_password_hash(self.password, password)

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    @validates("email", include_backrefs=False)
    def validateemail(self, key, value):
        regex = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$'
        if not re.match(regex, value):
            return {"error": "Invalid email format"}
        return value 
    
    @validates('first_name', 'last_name')
    def validate_first_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key.replace("_", " ")).capitalize())
        if len(value.replace(" ", "")) < 2 or len(value.replace(" ", "")) > 50:
            raise ValueError("{} must have between 2 and 50 characters".format(key.replace("_", " ")).capitalize())
        return value
    
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }

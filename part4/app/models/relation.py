from sqlalchemy import Table, Column, Integer, String, ForeignKey
from app import db

place_amenity = db.Table('place_amenity',
    Column('place_id', db.String(36), ForeignKey('places.id'), primary_key=True),
    Column('amenity_id', db.String(36), ForeignKey('amenities.id'), primary_key=True)
)

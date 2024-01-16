from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship("Mission", back_populates="planet", cascade="all, delete-orphan")
    scientists = association_proxy('missions', 'scientist')
    
    # Add serialization rules
    serialize_rules = ("-missions",)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship("Mission", back_populates="scientist", cascade="all, delete-orphan")
    planets = association_proxy('missions', 'planet')

    # Add serialization rules
    serialize_rules = ("-missions",)

    # Add validation
# must have a name, and a field_of_study
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name) < 1:
            raise ValueError("Scientist must have a name")
        return name
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if not field_of_study or len(field_of_study) < 1:
            raise ValueError('Scientist must have field of study.')
        return field_of_study


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    # Add relationships
    planet = db.relationship("Planet", back_populates="missions")
    scientist = db.relationship("Scientist", back_populates="missions")

    # Add serialization rules
    serialize_rules = ("-scientist","-planet")

    # Add validation
# must have a name, a scientist_id and a planet_id
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name) < 1:
            raise ValueError('Mission must have name.')
        return name
    
    @validates('scientist_id')
    def validate_scientist(self, key, scientist_id):
        if scientist_id is not None:
            return scientist_id
        raise ValueError('Mission must have scientist ID.')
    
    @validates('planet_id')
    def validate_planet(self, key, planet_id):
        if planet_id is not None:
            return planet_id
        raise ValueError('Mission must have planet ID.')

# add any models you may need.

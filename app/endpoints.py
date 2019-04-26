from app.helper import *
from marshmallow import Schema, fields as ma_fields, post_load, validates_schema, ValidationError
import logging
from flask_restplus import Resource, fields, marshal_with, Namespace, Api
import json
from flask import Blueprint

log = logging.getLogger(__name__)

placebp = Blueprint('place', __name__)
ns_place = Namespace(
    'similar', description='Get places with simlar Revenue,Tax,Expenditures etc.,')

api = Api(placebp, version='1.0',
          title='TruthTree ML API',
          description='APIs supported by ML')

api.add_namespace(ns_place)

year_range = ns_place.model('Year range',
                            {'start': fields.Integer(default=1967, description="Starting year"),
                             'end': fields.Integer(default=2016, description="Ending year")})

PlaceSingle = ns_place.model('Similar places for single attribute',
                             {'id': fields.Integer(required=True, description="Place ID"),
                              'place_type': fields.Integer(required=True, description="Type of place, Ex. state(0), county(1), city(2)"),
                              'attribute': fields.Integer(required=True, description="Attribute ID"),
                              'normalize_by': fields.Integer(description="Attribute to normalize the data, default = 1 (Population)", default=1),
                              'year_range': fields.Nested(year_range, description="Year Range between 1967 and 2016"),
                              'count': fields.Integer(2, description="Number of similar places in the output")})

PlaceMulti = ns_place.model('Similar places for multiple attributes',
                            {'id': fields.Integer(required=True, description="Place ID"),
                             'place_type': fields.Integer(required=True, description="Type of place, Ex. state(0), county(1), city(2)"),
                             'year': fields.Integer(required=True, description="Year"),
                             'attribute': fields.List(fields.Integer, required=True, description="List of attribute IDs"),
                             'normalize_by': fields.Integer(description="Attribute to normalize the data, default = 1 (Population)", default=1),
                             'count': fields.Integer(2, description="Number of similar places in the output")})


class YearRangeSchema(Schema):
    start = ma_fields.Integer()
    end = ma_fields.Integer()

    @validates_schema
    def validate_input(self, data):
        if data['start'] < 1967 or data['end'] > 2016:
            raise ValidationError(
                "Only years between 1967 and 2016 are supported(inclusive)")


class PlaceSingleSchema(Schema):
    id = ma_fields.Integer()
    attribute = ma_fields.Integer()
    place_type = ma_fields.Integer()
    count = ma_fields.Integer()
    normalize_by = ma_fields.Integer()
    year_range = ma_fields.Nested(YearRangeSchema)

    @validates_schema
    def validate_input(self, data):
        errors = {}
        if data['place_type'] not in [0, 1, 2]:
            errors['place_type'] = [
                'Unsupported place type, use 0 (for state), 1 (for county) and 2 (for cities)']
            raise ValidationError(errors)

        place = get_place(data['place_type'])
        if data['attribute'] not in place.supported_attributes:
            errors['attribute'] = ['Unsupported attribute']

        if data['normalize_by'] not in place.supported_attributes:
            errors['normalize_by'] = ['Unsupported attribute']

        if data['id'] not in place.df.index:
            errors['id'] = "Invalid place id"

        if errors:
            raise ValidationError(errors)

    class Meta:
        fields = ('id', 'attribute', 'count', 'place_type',
                  'year_range', 'normalize_by')
        ordered = True


class PlaceMultiSchema(Schema):
    id = ma_fields.Integer()
    place_type = ma_fields.Integer()
    normalize_by = ma_fields.Integer()
    attribute = ma_fields.List(ma_fields.Integer)
    count = ma_fields.Integer()
    year = ma_fields.Integer()

    @validates_schema
    def validate_input(self, data):
        errors = {}
        if data['place_type'] not in [0, 1, 2]:
            errors['place_type'] = [
                'Unsupported place type, use 0 (for state), 1 (for county) and 2 (for cities)']
            raise ValidationError(errors)

        place = get_place(data['place_type'])
        for attribute in data['attribute']:
            if attribute not in place.supported_attributes:
                errors['attribute'] = [
                    "Unsupported attribute '{}' ".format(attribute)]
                break

        if data['normalize_by'] not in place.supported_attributes:
            errors['normalize_by'] = ['Unsupported attribute']

        if data['id'] not in place.df.index:
            errors['id'] = "Invalid place id"

        if data['year'] < 1967 or data['year'] > 2016:
            errors['year'] = [
                "Only years between 1967 and 2016 are supported(inclusive)"]

        if errors:
            raise ValidationError(errors)

        class Meta:
            fields = ('id', 'attribute', 'count',
                      'place_type', 'year', 'normalize_by')
            ordered = True


@ns_place.route('/supported/<int:place_type>')
@ns_place.response(200, 'OK')
@ns_place.response(500, 'Internal Server Error')
@ns_place.response(400, 'Bad Request')
class Supported(Resource):
    def get(self, place_type):
        """
        Returns list of attributes supported to compare state/county/city.
        """
        if place_type not in [0, 1, 2]:
            return "Invalid place_type", 400
        return get_supported_attributes(place_type)


@ns_place.route('/supported')
@ns_place.response(200, 'OK')
@ns_place.response(500, 'Internal Server Error')
class Supported(Resource):
    def get(self):
        """
        Returns list of common attributes supported to compare places
        """
        return get_common_attributes()


@ns_place.route('/single')
@ns_place.response(501, 'Place ID not supported')
@ns_place.response(500, 'Internal Server Error')
@ns_place.response(200, 'OK')
@ns_place.response(400, 'Bad Request')
class SimilarPlaces(Resource):
    @api.expect(PlaceSingle)
    def post(self):
        """
        List of places which are similar in single attribute.
        """
        schema = PlaceSingleSchema()
        result, errors = schema.load(api.payload)
        if errors:
            return errors, 400
        return get_similar_places(result)


@ns_place.route('/multi')
@ns_place.response(501, 'Place ID not supported')
@ns_place.response(500, 'Internal Server Error')
@ns_place.response(200, 'OK')
@ns_place.response(400, 'Bad Request')
class SimilarPlacesMultiAttr(Resource):
    @api.expect(PlaceMulti)
    def post(self):
        """
        List of places which are similar in multiple attributes(Total_Revenue,Total_Taxes,etc.  
        """
        schema = PlaceMultiSchema()
        result, errors = schema.load(api.payload)
        if errors:
            return errors, 400
        print(json.dumps(result))
        return get_similar_places(result, multiattr=True)

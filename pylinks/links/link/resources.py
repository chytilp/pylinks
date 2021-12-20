from flask_restful import Resource, Api
from flask import request, Blueprint
from webargs import fields, ValidationError
from marshmallow.validate import Length

from lib.response import make_json_response
from lib.param_check import use_args, between, gt, is_url
from lib.query import apply_limit_and_offset

from .models import Category, Link
from links import DEFAULT_GET_LIMIT


blueprint = Blueprint('links', __name__)
api = Api(blueprint)


def exists_link(except_link_id=None, name=None, link=None):
    if except_link_id is None and name is None and link is None:
        raise ValueError("Link search, everything None, nothing to search.")
    if except_link_id:
        if name:
            return (Link.query.filter(Link.name == name, Link.id != except_link_id).first()
                    is not None)
        elif link:
            return (Link.query.filter(Link.link == link, Link.id != except_link_id).first()
                    is not None)
    else:
        if name:
            return Link.query.filter_by(name=name).first() is not None
        elif link:
            return Link.query.filter_by(link=link).first() is not None


def exists_category(except_category_id=None, name=None):
    if name is None and except_category_id is None:
        raise ValueError("Category search, everything None, nothing to search.")
    if except_category_id and name:
        return (Category.query.filter(Category.name == name,
                                      Category.id != except_category_id).first() is not None)
    elif name:
        return Category.query.filter_by(name=name).first() is not None
    raise ValueError("Invalid category search parameters combination.")


def get_category(category_id):
    return Category.query.filter_by(id=category_id).first()


@api.resource('/links')
class LinkListResource(Resource):

    @use_args({
            "limit": fields.Int(validate=between(1, 1000), missing=DEFAULT_GET_LIMIT),
            "offset": fields.Int(missing=0, validate=gt(0)),
        }, location="query")
    def get(self, args):
        query = apply_limit_and_offset(Link.query, args["limit"], args["offset"])
        links = query.filter_by(active=None).all()
        result = {'links': [link.to_json() for link in links]}
        return make_json_response(200, result)

    @use_args({
        "name": fields.Str(required=True, validate=(
                Length(min=1, max=50, error="Length must be between [{min}, {max}]."))),
        "link": fields.Str(required=True, validate=is_url),
        "categoryId": fields.Int(required=True),
    }, location="json")
    def post(self, args):
        # 1. name is unique (not in db yet)
        if exists_link(name=args["name"]):
            raise ValidationError("Link with name: {} already exists.".format(args["name"]))
        # 2. link is unique
        if exists_link(link=args["link"]):
            raise ValidationError("Link with link: {} already exists.".format(args["link"]))
        # 3. categoryId exists in db.
        category = get_category(args["categoryId"])
        if not category:
            raise ValidationError("Category with id: {} does not exist.".format(args["categoryId"]))
        new_link = Link(name=args["name"], link=args["link"], category=category)
        new_link.save()
        return make_json_response(201, new_link.to_json())


@api.resource('/links/<int:link_id>')
class LinkResource(Resource):

    @use_args({
            "link_id": fields.Int(validate=gt(0), required=True)
        }, location="view_args")
    def get(self, args, link_id):
        link_id = args['link_id']
        link = Link.query.filter_by(id=link_id).first_or_404()
        result = link.to_json()
        return make_json_response(200, result)

    @use_args({
            "link_id": fields.Int(validate=gt(0), required=True)
        }, location="view_args")
    def delete(self, link_id):
        link = Link.query.filter_by(id=link_id).first_or_404()
        link.delete()
        return make_json_response(202, link.to_json())

    @use_args({
            "link_id": fields.Int(validate=gt(0), required=True)
        }, location="view_args")
    @use_args({
        "name": fields.Str(required=True, validate=(
                Length(min=1, max=50, error="Length must be between [{min}, {max}]."))),
        "link": fields.Str(required=True, validate=is_url),
        "categoryId": fields.Int(required=True),
    }, location="json")
    def put(self, link_id, args):
        # 1. name is unique
        if exists_link(except_link_id=link_id, name=args["name"]):
            raise ValidationError("Link with name: {} already exists.".format(args["name"]))
        # 2. link is unique
        if exists_link(except_link_id=link_id, link=args["link"]):
            raise ValidationError("Link with link: {} already exists.".format(args["link"]))
        # 3. categoryId exists in db.
        category = get_category(args["categoryId"])
        if not category:
            raise ValidationError("Category with id: {} does not exist.".format(args["categoryId"]))
        modified_link = Link(name=args["name"], link=args["link"], category=category)
        modified_link.save()
        return make_json_response(202, modified_link.to_json())


@api.resource('/categories')
class CategoryListResource(Resource):

    @use_args({
            "limit": fields.Int(validate=between(1, 1000), missing=DEFAULT_GET_LIMIT),
            "offset": fields.Int(missing=0, validate=gt(0)),
        }, location="query")
    def get(self, args):
        query = apply_limit_and_offset(Category.query, args["limit"], args["offset"])
        categories = query.filter_by(active=None).all()
        result = {'categories': [category.to_json(True) for category in categories]}
        return make_json_response(200, result)

    @use_args({
        "name": fields.Str(required=True, validate=(
                Length(min=1, max=50, error="Length must be between [{min}, {max}]."))),
        "parentId": fields.Int(missing=0),
    }, location="json")
    def post(self, args):
        # 1. name is unique (not in db yet)
        if exists_category(name=args["name"]):
            raise ValidationError("Category with name: {} already exists.".format(args["name"]))
        # 2. parentId exists in db.
        parent = None
        if args["parentId"] > 0:
            parent = get_category(args["parentId"])
            if not parent:
                raise ValidationError("Category with id: {} does not exist.".format(
                    args["parentId"]))

        new_category = Category(name=args["name"], parent_category=parent)
        new_category.save()
        return make_json_response(201, new_category.to_json())


@api.resource('/categories/<int:category_id>')
class CategoryResource(Resource):

    @use_args({
        "category_id": fields.Int(validate=gt(0), required=True)
    }, location="view_args")
    def get(self, args, category_id):
        category_id = args['category_id']
        category = Category.query.filter_by(id=category_id).first_or_404()
        result = category.to_json()
        return make_json_response(200, result)

    @use_args({
        "category_id": fields.Int(validate=gt(0), required=True)
    }, location="view_args")
    def delete(self, category_id):
        category = Category.query.filter_by(id=category_id).first_or_404()
        category.delete()
        return make_json_response(202, category.to_json())

    @use_args({
        "category_id": fields.Int(validate=gt(0), required=True)
    }, location="view_args")
    @use_args({
        "name": fields.Str(required=True, validate=(
                Length(min=1, max=50, error="Length must be between [{min}, {max}]."))),
        "parentId": fields.Int(missing=0),
    }, location="json")
    def put(self, category_id, args):
        # 1. name is unique
        if exists_category(except_category_id=category_id, name=args["name"]):
            raise ValidationError("Category with name: {} already exists.".format(args["name"]))
        # 3. parentId exists in db.
        parent = get_category(args["parentId"])
        if not parent:
            raise ValidationError("Category with id: {} does not exist.".format(args["parentId"]))
        modified_category = Category(name=args["name"], parent_category=parent)
        modified_category.save()
        return make_json_response(202, modified_category.to_json())


def register(app, **kwargs):
    app.register_blueprint(blueprint, **kwargs)

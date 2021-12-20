from datetime import datetime

from links import db


class Category(db.Model):

    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    active = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, name, parent_category):
        self.name = name
        self.parent_id = parent_category.id

    @property
    def parent(self):
        if self.parent_id:
            return Category.query.filter_by(id=self.parent_id)[0]
        else:
            return None

    @property
    def children(self):
        return Category.query.filter_by(parent_id=self.id).all()

    def to_json(self, detailed=False):
        json_result = {
            "id": self.id,
            "name": self.name,
            "active": self.active is None,
            "created": self.created,
        }
        if detailed:
            json_result["parent"] = None if self.parent is None else self.parent.to_json()
        return json_result

    def save(self):
        db.session.add(self)
        db.commit()

    def delete(self):
        self.active = datetime.now()
        db.session.add(self)
        db.commit()

    def __repr__(self):
        return '<Category id=%d name=%r>' % (self.id, self.name)


class Link(db.Model):

    __tablename__ = 'link'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)
    link = db.Column(db.String(100), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(
        'Category', backref=db.backref('links', lazy='dynamic')
    )
    active = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, name, link, category):
        self.name = name
        self.link = link
        self.category = category
        self.category_id = category.id

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "link": self.link,
            "category": self.category.to_json(),
            "active": self.active is None,
            "created": self.created,
        }

    def save(self):
        db.session.add(self)
        db.commit()

    def delete(self):
        self.active = datetime.now()
        db.session.add(self)
        db.commit()

    def __repr__(self):
        return '<Link id=%d name=%r>' % (self.id, self.name)

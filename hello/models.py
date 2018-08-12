from datetime import datetime
from hello import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship('Product', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Product('{self.title}', '{self.date_posted}')"


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False, unique=True)
    qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Location('{self.location_name}')"


class ProductMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, nullable=False, default=datetime.now)
    from_location = db.Column(db.String(100))
    to_location = db.Column(db.String(100))
    pid = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"ProductMovement('{self.from_location}', '{self.to_location}', '{self.pid}', '{self.qty}')"

from datetime import datetime
from flaskshow import db,app,user_login_manager, admin_login_manager
from flask_login import UserMixin

@user_login_manager.user_loader
def load_user(user_id):
    return Buyer.query.get(int(user_id))

@admin_login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))


class Admin(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    events = db.relationship('Event', backref='admin', lazy=True)

    def is_admin(self):
        return True



class Event(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(255))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    ticket_price = db.Column(db.Float, nullable=False)
    tickets = db.relationship('Ticket', backref='event', lazy=True)



class Venue(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    events = db.relationship('Event', backref='venue', lazy=True)
    admins = db.relationship('Admin', backref='venue', lazy=True)




class Ticket(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id',ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'))

class Buyer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    tickets_purchased = db.relationship('Ticket', backref='purchased_by', lazy=True)




    def get_id(self):
        return str(self.id)

    def is_buyer(self):
        return True    

    def is_active(self):
        return True

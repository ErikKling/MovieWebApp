from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    movies = relationship('Movie', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"
    
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    year = db.Column(db.String)
    poster = db.Column(db.String)
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
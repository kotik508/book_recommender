from . import db
from sqlalchemy.sql import func


class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True)
    picked_books = db.Column(db.String)
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    scores = db.relationship('Score')


class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    session_id = db.Column(db.Integer, db.ForeignKey('usersession.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))


class Book(db.Model):
    __tablename__ = "book"
    
    id = db.Column(db.Integer, primary_key=True)
    goodreads_id = db.Column(db.Integer)
    title = db.Column(db.String(250))
    isbn = db.Column(db.Integer)
    author = db.Column(db.String(150))
    num_pages = db.Column(db.Integer(db.Integer))
    description = db.Column(db.String(10000))
    cover_image_uri = db.Column(db.String(150))
    series_length = db.Column(db.Integer)
    year_first_published = db.Column(db.Integer)
    avg_rating = db.Column(db.Float)
    tags = db.Column(db.String(250))
    rating_distribution = db.Column(db.String(300))
    score = db.relationship('Score')



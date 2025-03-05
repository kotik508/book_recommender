from . import db
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector


class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True)
    picked_books = db.Column(db.String)
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    scores = db.relationship('Score', back_populates='session', cascade='all, delete-orphan')


class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    session = db.relationship('Session', back_populates='scores')
    books = db.relationship('Book', back_populates='scores')


class Book(db.Model):
    __tablename__ = "book"
    
    id = db.Column(db.Integer, primary_key=True)
    goodreads_id = db.Column(db.BigInteger)
    title = db.Column(db.String(250))
    isbn = db.Column(db.String(150))
    author = db.Column(db.String(150))
    num_pages = db.Column(db.Integer)
    description = db.Column(db.String(10000))
    cover_image_uri = db.Column(db.String(150))
    series_length = db.Column(db.Integer)
    year_first_published = db.Column(db.Integer)
    avg_rating = db.Column(db.Float)
    tags = db.Column(db.String(250))
    rating_distribution = db.Column(db.String(300))
    embedding = db.Column(Vector(1024))
    scores = db.relationship('Score', back_populates='books', cascade='all, delete-orphan')


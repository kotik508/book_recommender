from . import db
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from flask import session
from sqlalchemy import text
import numpy as np


class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True)
    picked_books = db.Column(db.String)
    centroid1 = db.Column(Vector(1024))
    centroid2 = db.Column(Vector(1024))
    centroid3 = db.Column(Vector(1024))
    centroid4 = db.Column(Vector(1024))
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    rounds = db.Column(db.Integer, default=0)
    scores = db.relationship('Score', back_populates='session', cascade='all, delete-orphan')

    @classmethod
    def increase_session_round(cls):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        sess.rounds += 1
        db.session.commit()

    @classmethod
    def assign_centroids(cls, centroids):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        sess.centroid1 = centroids[0].tolist()
        sess.centroid2 = centroids[1].tolist()
        sess.centroid3 = centroids[2].tolist()
        sess.centroid4 = centroids[3].tolist()
        db.session.commit()

    @classmethod
    def get_centroids(cls):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        centroids = [np.array(sess.centroid1), np.array(sess.centroid2), 
                     np.array(sess.centroid3), np.array(sess.centroid4)]
        return centroids

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
    scores = db.relationship('Score', back_populates='book', cascade='all, delete-orphan')

    @classmethod
    def get_embeddings(cls):
        results = db.session.query(cls.embedding).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_best_books(cls):
        query = text("SELECT b.* FROM book b LEFT JOIN score s ON b.id = s.book_id WHERE s.session_id = :session_id ORDER BY s.score DESC LIMIT 5;")
        results = db.session.execute(query, {"session_id": int(session['session_id'])})
        return results.fetchall()

class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    session = db.relationship('Session', back_populates='scores')
    book = db.relationship('Book', back_populates='scores')

    @classmethod
    def get_scores_from_sample(cls, session_id: int, books: list[Book]):
        book_ids = [book.id for book in books]
        scores = cls.query.filter((cls.session_id == session_id) & (cls.book_id.in_(book_ids))).all()
        return scores
    
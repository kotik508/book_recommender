from . import db
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from flask import session, current_app
from sqlalchemy import text
import numpy as np


picked_books = db.Table(
    'picked_books',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True)
)

disabled_books = db.Table(
    'disabled_books',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True)
)

recommended_books = db.Table(
    'recommended_books',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True)
)

class Session(db.Model):
    __tablename__ = "session"

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50))
    picked_books = db.relationship('Book', secondary=picked_books, backref='picked_by_session')
    disabled_books = db.relationship('Book', secondary=disabled_books, backref='disabled_by_session')
    centroid1 = db.Column(Vector)
    centroid2 = db.Column(Vector)
    centroid3 = db.Column(Vector)
    centroid4 = db.Column(Vector)
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    rounds = db.Column(db.Integer, default=0)
    scores = db.relationship('Score', back_populates='session', cascade='all, delete-orphan')

    @classmethod
    def increase_session_round(cls):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        sess.rounds += 1
        db.session.commit()

    @classmethod
    def get_rounds(cls):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        return sess.rounds

    @classmethod
    def get_type(cls):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        return sess.version

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
    
    @classmethod
    def move_book(cls, book_id: int, add: bool):
        session_obj = cls.query.get(session['session_id'])
        book_obj = Book.query.get(book_id)

        if not session_obj or not book_obj:
            return False

        if add=='pick':
            if book_obj not in session_obj.picked_books and len(session_obj.picked_books) < 5:
                session_obj.picked_books.append(book_obj)
                current_app.logger.info(f'Added book: {book_obj.id} to selected books.')
            else:
                current_app.logger.error('Too many picked books.')
        elif add=='rm_pick':
            if book_obj in session_obj.picked_books:
                session_obj.picked_books.remove(book_obj)
                current_app.logger.info(f'Removed book: {book_obj.id} from selected books.')
            if book_obj not in session_obj.disabled_books:
                session_obj.disabled_books.append(book_obj)
                current_app.logger.info(f'Added book: {book_obj.id} to disabled books.')
        elif add=='rm_disable':
            if book_obj in session_obj.disabled_books:
                session_obj.disabled_books.remove(book_obj)
                current_app.logger.info(f'Removed book: {book_obj.id} from disabled books.')
        else:
            current_app.logger.error('Wrong add messsage')

        db.session.commit()
        return True
    
    @classmethod
    def move_to_recommend(cls, book_ids: list[int]):
        session_obj = cls.query.get(session['session_id'])

        for book_id in book_ids:
            book_obj = Book.query.get(book_id)

            if not session_obj or not book_obj:
                return False
            
            if book_obj not in session_obj.recommended_books:
                session_obj.recommended_books.append(book_obj)
            
        db.session.commit()
        return True

    
    @classmethod
    def get_picked_books(cls):
        session_obj = cls.query.get(session['session_id'])
        return session_obj.picked_books
    
    @classmethod
    def get_disabled_books(cls):
        session_obj = cls.query.get(session['session_id'])
        return session_obj.disabled_books

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
    svd = db.Column(Vector(150))
    scores = db.relationship('Score', back_populates='book', cascade='all, delete-orphan')

    @classmethod
    def get_embeddings(cls):
        results = db.session.query(cls.embedding).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_svds(cls):
        results = db.session.query(cls.svd).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_best_books(cls):
        query = text("SELECT b.* FROM book b LEFT JOIN score s ON b.id = s.book_id WHERE s.session_id = :session_id ORDER BY s.score DESC LIMIT 20;")
        results = db.session.execute(query, {"session_id": int(session['session_id'])})
        best_books = results.fetchall()
        picked_books = [b.id for b in Session.get_picked_books()]
        disabled_books = [d.id for d in Session.get_disabled_books()]
        return [book for book in best_books if book.id not in picked_books + disabled_books]

class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    session = db.relationship('Session', back_populates='scores')
    book = db.relationship('Book', back_populates='scores')

    @classmethod
    def get_scores_from_sample(cls, books: list[Book]):
        session_id = session['session_id']
        book_ids = [book.id for book in books]
        scores = cls.query.filter((cls.session_id == session_id) & (cls.book_id.in_(book_ids))).all()
        return scores
    
    @classmethod
    def get_score(cls, session_id: int, book_id: int):
        return cls.query.filter((cls.session_id == session_id) & (cls.book_id == book_id)).first().score
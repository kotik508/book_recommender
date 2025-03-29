from . import db
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from flask import session, current_app
from sqlalchemy import text
import numpy as np
import random


picked_books = db.Table(
    'picked_books',
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
    code = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(50))
    picked_books = db.relationship('Book', secondary=picked_books, backref='picked_by_session')
    recommended_books = db.relationship('Book', secondary=recommended_books, backref='recommended_by_session')
    centroid1 = db.Column(Vector)
    centroid2 = db.Column(Vector)
    centroid3 = db.Column(Vector)
    centroid4 = db.Column(Vector)
    summary1 = db.Column(db.String(400))
    summary2 = db.Column(db.String(400))
    summary3 = db.Column(db.String(400))
    summary4 = db.Column(db.String(400))
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    rounds = db.Column(db.Integer, default=0)
    age_category = db.Column(db.String(20))
    education = db.Column(db.String(150))
    gender = db.Column(db.String(20))
    email = db.Column(db.String(200))
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
        return sess.type

    @classmethod
    def assign_centroids(cls, centroids):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        sess.centroid1 = centroids[0].tolist()
        sess.centroid2 = centroids[1].tolist()
        sess.centroid3 = centroids[2].tolist()
        sess.centroid4 = centroids[3].tolist()
        db.session.commit()

    @classmethod
    def assign_summaries(cls, summaries: dict):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        sess.summary1 = summaries[0]
        sess.summary2 = summaries[1]
        sess.summary3 = summaries[2]
        sess.summary4 = summaries[3]
        db.session.commit()

    @classmethod
    def get_summaries(cls):
        sess = cls.query.filter(cls.id == session['session_id']).first()
        summaries = {}
        summaries[0] = sess.summary1
        summaries[1] = sess.summary2
        summaries[2] = sess.summary3
        summaries[3] = sess.summary4
        return summaries

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
        results = db.session.query(cls.embedding).order_by(cls.id).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_svds(cls):
        results = db.session.query(cls.svd).order_by(cls.id).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_book_ids(cls):
        book_ids = db.session.query(cls.id).order_by(cls.id).all()
        return [row[0] for row in book_ids]
    
    @classmethod
    def get_embeddings_from_ids(cls, book_ids):
        results = db.session.query(cls.embedding).filter(cls.id.in_(book_ids)).order_by(cls.id).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_svds_from_ids(cls, book_ids):
        results = db.session.query(cls.svd).filter(cls.id.in_(book_ids)).order_by(cls.id).all()
        return [row[0] for row in results]
    
    @classmethod
    def get_best_books(cls):
        query = text(
            # "SELECT b.id, b.goodreads_id, b.title, b.author, b.description, b.cover_image_uri, b.avg_rating "
            "SELECT b.* "
            "FROM book b "
            "LEFT JOIN score s ON b.id = s.book_id "
            "WHERE s.session_id = :session_id "
            "ORDER BY s.score DESC "
            "LIMIT 100;"
        )
        results = db.session.execute(query, {"session_id": int(session['session_id'])})
        current_app.logger.info("checkpoint 1")
        best_books = results.fetchall()

        picked_books = set(b.id for b in Session.get_picked_books())
        show_books = {'best_books': [], 'sampled_books': []}

        current_app.logger.info("checkpoint 2")
        
        for book in best_books:
            if len(show_books['best_books']) < 10 and book.id not in picked_books:
                show_books['best_books'].append(book)
                picked_books.add(book.id)
        
        current_app.logger.info("checkpoint 3")
        
        remaining_books = [book for book in best_books if book.id not in picked_books]
        if remaining_books:
            show_books['sampled_books'] = random.sample(remaining_books, min(len(remaining_books), 10))

        current_app.logger.info("checkpoint 4")
            
        return show_books

class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

    session = db.relationship('Session', back_populates='scores')
    book = db.relationship('Book', back_populates='scores')

    @classmethod
    def get_scores_from_sample(cls, book_ids: list[Book]):
        session_id = session['session_id']
        scores = cls.query.filter((cls.session_id == session_id) & (cls.book_id.in_(book_ids))).order_by(cls.book_id).all()
        return scores
    
    @classmethod
    def get_score(cls, session_id: int, book_id: int):
        return cls.query.filter((cls.session_id == session_id) & (cls.book_id == book_id)).first().score
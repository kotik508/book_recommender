from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_migrate import Migrate
from logging.config import dictConfig
import configparser
import pandas as pd
import numpy as np
import os
import sys
import asyncio


db = SQLAlchemy()
DB_NAME = "bookie"

def create_app():
    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read('../config.ini')
    app.config['SECRET_KEY'] = config['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if sys.platform.startswith('linux'):
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
 
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/app/logs/bookie.log',
                'mode': 'a',
                'maxBytes': 10000000,
                'backupCount': 3,
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        }
    })

    db.init_app(app)
    app.logger.info(f'Database initialized')
    migration = Migrate(app, db)
    app.logger.info(f'Database Migrated')

    from .text_generation import init_genai

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    from .models import Session, Score, Book

    populate_books(app)

    return app

def populate_books(app):
    DB_URI = os.getenv("DATABASE_URL")
    TABLE_NAME = 'book'
    books_populated = False
    engine = create_engine(DB_URI)
    df = pd.read_csv('goodreads_scraper/books_cleaned.csv')
    embeddings = np.load('data/embeddings.npy')
    svd_vectors = np.load('data/svd_vectors.npy')

    from .models import Book

    check_books = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = :table_name
            )
        """)
    
    count_rows_query = text(f"SELECT COUNT(*) FROM {TABLE_NAME}")

    with engine.connect() as connection:
        table_exists = connection.execute(check_books, {"table_name": TABLE_NAME}).scalar()

        if table_exists:
            row_count = connection.execute(count_rows_query).scalar()
            if row_count == len(df):
                app.logger.info(f"Table '{TABLE_NAME}' exists with {row_count} books present.")
                books_populated = True
            elif row_count < len(df):
                app.logger.info(f"Table '{TABLE_NAME}' exists with, but only {row_count} books are present.\nRepopulating the table.")
            else:
                app.logger.info(f"Table '{TABLE_NAME}' exists but is empty")
        else:
            app.logger.error(f"Table '{TABLE_NAME}' does not exist.")
            books_populated = True
        
        if not books_populated:
            with app.app_context():

                db.session.query(Book).delete()
                db.session.commit()

                for (_, row), embedding, svd in zip(df.iterrows(), embeddings, svd_vectors):
                    book = Book(
                        goodreads_id=row['book_id'],
                        title = row['book_title'],
                        isbn = row['isbn'],
                        author = row['author'],
                        num_pages = row['num_pages'] if pd.notna(row['num_pages']) else None,
                        description = row['description'],
                        cover_image_uri = row['cover_image_uri'],
                        series_length = row['series_length'] if pd.notna(row['series_length']) else None,
                        year_first_published = row['year_first_published'] if pd.notna(row['year_first_published']) else None,
                        avg_rating = row['average_rating'],
                        tags = row['tags'],
                        rating_distribution = row['rating_distribution'],
                        embedding = embedding,
                        svd = svd
                    )
                    db.session.add(book)
                db.session.commit()

                app.logger.info(f"Populated table '{TABLE_NAME}' with {len(df)} books.")
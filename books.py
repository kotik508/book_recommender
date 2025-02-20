import pandas as pd


def init_books():
    books = pd.read_csv('goodreads_scraper/books_old.csv')
    books['score'] = 0.19
    return books



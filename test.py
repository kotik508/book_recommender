import pandas as pd
import numpy as np

books = pd.read_csv('goodreads_scraper/books_cleaned.csv')

embeddings = np.load('../embeddings.npy')

print(len(embeddings))
print(len(books))

if len(embeddings) == len(books):

    for (_, row), embedding in zip(books.iterrows(), embeddings):
        if _ < 5:
            print("Row: " + str(_))
            print("Book: " + row['book_title'])
            print(len(embedding))
            print(embedding[:5])

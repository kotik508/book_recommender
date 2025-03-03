from website import create_app
import numpy as np
from computations import initialize_scores, load_embeddings
from text_generation import init_genai
import pandas as pd
import ast

app = create_app()

genai_client = init_genai()

centroids = None
best_embeddings = None

books = pd.read_csv('goodreads_scraper/books_cleaned.csv')
books['tags'] = books['tags'].apply(ast.literal_eval)

scores = initialize_scores(len(books))
embeddings = load_embeddings()
rnd = 0

if __name__ == '__main__':
    app.run(debug=True)
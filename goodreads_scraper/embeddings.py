from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

model = SentenceTransformer('Snowflake/snowflake-arctic-embed-l-v2.0')

books = pd.read_csv('books_cleaned.csv')

embeddings = model.encode(books['description'], )

print('Embeddings created')

np.save('../../embeddings.npy', embeddings)
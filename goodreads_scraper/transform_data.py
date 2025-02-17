import pandas as pd

data = pd.read_json('book_data.json')

data.to_csv('books.json')
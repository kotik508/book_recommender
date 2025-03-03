import pandas as pd

data = pd.read_csv('goodreads_scraper/books_cleaned.csv')

print(len(data['tags'].loc[data['tags'].str.len().idxmax()]))

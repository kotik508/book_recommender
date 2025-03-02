from text_generation import init_genai, get_description, create_prompt
import pandas as pd

client = init_genai()

books = pd.read_csv('goodreads_scraper/books_cleaned.csv')

book_descs = books.loc[books['author'] == 'J.R.R. Tolkien', 'description']

prompt = create_prompt(book_descs)

print(get_description(client, prompt))
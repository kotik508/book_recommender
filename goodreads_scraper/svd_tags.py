import ast
import pandas as pd
from sklearn.decomposition import TruncatedSVD
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer

books = pd.read_csv('goodreads_scraper/books_cleaned.csv')
books['tags'] = books['tags'].apply(lambda x: ast.literal_eval(x))

mlb = MultiLabelBinarizer()
tags_matrix = pd.DataFrame(mlb.fit_transform(books['tags']), columns=mlb.classes_, index=books['book_title'])

svd = TruncatedSVD(n_components=150)
svd_matrix = svd.fit_transform(tags_matrix)

np.save('../../svd_vectors.npy', svd_matrix)

# svd.fit(tags_matrix)

# plt.plot(range(1, 151), np.cumsum(svd.explained_variance_ratio_), marker='o')
# plt.xlabel("Number of Components")
# plt.ylabel("Cumulative Explained Variance")
# plt.title("Choosing the Optimal Number of Components")
# plt.grid()
# plt.show()
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

norms = np.linalg.norm(svd_matrix, axis=1, keepdims=True)

no = []
for i, n in enumerate(norms):
    if not np.isclose(n, 1):
        no.append(n)

print(len(no))

norms = np.where(norms == 0, 1, norms)

normalized_svds = svd_matrix / norms

norms2 = np.linalg.norm(normalized_svds, axis=1, keepdims=True)

no = []
for i, n in enumerate(norms2):
    if not np.isclose(n, 1):
        no.append(n)

print(len(no))

print(min(norms2))

np.save('data/svd_vectors.npy', normalized_svds)

# svd.fit(tags_matrix)

# plt.plot(range(1, 151), np.cumsum(svd.explained_variance_ratio_), marker='o')
# plt.xlabel("Number of Components")
# plt.ylabel("Cumulative Explained Variance")
# plt.title("Choosing the Optimal Number of Components")
# plt.grid()
# plt.show()
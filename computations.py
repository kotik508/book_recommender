from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd


def create_embeddings():
    model = SentenceTransformer('../models/multilingual-e5-large').to('cuda')

    books = pd.read_csv('goodreads_scraper/books_desc.csv')

    embeddings = model.encode(books['description'], )

    print('Embeddings created')

    np.save('../embeddings', embeddings)


def load_embeddings():
    desc_emb = np.load('../embeddings.npy')
    return desc_emb


def cluster(embeddings: pd.DataFrame, scores: np.array):
    kmeans = KMeans(n_clusters=4, n_init=10, random_state=0, max_iter=1000)
    kmeans.fit(embeddings, sample_weight=scores)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    return labels, centroids
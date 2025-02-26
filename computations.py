from scipy.spatial.distance import cdist
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
from transformers import pipeline


def create_embeddings():
    model = SentenceTransformer('Snowflake/snowflake-arctic-embed-l-v2.0')

    books = pd.read_csv('goodreads_scraper/books_cleaned.csv')

    embeddings = model.encode(books['description'], )

    print('Embeddings created')

    np.save('../embeddings', embeddings)


def load_embeddings():
    desc_emb = np.load('../embeddings.npy')
    return desc_emb


def clustering(embeddings: np.ndarray, scores: np.array):

    # sample_indices = np.random.choice(embeddings.shape[0], size=100, replace=False)

    # find clusters using k-means with k = 4
    kmeans = KMeans(n_clusters=4, n_init=10, max_iter=1000)
    kmeans.fit(embeddings, sample_weight=scores)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    best_embeddings = {}

    # Find 4 best matching book descriptions for each cluster
    for cluster_id in range(4):
        cluster_indices = np.where(labels == cluster_id)[0]

        cluster_embeddings = embeddings[cluster_indices]
        distances = cdist(cluster_embeddings, centroids[cluster_id].reshape(1, -1), metric='euclidean').flatten()

        top_indices = cluster_indices[np.argsort(distances)[:4]]

        best_embeddings[cluster_id] = top_indices.tolist()

    return labels, centroids, best_embeddings

def initialize_scores(books_len: int):
    scores = np.full(books_len, 1/books_len)
    return scores


def update_scores(scores, embeddings, selected_cluster, centroids, sigma: np.float32 = np.float32(0.1)):

    res = np.full(len(embeddings), np.float32(1))
    for index, book in enumerate(embeddings):
        disp_sum = 0
        for x in centroids:

            if not np.array_equal(x, selected_cluster):
                disp_sum += np.exp(-(np.divide(np.linalg.norm(x - book), sigma)))

        like_val = np.exp(-(np.divide(np.linalg.norm(selected_cluster - book), sigma)))
        res[index] = res[index] * (like_val / (disp_sum + like_val)) * scores[index]

    res = np.divide(res, np.max(res))

    return res


def generate_text(texts):
    summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

    text = '\n'.join(texts)

    return summarizer(text)[0]['summary_text']

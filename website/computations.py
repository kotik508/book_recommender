from scipy.spatial.distance import cdist
from flask import session
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from .text_generation import get_description
from .models import Score, Session, Book
from . import db
import random
import time
import numpy as np
import pandas as pd


def get_answers():

    books = Book.query.all()
    now = time.time()
    scores = np.array([score.score for score in Score.get_scores_from_sample(books)])
    weights = np.log1p(scores)
    print(sum(weights))
    print(f'Log transform took: {round(time.time()- now, 4)} seconds')
    books_sampled = random.choices(books, weights=weights, k=500)

    now = time.time()
    best_embeddings = clustering(books_sampled)
    print(f'Clustering took: {round(time.time()- now, 4)} seconds')

    now = time.time()
    summaries = {}
    for cluster in best_embeddings.keys():
        summaries[cluster] = get_description(best_embeddings[cluster])
    print(f'Generating descriptions took: {round(time.time()- now, 4)} seconds')

    session['summaries'] = summaries

def create_embeddings():
    model = SentenceTransformer('Snowflake/snowflake-arctic-embed-l-v2.0')

    books = pd.read_csv('goodreads_scraper/books_cleaned.csv')

    embeddings = model.encode(books['description'], )

    print('Embeddings created')

    np.save('../embeddings.npy', embeddings)

def load_embeddings():
    desc_emb = np.load('../embeddings.npy')
    return desc_emb

def clustering(books: list[Book]):

    if session['type'] == 'descriptions':
        embeddings = np.array([book.embedding for book in books])
    elif session['type'] == 'tags':
        embeddings = np.array([book.svd for book in books])
    else:
        print(f'WARNING INVALID SESSION TYPE: {session['type']}')
        embeddings = np.array([book.embedding for book in books])

    # find clusters using k-means with k = 4
    kmeans = KMeans(n_clusters=4, n_init=10, max_iter=1000)
    kmeans.fit(embeddings)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    Session.assign_centroids(centroids)

    best_embeddings = {}

    # Find 5 best matching book descriptions for each cluster
    for cluster_id in range(4):
        cluster_indices = np.where(labels == cluster_id)[0]

        cluster_embeddings = embeddings[cluster_indices]
        distances = cdist(cluster_embeddings, centroids[cluster_id].reshape(1, -1), metric='euclidean').flatten()

        top_indices = cluster_indices[np.argsort(distances)[:5]].tolist()

        best_embeddings[cluster_id] = [books[i] for i in top_indices]

    for cs in best_embeddings.keys():
        print(f'Best book for cluster {cs}: {best_embeddings[cs][0].tags[:20]}')
        print(f'Second best book for cluster {cs}: {best_embeddings[cs][1].tags[:20]}')
        print(f'Third best book for cluster {cs}: {best_embeddings[cs][3].tags[:20]}')

    return best_embeddings

def update_scores(scores: list[Score], embeddings, selected_cluster: int, sigma: np.float32 = np.float32(0.5)):

    centroids = Session.get_centroids()

    # Score calculation based on embedding distance
    for score, embedding in zip(scores, embeddings):
        disp_sum = 0
        for x in centroids:

            if not np.array_equal(x, centroids[selected_cluster]):
                disp_sum += np.exp(-(np.divide(np.linalg.norm(x - embedding), sigma)))
        
        like_val = np.exp(-(np.divide(np.linalg.norm(centroids[selected_cluster] - embedding), sigma)))
        score.score = float(score.score * (like_val / (disp_sum + like_val)))

    # Score adjustment to keep values between 0 and 1
    scores_list = np.array([s.score for s in scores])
    scores_cal = np.divide(scores_list, np.max(scores_list))
    
    for score, new_score in zip(scores, scores_cal):
        score.score = float(new_score)
    
    db.session.commit()



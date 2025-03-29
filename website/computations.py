from scipy.spatial.distance import cdist
from flask import session, current_app
from sklearn.cluster import KMeans
from .text_generation import run_async_process, get_description
from .models import Score, Session, Book
from . import db
import asyncio
import time
import numpy as np
import pandas as pd


def get_answers(book_ids):
    now = time.time()
    scores = np.array([score.score for score in Score.get_scores_from_sample(book_ids)])
    exp = (15 - Session.get_rounds()) / 2 - 2
    # exp = 5 + (Session.get_rounds() / 2)
    weights = scores**(exp)
    weights = np.divide(weights, np.sum(weights))
    current_app.logger.info(f'Score transform took: {round(time.time()- now, 4)} seconds')

    now = time.time()
    books_sampled = np.random.choice(list(range(len(book_ids))), size=500, replace=False, p=weights)
    sorted = np.argsort(-scores)
    current_app.logger.info("Mean rank: " + str(np.mean(np.where(sorted[:, None] == books_sampled)[0])))
    
    # current_app.logger.info(f'HP position: {np.where(sorted[:, None] == 120)[0]}')
    # current_app.logger.info(f'HP score: {Score.query.filter((Score.book_id == 121) & (Score.session_id == session['session_id'])).first().score}')
    # current_app.logger.info(f'1984 position: {np.where(sorted[:, None] == 2714)[0]}')
    # current_app.logger.info(f'1984 score: {Score.query.filter((Score.book_id == 2715) & (Score.session_id == session['session_id'])).first().score}')
    
    current_app.logger.info(f'LOTR position: {np.where(sorted[:, None] == 75)[0]}')
    current_app.logger.info(f'LOTR score: {Score.query.filter((Score.book_id == 76) & (Score.session_id == session['session_id'])).first().score}')
    books_sampled = [book_ids[book] for book in books_sampled]
    books_sampled.sort()
    current_app.logger.info(books_sampled[:20])
    current_app.logger.info(f'Books sample took: {round(time.time()- now, 4)} seconds')

    now = time.time()
    best_embeddings = clustering(books_sampled)
    current_app.logger.info(f'Clustering took: {round(time.time()- now, 4)} seconds')

    now = time.time()
    tasks = [get_description(best_embeddings[i]) for i in best_embeddings.keys()]

    summaries = run_async_process(tasks)

    Session.assign_summaries(summaries)
    current_app.logger.info(f'Summ gen took + assign took: {round(time.time()- now, 4)} seconds')

def load_embeddings():
    desc_emb = np.load('data/embeddings.npy')
    return desc_emb

def clustering(book_ids):

    if session['type'] == 'descriptions':
        embeddings = np.array(Book.get_embeddings_from_ids(book_ids))
    elif session['type'] == 'tags':
        embeddings = np.array(Book.get_svds_from_ids(book_ids))
    else:
        current_app.logger.warning(f'WARNING INVALID SESSION TYPE: {session['type']}')
        embeddings = np.array(Book.get_embeddings_from_ids(book_ids))

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

        best_ids = [book_ids[i] for i in cluster_indices]

        best_books = Book.query.filter(Book.id.in_(best_ids)).all()

        best_books_sorted = sorted(best_books, key=lambda book: int(book.id))[:5]
        best_embeddings[cluster_id] = best_books_sorted

        # cluster_embeddings = embeddings[cluster_indices]
        # distances = cdist(cluster_embeddings, centroids[cluster_id].reshape(1, -1), metric='euclidean').flatten()

        # top_indices = cluster_indices[np.argsort(distances)[:10]].tolist()

        # best_embeddings[cluster_id] = [books[i] for i in top_indices]

    # for cs in best_embeddings.keys():
    #     for i in range(4):
    #         current_app.logger.info(f'Best book for cluster {cs}: Book {i} {best_embeddings[cs][i].title}')

    return best_embeddings

def update_scores(scores: list[Score], embeddings, selected_cluster: int, disable_books: list[str], sigma: np.float32 = np.float32(0.25)):

    centroids = Session.get_centroids()

    scores_list = []

    # Score calculation based on embedding distance
    for score, embedding in zip(scores, embeddings):
    
        disp_sum = 0
        for x in centroids:

            if not np.array_equal(x, centroids[selected_cluster]):
                disp_sum += np.exp(-np.linalg.norm(x - embedding) / sigma)
        
        like_val = np.exp(-np.linalg.norm(centroids[selected_cluster] - embedding) / sigma)
        score.score = float(score.score * (like_val / (disp_sum + like_val)))

        scores_list.append(score.score)

    # Score adjustment to keep values between 0 and 1
    scores_list = np.array(scores_list)
    if np.max(scores_list) > 0:
        scores_cal = np.divide(scores_list, np.max(scores_list))
    else:
        scores_cal = np.divide(scores_list, float(np.e**(-10)))
    
    for score, new_score in zip(scores, scores_cal):
        if score.book_id not in disable_books:
            score.score = float(new_score)
        else:
            score.score = float(np.e**(-10))
    
    db.session.commit()



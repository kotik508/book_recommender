from flask import session, current_app
from sklearn.cluster import KMeans
from .text_generation import run_async_process, get_description
from .models import Score, Session, Book
from . import db
import time
import numpy as np
import random


def get_answers(book_ids):
    now = time.time()
    scores = np.array([score.score for score in Score.get_scores_from_sample(book_ids)])
    exp = 8
    weights = scores**(exp)
    weights = np.divide(weights, np.sum(weights))
    current_app.logger.info(f'Score transform took: {round(time.time()- now, 4)} seconds')

    now = time.time()
    books_sampled = np.random.choice(list(range(len(book_ids))), size=500, replace=False, p=weights)
    sorted = np.argsort(-scores)
    # current_app.logger.info("Mean rank: " + str(np.mean(np.where(sorted[:, None] == books_sampled)[0])))
    
    # current_app.logger.info(f'HP position: {np.where(sorted[:, None] == 5648)[0]}')
    # current_app.logger.info(f'HP score: {Score.query.filter((Score.book_id == 5649) & (Score.session_id == session['session_id'])).first().score}')
    # current_app.logger.info(f'1984 position: {np.where(sorted[:, None] == 2714)[0]}')
    # current_app.logger.info(f'1984 score: {Score.query.filter((Score.book_id == 2715) & (Score.session_id == session['session_id'])).first().score}')
    # current_app.logger.info(f'LOTR position: {np.where(sorted[:, None] == 75)[0]}')
    # current_app.logger.info(f'LOTR score: {Score.query.filter((Score.book_id == 76) & (Score.session_id == session['session_id'])).first().score}')
    # current_app.logger.info(f'Martian position: {np.where(sorted[:, None] == 324)[0]}')
    # current_app.logger.info(f'Martian score: {Score.query.filter((Score.book_id == 325) & (Score.session_id == session['session_id'])).first().score}')
    
    books_sampled = [book_ids[book] for book in books_sampled]
    books_sampled.sort()
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
    centroids = kmeans.cluster_centers_ / np.linalg.norm(kmeans.cluster_centers_, axis=1, keepdims=True)
    Session.assign_centroids(centroids)

    best_embeddings = {}

    # Find 5 best matching book descriptions for each cluster
    for cluster_id in range(4):
        cluster_indices = np.where(labels == cluster_id)[0]

        best_ids = [book_ids[i] for i in cluster_indices]

        best_books = Book.query.filter(Book.id.in_(best_ids)).all()

        best_books_sorted = sorted(best_books, key=lambda book: int(book.id))[:5]
        best_embeddings[cluster_id] = best_books_sorted

    return best_embeddings

def update_scores(scores: list[Score], embeddings, selected_cluster: int, disable_books: list[str], sigma: np.float32 = np.float32(0.25)):

    try:

        centroids = Session.get_centroids()

        scores_list = []

        # Score calculation based on embedding distance
        for score, embedding in zip(scores, embeddings):
        
            disp_sum = 0
            for x in centroids:

                if not np.array_equal(x, centroids[selected_cluster]):
                    disp_sum += np.exp(-(1 - np.dot(x, embedding)) / sigma)
            
            like_val = np.exp(-(1 - np.dot(centroids[selected_cluster], embedding)) / sigma)
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
    
    except Exception as e:
        current_app.logger.exception(e)


def disable_books(book_ids: list[int]):
    scores = Score.get_scores_from_sample(book_ids)
    for score in scores:
        score.score = float(np.e**(-10))
    db.session.commit()

def get_sigma():
    if int(Session.get_rounds()) < 1:
        if session['type'] == 'descriptions':
            sigma = random.sample([0.02, 0.03, 0.04, 0.05, 0.06], 1)[0]
        else:
            sigma = random.sample([0.2, 0.22, 0.24, 0.18, 0.16], 1)[0]
        if sigma:
            Session.assign_sigma(sigma)
        else:
            current_app.logger.error(f"No sigma")
    else:
        sigma = Session.query.filter(Session.id == session['session_id']).first().sigma
        if not sigma:
            current_app.logger.error(f"No sigma")
            if session['type'] == 'descriptions':
                sigma = random.sample([0.02, 0.03, 0.04, 0.05, 0.06], 1)[0]
            else:
                sigma = random.sample([0.2, 0.22, 0.24, 0.18, 0.16], 1)[0]
            if sigma:
                Session.assign_sigma(sigma)
    return sigma
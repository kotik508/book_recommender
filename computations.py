from scipy.spatial.distance import cdist
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from text_generation import create_prompt, get_description
from website.models import Score, Session, Book
from website import genai_client
import numpy as np
import pandas as pd


def get_answers(embeddings, scores, books):
    hights_ind = np.argsort(scores)[-5:][::-1]
    print(scores[hights_ind])

    labels, centroids, best_embeddings = clustering(embeddings, scores)

    summaries = {}
    for cluster in best_embeddings.keys():
        prompt = create_prompt(books.loc[best_embeddings[cluster], 'description'].tolist())
        summaries[cluster] = get_description(genai_client, prompt)

    return "Which of these descriptions best suits your book preference?", summaries

def create_embeddings():
    model = SentenceTransformer('Snowflake/snowflake-arctic-embed-l-v2.0')

    books = pd.read_csv('goodreads_scraper/books_cleaned.csv')

    embeddings = model.encode(books['description'], )

    print('Embeddings created')

    np.save('../embeddings.npy', embeddings)

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

    for i in range(len(centroids)):
        centroids[i] = centroids[i].tolist()

    return labels, centroids, best_embeddings

def initialize_scores(books_len: int):
    scores = np.full(books_len, 1/books_len)
    return scores


def update_scores(scores, embeddings, selected_cluster, centroids, sigma: np.float32 = np.float32(0.05)):

    # lowest_dist = 0
    # lowest_dist_ind = None
    res = np.full(len(embeddings), np.float32(1))
    for index, book in enumerate(embeddings):
        disp_sum = 0
        for x in centroids:

            if not np.array_equal(x, selected_cluster):
                disp_sum += np.exp(-(np.divide(np.linalg.norm(x - book), sigma)))

        like_val = np.exp(-(np.divide(np.linalg.norm(selected_cluster - book), sigma)))
        res[index] = res[index] * (like_val / (disp_sum + like_val)) * scores[index]

        # dist = like_val / (disp_sum + like_val)
        # if dist > lowest_dist:
        #     lowest_dist = dist
        #     lowest_dist_ind = index

    res = np.divide(res, np.max(res))
    # print(f'Highest score: {np.argmax(res)}')
    # print(f'Lowest distance: {lowest_dist_ind}')

    return res

def update_scores_obj(books: list[Book], selected_cluster: int, centroids, sigma: np.float32 = np.float(32)):

    # Score calculation based on embedding distance
    for book in books:
        disp_sum = 0
        for x in centroids:

            if not np.array_equal(x, centroids[selected_cluster]):
                disp_sum += np.exp(-(np.divide(np.linalg.norm(x - np.array(book.embedding), sigma))))
        
        like_val = np.exp(-(np.divide(np.linalg.norm(centroids[selected_cluster] - np.array(book.embedding), sigma))))
        book.score = book.score * (like_val / (disp_sum + like_val))

    # Score adjustment to keep values between 0 and 1
    books_cal = np.array([book.score for book in books])
    scores = np.divide(books_cal, np.max(books_cal))

    for book, new_score in zip(books, scores):
        book.score = new_score


import numpy as np


def initialize_scores(books_len: int):
    scores = np.full(books_len, 0.1)
    return scores


def update_scores(scores, embeddings, selected_cluster, centroids, sigma: np.float32 = np.float32(0.01)):

    res = np.full(len(embeddings), np.float32(1))
    for index, book in enumerate(embeddings):
        disp_sum = 0
        for x in centroids:

            if x != selected_cluster:
                disp_sum += np.exp(-(np.divide(np.linalg.norm(x - book), sigma)))

        like_val = np.exp(-(np.divide(np.linalg.norm(selected_cluster - book), sigma)))
        res[index] = res[index] * (like_val / (disp_sum + like_val)) * scores[index]

    res = np.divide(res, np.max(res))

    return res


def compute_centroids(embeddings, clusters):
    return None
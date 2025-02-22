from computations import load_embeddings, cluster
from scores import initialize_scores
import numpy as np



embeddings = load_embeddings()

scores = initialize_scores(len(embeddings))

labels, centroids = cluster(embeddings, scores)

print(centroids)

# clusters = {}
#
# for cluster in np.unique(results):
#     print(cluster)
#     clusters[cluster] = np.where(results == cluster)[0].tolist()
#
# print(clusters[np.int32(1)])
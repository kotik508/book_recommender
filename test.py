from computations import load_embeddings
import numpy as np



d = {}

d['1'] = [1, 5, 6]
d['tes'] = [9, 8, 9]

for i, l in d.items():
    print(d[i])
    print('---')
    print(l)
# clusters = {}
#
# for cluster in np.unique(results):
#     print(cluster)
#     clusters[cluster] = np.where(results == cluster)[0].tolist()
#
# print(clusters[np.int32(1)])
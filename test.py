import numpy as np

sel = np.array([5, 1, 3])

ar = np.array([1, 6, 9, 3, 5, 7])


ranked_ar = np.argsort(-ar)
print(ranked_ar[:, None])
print(np.where(ranked_ar[:, None] == 4)[0])
import pandas as pd
import numpy as np
import ast
import umap
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objs as go
from collections import Counter

embeddings = np.load('data/svd_vectors.npy') 
books = pd.read_csv('../bakalarka/goodreads_scraper/books_cleaned.csv')
books['tags'] = books['tags'].apply(ast.literal_eval)

kmeans = KMeans(n_clusters=4, n_init=10, max_iter=1000, random_state=42)
kmeans.fit(embeddings)
labels = kmeans.labels_

u_2d = umap.UMAP(n_components=2, n_neighbors=250, random_state=42)
umap_2d = u_2d.fit(embeddings)

highlighted_authors = {'J.R.R. Tolkien', 'J.K. Rowling', 'Oscar Wilde', 'William Shakespeare', 'John Green', 'Jo Nesbø'}
highlighted_books = {'The Fellowship of the Ring', 'The Return of the King',
                     'The Snowman', 'Harry Potter and the Goblet of Fire', 'The Picture of Dorian Gray', 'Romeo and Juliet',
                     'The Fault in Our Stars'}

books['cluster'] = labels

excluded = {'Fiction', 'Audiobook'}
top_tags_per_cluster = {}

for cluster_id, group in books.groupby('cluster'):
    all_tags = sum(group['tags'], [])
    filtered_tags = [tag for tag in all_tags if tag not in excluded]
    top_tags = [tag for tag, _ in Counter(filtered_tags).most_common(3)]
    top_tags_per_cluster[cluster_id] = top_tags

df = pd.DataFrame(umap_2d.embedding_, columns=['x', 'y'])
df['title'] = books['book_title']
df['author'] = books['author']
df['highlight'] = df.apply(lambda t: 'highlight' if (t['author'] in highlighted_authors) and (t['title'] in highlighted_books) else 'normal', axis=1)
df['knn_label'] = labels

color_map = {0: '#AB63FA', 1: '#EF553B', 2: '#00CC96', 3: '#636EFA', 'highlight': 'black'}
marker_symbols = ['circle', 'diamond', 'cross', 'triangle-up', 'triangle-down', 'square', 'star', 'hexagram', 'x', 'pentagon']

fig = go.Figure()

for cluster_label in sorted(df['knn_label'].unique()):
    cluster_df = df[(df['highlight'] == 'normal') & (df['knn_label'] == cluster_label)]
    top_tags = ', '.join(top_tags_per_cluster.get(cluster_label, []))
    fig.add_trace(go.Scatter(
        x=cluster_df['x'],
        y=cluster_df['y'],
        mode='markers',
        marker=dict(
            size=6,
            color=color_map[cluster_label],
            opacity=0.7
        ),
        name=f'Cluster {cluster_label}: {top_tags}',
        hovertext=cluster_df['title'],
        hoverinfo='text'
    ))

highlighted_df = df[df['highlight'] == 'highlight'].reset_index(drop=True)
for i, row in highlighted_df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row['x']],
        y=[row['y']],
        mode='markers+text',
        marker=dict(
            size=12,
            color='black',
            symbol=marker_symbols[i % len(marker_symbols)],
        ),
        text=row['title'],
        textposition='top center',
        hoverinfo='text',
        textfont=dict(
            size=30,
            color='black',
            family='Arial'
        ),
        showlegend=False
    ))

fig.update_layout(
    legend_title="Clusters",
    template="plotly_white",
    legend=dict(
        font=dict(
            size=30
        )
    )
)

fig.show()

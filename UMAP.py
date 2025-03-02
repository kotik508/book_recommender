import pandas as pd
import ast
import umap
import plotly.express as px
import plotly.graph_objs as go
from computations import load_embeddings, clustering, initialize_scores

embeddings = load_embeddings()
scores = initialize_scores(len(embeddings))
books = pd.read_csv('goodreads_scraper/books_cleaned.csv')
books['tags'] = books['tags'].apply(ast.literal_eval)
labels, centroids, best_embeddings = clustering(embeddings, scores)

u_2d = umap.UMAP(n_components=2, n_neighbors=250)
umap_2d = u_2d.fit(embeddings)

print(umap_2d.embedding_.shape)
print(len(books))


highlighted_authors = {'J.R.R. Tolkien', 'J.K. Rowling', 'Oscar Wilde', 'William Shakespeare', 'John Green'}
highlighted_books = {'The Fellowship of the Ring', 'The Two Towers', 'The Return of the King',
                     'Harry Potter and the Chamber of Secrets', 'Harry Potter and the Goblet of Fire',
                     'Harry Potter and the Deathly Hallows', 'The Picture of Dorian Gray', 'Romeo and Juliet',
                     'The Fault in Our Stars'}

df = pd.DataFrame(umap_2d.embedding_, columns=['x', 'y'])
df['title'] = books['book_title']
df['author'] = books['author']
df['highlight'] = df.apply(lambda t: 'highlight' if (t['author'] in highlighted_authors) and (t['title'] in highlighted_books ) else 'normal', axis=1)
df['knn_label'] = labels

color_map = {0: '#AB63FA', 1: '#EF553B', 2: '#00CC96', 3: '#636EFA', 'highlight': 'black'}

centroids = df.groupby('knn_label')[['x', 'y']].mean().reset_index()
centroids['title'] = 'Centroid ' + centroids['knn_label'].astype(str)

fig = px.scatter(
    df[df['highlight'] == 'normal'], x='x', y='y', hover_data=['title'],
    color=df[df['highlight'] == 'normal']['knn_label'].astype(str),
    title="UMAP with Highlighted Books",
    color_discrete_map={str(k): v for k, v in color_map.items()},
)

fig.update_traces(marker=dict(opacity=0.4), selector=dict(mode='markers'))

# Plot highlighted points (black)
fig.add_scatter(
    x=df[df['highlight'] == 'highlight']['x'],
    y=df[df['highlight'] == 'highlight']['y'],
    mode='markers', marker=dict(size=12, color='black', symbol='star'),
    name="Highlighted Books"
)

fig.add_trace(go.Scatter(
    x=df[df['highlight'] == 'highlight']['x'],
    y=df[df['highlight'] == 'highlight']['y'],
    mode='text',
    text=df[df['highlight'] == 'highlight']['title'],
    textposition='top center',
    marker=dict(size=12, color='black', symbol='star', opacity=0),
    showlegend=False
))

fig.show()
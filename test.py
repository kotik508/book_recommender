import pandas as pd
import ast
import umap
import plotly.express as px
from computations import load_embeddings, clustering, initialize_scores
import matplotlib.pyplot as plt

embeddings = load_embeddings()
scores = initialize_scores(len(embeddings))
books = pd.read_csv('goodreads_scraper/books_cleaned.csv')
books['tags'] = books['tags'].apply(ast.literal_eval)
labels, centroids, best_embeddings = clustering(embeddings, scores)

u_2d = umap.UMAP(n_components=2, n_neighbors=250)
umap_2d = u_2d.fit(embeddings)

print(umap_2d.embedding_.shape)
print(len(books))



highlighted_books = {'Harry Potter and the Order of the Phoenix', 'Harry Potter and the Chamber of Secrets', 
                     'Harry Potter and the Goblet of Fire', 'The Chronicles of Narnia', 'The Fellowship of the Ring',
                     'The Two Towers', 'The Return of the King', 'The Great Gatsby'}

df = pd.DataFrame(umap_2d.embedding_, columns=['x', 'y'])
df['title'] = books['book_title']
df['highlight'] = df['title'].apply(lambda t: 'highlight' if t in highlighted_books else 'normal')
df['knn_label'] = labels

color_map = {0: '#AB63FA', 1: '#EF553B', 2: '#00CC96', 3: '#636EFA', 'highlight': 'black'}

centroids = df.groupby('knn_label')[['x', 'y']].mean().reset_index()
centroids['title'] = 'Centroid ' + centroids['knn_label'].astype(str)

fig = px.scatter(
    df[df['highlight'] == 'normal'], x='x', y='y', hover_data=['title'], 
    color=df[df['highlight'] == 'normal']['knn_label'].astype(str),
    title="UMAP with Highlighted Books",
    color_discrete_map={str(k): v for k, v in color_map.items()}
)

# Plot highlighted points (black)
fig.add_scatter(
    x=df[df['highlight'] == 'highlight']['x'], 
    y=df[df['highlight'] == 'highlight']['y'], 
    mode='markers', marker=dict(size=12, color='black', symbol='star'),
    name="Highlighted Books"
)

annotations = []

arrow_offset = 0.2  # Adjusts arrow length
label_offset_y = 0.25  # Adjusts text position to prevent overlap

highlight_df = df[df['highlight'] == 'highlight'].sort_values(by='y')

# Add arrows + labels
for i, (_, row) in enumerate(highlight_df.iterrows()):
    y_adjustment = ((i % 2) * 2 - 1) * label_offset_y  # Alternate up and down
    annotations.append(
        dict(
            x=row['x'], y=row['y'],  # Arrow points to book
            xref="x", yref="y",
            ax=row['x'] + arrow_offset,  
            ay=row['y'] + arrow_offset + y_adjustment,  # Shift text up/down
            axref="x", ayref="y",
            text=row['title'],  # Book title as label
            showarrow=True,
            arrowhead=2,
            arrowsize=2,  # Thicker arrow
            arrowcolor="black",
            font=dict(size=12, color="black"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
    )

# Apply annotations
fig.update_layout(annotations=annotations)

fig.show()
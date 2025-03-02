import numpy as np
from computations import initialize_scores, update_scores, clustering, load_embeddings
from text_generation import init_genai, create_prompt, get_description
import pandas as pd
import ast
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'se159'

genai_client = init_genai()

centroids = None
best_embeddings = None

books = pd.read_csv('goodreads_scraper/books_cleaned.csv')
books['tags'] = books['tags'].apply(ast.literal_eval)

scores = initialize_scores(len(books))
embeddings = load_embeddings()

def update_clusters():
    return

def get_answers():
    global centroids, best_embeddings, scores
    hights_ind = np.argsort(scores)[-5:][::-1]
    print(scores[hights_ind])

    labels, centroids, best_embeddings = clustering(embeddings, scores)

    summaries = {}
    for cluster in best_embeddings.keys():
        prompt = create_prompt(books.loc[best_embeddings[cluster], 'description'].tolist())
        summaries[cluster] = get_description(genai_client, prompt)

    return "Který z těchto popisů nejvíce vystihuje knihu, kterou byste si rád přečetl/přečetla?", summaries

@app.route("/")
def home():
    question, answers = get_answers()
    return render_template("main_page.html", question=question, answers=answers)

@app.route("/submit", methods=['POST'])
def submit():
    global centroids, best_embeddings, scores
    selected_answer = request.form.get("answer")
    print(f"User selected: {selected_answer}")
    print(centroids[3])

    if max(scores) <= 0.85:
        scores = update_scores(scores, embeddings, centroids[int(selected_answer)], centroids)
        print(f'scores {scores}')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('final_page', message=books.loc[np.max(scores), "description"]))

@app.route("/final")
def final_page():
    message = request.args.get('message', 'Def if nothing')
    return message

if __name__ == "__main__":
    app.run(debug=True)

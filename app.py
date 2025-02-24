import time
import numpy as np
from computations import initialize_scores, update_scores, clustering, load_embeddings
import pandas as pd
import ast
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'se159'

books = pd.read_csv('goodreads_scraper/books_desc.csv')
books['tags'] = books['tags'].apply(ast.literal_eval)

scores = initialize_scores(len(books))
embeddings = load_embeddings()

def get_answers():
    hights_ind = np.argsort(scores)[-5:][::-1]
    print(scores[hights_ind])

    labels, centroids, best_embeddings = clustering(embeddings, scores)

    summaries = {}
    for cluster in best_embeddings.keys():
        time.sleep(1)
        summaries[cluster] = books.loc[best_embeddings[cluster][0], 'description']

    return "Který z těchto popisů nejvíce vystihuje knihu, kterou byste si rád přečetl/přečetla?", summaries

@app.route("/")
def home():
    question, answers = get_answers()
    return render_template("main_page.html", question=question, answers=answers)

@app.route("/submit", methods=['POST'])
def submit():
    selected_answer = request.form.get("answer")
    print(f"User selected: {selected_answer}")

    if max(scores) <= 0.85:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('final_page', message=books.iloc[np.max(scores), "description"]))

@app.route("/final")
def final_page():
    message = request.args.get('message', 'Def if nothing')
    return message

if __name__ == "__main__":
    app.run(debug=True)

from flask import Blueprint, redirect, render_template, url_for, request
from computations import update_scores

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
    # question, answers = get_answers()
    # return render_template("main_page.html", question=question, answers=answers)
        return render_template('home.html')

# @views.route("/submit", methods=['POST'])
# def submit():
#     global centroids, best_embeddings, scores, rnd
#     selected_answer = request.form.get("answer")
#     print(f"User selected: {selected_answer}")
#     print(centroids[3])
#     scores = update_scores(scores, embeddings, centroids[int(selected_answer)], centroids)
#     rnd += 1

#     if max(scores) <= 0.85 or rnd < 4:
#         return render_template("main_page.html", question=question, answers=answers)
#     else:
#         print(books.loc[int(np.max(np.argsort(scores)[-1:])), "book_title"])
#         return redirect(url_for('final_page', message=books.loc[int(np.max(np.argsort(scores)[-1:])), "description"]))
    
# @app.route("/final")
# def final_page():
#     message = request.args.get('message', 'Def if nothing')
#     return message

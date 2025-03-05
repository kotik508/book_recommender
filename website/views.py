from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from computations import update_scores
from .models import Session, Book, Score
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        new_session = Session()
        db.session.add(new_session)
        session['session_id'] = new_session.id

        books = Book.query.all()
        scores = [Score(session_id=new_session.id, book_id=b.id, score=1/len(books)) for b in books]
        db.session.add_all(scores)

        db.session.commit()
        flash('Started a session!', category='success')

    return render_template('main_page.html')

@views.route('/books', methods=['GET', 'POST'])
def books():
    return render_template('base.html')
    

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

from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from .computations import update_scores, get_answers
from .models import Session, Book, Score
from . import db
import random

views = Blueprint('views', __name__)


@views.route('/books', methods=['GET', 'POST'])
def book_choice():
    if request.method == 'GET':
        return render_template('main_page.html', summaries=session['summaries'])
    
    elif request.method == 'POST':
        Session.increase_session_round()
        
        scores = Score.query.filter(Score.session_id == session['session_id'])
        selected_cluster = int(request.form.get('answer'))

        update_scores(scores, selected_cluster, )
        return render_template('base.html')
    
@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

    elif request.method == 'POST':

        new_session = Session()
        db.session.add(new_session)
        db.session.commit()
        session['session_id'] = new_session.id

        books = Book.query.all()
        scores = [Score(session_id=new_session.id, book_id=b.id, score=1/len(books)) for b in books]
        db.session.add_all(scores)

        db.session.commit()
        flash('Started a session!', category='success')

        sampled_books = random.sample(books, 500)

        session['summaries'] = get_answers(sampled_books)

    return redirect(url_for('views.book_choice'))

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

from flask import Blueprint, redirect, render_template, url_for, request, flash, session, jsonify
from .computations import update_scores, get_answers
from .models import Session, Book, Score
from . import db
import numpy as np
import time

views = Blueprint('views', __name__)


@views.route('/books', methods=['GET', 'POST'])
def book_choice():
    if request.method == 'GET':
        best_books = Book.get_best_books()
        # for book in best_books:
            # print(f'{book.title}: {Score.get_score(int(session['session_id']), book.id)}')
        picked_books = Session.get_picked_books()
        return render_template('main_page.html', summaries=session['summaries'], round=Session.get_rounds(), 
                               best_books=best_books, picked_books=picked_books)
    
    elif request.method == 'POST':
        

        if request.is_json:
            data = request.get_json()
            Session.move_book(int(data['book_id']), data['add'])
            best_books = Book.get_best_books()
            return jsonify({
                'status': 'success',
                'message': 'Book picked/removed'
            }), 200

        else:
            Session.increase_session_round()

            if session['type'] == 'descriptions':
                embeddings = np.array(Book.get_embeddings())
            elif session['type'] == 'tags':
                embeddings = np.array(Book.get_svds())
            else:
                print(f'WARNING INVALID SESSION TYPE: {session['type']}')
                embeddings = np.array(Book.get_embeddings())
            
            scores = Score.query.filter(Score.session_id == session['session_id'])
            selected_cluster = int(request.form.get('answer'))

            now = time.time()
            update_scores(scores, embeddings, selected_cluster)
            print(f'Update scores took: {round(time.time()- now)} seconds')

            if Session.query.filter(Session.id == session['session_id']).first().rounds < 11:
                get_answers()
                return redirect(url_for('views.book_choice'))
            else:
                return redirect(url_for('views.final_page'))

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

    elif request.method == 'POST':

        session['type'] = request.form.get('action')

        new_session = Session()
        db.session.add(new_session)
        db.session.commit()
        session['session_id'] = new_session.id

        books = Book.query.all()
        scores = [Score(session_id=new_session.id, book_id=b.id, score=1/len(books)) for b in books]
        db.session.add_all(scores)

        db.session.commit()
        flash('Started a session!', category='success')

        now = time.time()
        get_answers()
        print(f'Prepare questions took: {round(time.time()- now)} seconds')

    return redirect(url_for('views.book_choice'))

@views.route('/final', methods=['GET'])
def final_page():
    picked_books = Session.get_picked_books()
    if len(picked_books) < 5:
        recom_books = Book.get_best_books()
    return render_template('final.html', picked_books=picked_books, recom_books=recom_books)


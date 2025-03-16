from flask import Blueprint, redirect, render_template, url_for, request, flash, session, jsonify, current_app
from .computations import update_scores, get_answers
from .models import Session, Book, Score
import asyncio
from .text_generation import get_description
from . import db
import numpy as np
import time

views = Blueprint('views', __name__)


@views.route('/books', methods=['GET', 'POST'])
async def book_choice():
    if request.method == 'GET':
        best_books = Book.get_best_books()
        picked_books = Session.get_picked_books()
        current_app.logger.info(f'Session: {session["session_id"]} in round: {Session.get_rounds()} has these picked books: {", ".join(str(book.id) for book in picked_books)}')
        current_app.logger.info(f'Session: {session["session_id"]} in round: {Session.get_rounds()} has these best books: {", ".join(str(book.id) for book in best_books[:5])}')
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

            if session['type'] == 'descriptions':
                embeddings = np.array(Book.get_embeddings())
            elif session['type'] == 'tags':
                embeddings = np.array(Book.get_svds())
            else:
                current_app.logger.warning(f'WARNING INVALID SESSION TYPE: {session['type']}')
                embeddings = np.array(Book.get_embeddings())
            
            scores = Score.query.filter(Score.session_id == session['session_id'])
            selected_cluster = int(request.form.get('answer'))

            now = time.time()
            update_scores(scores, embeddings, selected_cluster)
            current_app.logger.info(f'Update scores for session: {session['session_id']} and round: {Session.get_rounds()} took: {round(time.time()- now)} seconds')

            if Session.query.filter(Session.id == session['session_id']).first().rounds < 11:
                now = time.time()
                await get_answers()
                current_app.logger.info(f'Generating descriptions took: {round(time.time()- now, 4)} seconds')
                Session.increase_session_round()
                current_app.logger.info(f'Moving session with id: {session['session_id']} to round: {Session.get_rounds()}')
                return redirect(url_for('views.book_choice'))
            else:
                return redirect(url_for('views.final_page'))

@views.route('/', methods=['GET', 'POST'])
async def home():
    if request.method == 'GET':
        return render_template('home.html')

    elif request.method == 'POST':

        new_session = Session()
        db.session.add(new_session)
        db.session.commit()
        session['session_id'] = new_session.id
        session['type'] = 'description' if new_session.id % 2 == 1 else 'tags'
        new_session.version = session['type']
        db.session.commit()

        books = Book.query.all()
        scores = [Score(session_id=new_session.id, book_id=b.id, score=1/len(books)) for b in books]
        db.session.add_all(scores)

        db.session.commit()
        flash('Started a session!', category='success')

        now = time.time()
        await get_answers()
        current_app.logger.info(f'Generating descriptions took: {round(time.time()- now, 4)} seconds')
    
        current_app.logger.info(f'Started session: {session['session_id']} with type: {Session.get_type()}.')

    return redirect(url_for('views.book_choice'))

@views.route('/final', methods=['GET'])
def final_page():
    picked_books = Session.get_picked_books()
    recom_books = Book.get_best_books()
    recom_ids = [book.id for book in recom_books[:5]]
    Session.move_to_recommend(recom_ids)
    current_app.logger.info(f'Session: {session["session_id"]} ended with these picked books: {", ".join(str(book.id) for book in picked_books)}')
    current_app.logger.info(f'Session: {session["session_id"]} ended with these recommended books: {", ".join(str(book.id) for book in recom_books[:5])}')
    return render_template('final.html', picked_books=picked_books, recom_books=recom_books)


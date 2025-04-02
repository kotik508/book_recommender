from flask import Blueprint, redirect, render_template, url_for, request, flash, session, jsonify, current_app
from .computations import update_scores, get_answers, disable_books
import uuid
from .models import Session, Book, Score
from . import db
import numpy as np
import time
import random

views = Blueprint('views', __name__)


@views.route('/books', methods=['GET', 'POST'])
def book_choice():
    if request.method == 'GET':
        show_books = Book.get_best_books()
        try:
            bb_tags = Book.get_tags(show_books['best_books'])
        except Exception as e:
            current_app.logger.exception(e)
        sb_tags = Book.get_tags(show_books['sampled_books'])
        picked_books = Session.get_picked_books()
        pb_tags = Book.get_tags(picked_books)
        current_app.logger.info(f'Session: {session["session_id"]} in round: {Session.get_rounds()} has these picked books: {", ".join(str(book.id) for book in picked_books)}')
        current_app.logger.info(f'Session: {session["session_id"]} in round: {Session.get_rounds()} has these best books: {", ".join(str(book.id) for book in show_books['best_books']+show_books['sampled_books'])}')
        return render_template('main_page.html', summaries=Session.get_summaries(), round=Session.get_rounds(), 
                               best_books=show_books['best_books'], sampled_books=show_books['sampled_books'], 
                               picked_books=picked_books, session_code=session['session_code'],
                               bb_tags=bb_tags, sb_tags=sb_tags, pb_tags=pb_tags)
    
    elif request.method == 'POST':
        

        if request.is_json:
            data = request.get_json()
            Session.move_book(int(data['book_id']), data['add'])
            return jsonify({
                'status': 'success',
                'message': 'Book picked/removed'
            }), 200

        else:
            dis_books = request.form.get("book_ids", "").split(",")
            dis_books = list(map(int, dis_books))

            if request.form.get("answer"):

                if session['type'] == 'descriptions':
                    embeddings = np.array(Book.get_embeddings())
                elif session['type'] == 'tags':
                    embeddings = np.array(Book.get_svds())
                else:
                    current_app.logger.warning(f'INVALID SESSION TYPE: {session['type']}')
                    embeddings = np.array(Book.get_embeddings())

                
                scores = Score.query.filter(Score.session_id == session['session_id']).order_by(Score.book_id).all()
                selected_cluster = int(request.form.get('answer'))

                now = time.time()
                if int(Session.get_rounds()) < 1:
                    if session['type'] == 'descriptions':
                        sigma = random.sample([0.02, 0.03, 0.04, 0.05, 0.06], 1)[0]
                    else:
                        sigma = random.sample([0.2, 0.22, 0.24, 0.18, 0.16], 1)[0]
                else:
                    sigma = Session.query.filter(Session.id == session['session_id']).first().sigma

                update_scores(scores=scores, embeddings=embeddings, selected_cluster=selected_cluster,
                                disable_books=dis_books, sigma=sigma)
                Session.assign_sigma(sigma)
                current_app.logger.info(f'Update scores for session: {session['session_id']} and round: {Session.get_rounds()} took: {round(time.time()- now)} seconds')
            else:
                disable_books(dis_books)

            if Session.query.filter(Session.id == session['session_id']).first().rounds < 10:
                now = time.time()
                book_ids = Book.get_book_ids()
                get_answers(book_ids)
                current_app.logger.info(f'Generating descriptions took: {round(time.time()- now, 4)} seconds')
                Session.increase_session_round()
                current_app.logger.info(f'Moving session with id: {session['session_id']} to round: {Session.get_rounds()}')
                return redirect(url_for('views.book_choice'))
            else:
                return redirect(url_for('views.final_page'))


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

    elif request.method == 'POST':

        if request.form.get('session_code'):
            sess_code = request.form.get('session_code')
            try:
                session['session_code'] = sess_code
                sess = Session.query.filter(Session.code == sess_code).first()
                session['session_id'] = sess.id
                session['type'] = sess.type
                flash(f'Loaded a session with code {sess_code}!', category='success')
                current_app.logger.info(f'Loaded session: {session['session_id']} with type: {Session.get_type()}.')
            except Exception as e:
                current_app.logger.exception(f'Tried to load a session with incorrect code: {sess_code}.')
                flash(f'Incorrect session code', category='error')
                return redirect(url_for('views.home'))
        else:
            session['session_code'] = str(uuid.uuid4())[:8]
            new_session = Session(code=session['session_code'])
            db.session.add(new_session)
            db.session.commit()
            session['session_id'] = new_session.id
            session['type'] = 'descriptions' if new_session.id % 2 == 1 else 'tags'
            new_session.type = session['type']
            db.session.commit()
            book_ids = Book.get_book_ids()
            scores = [Score(session_id=new_session.id, book_id=b, score=1/len(book_ids)) for b in book_ids]
            db.session.add_all(scores)

            db.session.commit()
            flash('Started a session!', category='success')

            now = time.time()
            get_answers(book_ids)
            current_app.logger.info(f'Generating descriptions took: {round(time.time()- now, 4)} seconds')
        
            current_app.logger.info(f'Started session: {session['session_id']} with type: {Session.get_type()}.')

    return redirect(url_for('views.book_choice'))

@views.route('/final', methods=['GET', 'POST'])
def final_page():
    if request.method == "GET":
        picked_books = Session.get_picked_books()
        recom_books = Book.get_best_books()
        recom_ids = [book.id for book in recom_books['best_books'][:5]]
        Session.move_to_recommend(recom_ids)
        current_app.logger.info(f'Session: {session["session_id"]} ended with these picked books: {", ".join(str(book.id) for book in picked_books)}')
        current_app.logger.info(f'Session: {session["session_id"]} ended with these recommended books: {", ".join(str(book.id) for book in recom_books['best_books'])}')
        return render_template('final.html', picked_books=picked_books, recom_books=recom_books['best_books'][:5],
                               session_code=session['session_code'])
    
    if request.method == "POST":
        sess = Session.query.filter(Session.id==session['session_id']).first()
        sess.age_category = request.form.get("age_category") if request.form.get("age_category") != "" else None
        sess.email = request.form.get("email") if request.form.get("email") != "" else None
        sess.gender = request.form.get("gender") if request.form.get("gender") != "" else None
        sess.education = request.form.get("education") if request.form.get("education") != "" else None
        db.session.commit()
        current_app.logger.info(f'Session {sess.id} has age category: {sess.age_category}')
        current_app.logger.info(f'Session {sess.id} has gender: {sess.gender}')
        current_app.logger.info(f'Session {sess.id} has education: {sess.education}')
        current_app.logger.info(f'Session {sess.id} has email: {sess.email}')
        return jsonify({
                'status': 'success',
                'message': 'Demography added'
            }), 200
    

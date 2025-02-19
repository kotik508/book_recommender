from pyexpat.errors import messages

from flask import Flask, render_template, request, redirect, url_for
from books import init_books

app = Flask(__name__)

books = init_books()

def get_answers():
    return "Který z těchto popisů nejvíce vystihuje knihu, kterou byste si rád přečetl/přečetla?", books.nlargest(4, 'score')

@app.route("/")
def home():
    question, answers = get_answers()
    return render_template("main_page.html", question=question, answers=answers)

@app.route("/submit", methods=['POST'])
def submit():
    selected_answer = request.form.get("answer")
    print(f"User selected: {selected_answer}")
    print(books.iloc[int(selected_answer)]['description'])
    books.loc[int(selected_answer), 'score'] += 0.2

    if max(books['score']) <= 0.85:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('final_page', message=books.iloc[books["score"].idxmax()]["description"]))

@app.route("/final")
def final_page():
    message = request.args.get('message', 'Def if nothing')
    return message

if __name__ == "__main__":
    app.run(debug=True)

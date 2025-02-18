from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    question = "Který z těchto popisů nejvíce vystihuje knihu, kterou byste si rád přečetl/přečetla?"
    answers = ["Could you survive on your own in the wild, with every one out to make sure you don't live to see the morning? In the ruins of a place once known as North America lies the nation of Panem, a shining Capitol surrounded by twelve outlying districts. The Capitol is harsh and cruel and keeps the districts in line by forcing them all to send one boy and one girl between the ages of twelve and eighteen to participate in the annual Hunger Games, a fight to the death on live TV. Sixteen-year-old Katniss Everdeen", "Book description two", "Book description three", "Book description four"]
    return render_template("main_page.html", question=question, answers=answers)

if __name__ == "__main__":
    app.run(debug=True)

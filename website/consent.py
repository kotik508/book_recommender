from flask import Blueprint

consent = Blueprint('consent', __name__)

@consent.route('/consent')
def consent():
    return "<p>Consent</p>"


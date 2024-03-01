from flask import Flask, jsonify, send_from_directory, abort, request
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

import requests
import os

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_DEFAULT_SENDER'] = 'risingstarsbot@gmail.com'
app.config['MAIL_USERNAME'] = 'risingstarsbot@gmail.com'
app.config['MAIL_PASSWORD'] = 'kbas cqzn tkcn dsro'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

CORS(app)
mail = Mail(app)

@app.route("/send-text", methods=['POST'])
def send_text():
    msg = Message("Test",
              recipients=["5129175055@txt.att.net"])
    msg.body = request.json
    mail.send(msg) 
    return request.json

@app.route("/reviews", methods=['GET'])
def get_reviews():
    url = "https://api.yelp.com/v3/businesses/rising-stars-bilingual-daycare-manchaca-2/reviews?limit=20&sort_by=newest"
    apiKey  = os.environ.get('REACT_APP_YELP_REVIEWS_API')
    bearerToken = 'Bearer ' + apiKey
    headers = {
        "access-control-allow-origin":'*',
        "accept": "application/json",
        "Authorization": bearerToken,
   }

    response = requests.get(url, headers=headers)

    review_data = response.json()
    return jsonify(review_data)

app.config["CLIENT_PDFS"] = '/Users/danielgonzalez/Desktop/risingstar-backend/client/documents/pdfs'

@app.route("/get-pdf/<string:file_name>")
def get_pdf(file_name):
    
    try:
        return send_from_directory(app.config["CLIENT_PDFS"], path=file_name, as_attachment=False)
    except FileNotFoundError:
        abort(404)

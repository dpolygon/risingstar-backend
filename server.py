from flask import Flask, jsonify, send_from_directory, abort, request
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
from celery import Celery

import requests
import os

load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('RS_BOT_EMAIL_USERNAME')
app.config['MAIL_USERNAME'] = os.environ.get('RS_BOT_EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('RS_BOT_EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

CORS(app)
mail = Mail(app)
celery = Celery('mail_tasks', broker='redis://localhost:6379/0')

@app.route("/send-mail", methods=['POST'])
def send_mail():
    send_async_mail.delay(request.json)
    return request.json

@celery.task
def send_async_mail(data): 
    with app.app_context():
        msg = Message(f"{data['contactInfo']} {data['name']}",
                    recipients=[os.environ.get('RS_BOT_RECIPIENT')])
        msg.body = data['message']
        mail.send(msg) 

@app.route("/send-text", methods=['POST', 'GET'])
def send_txt():
    bot_token = os.environ.get('RS_BOT_TOKEN')
    user_id = os.environ.get('RS_BOT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    user_data = request.json
    data = {
        "chat_id": user_id,
        "text": "Name: " + user_data['name'] + "\n" + 
                "Number: " + user_data['contactInfo'] + "\n" + 
                "Message: " + user_data['message']
    }
    response = requests.post(url, data=data)
    return jsonify(response.json())

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
        return send_from_directory(app.config["CLIENT_PDFS"], path=file_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)

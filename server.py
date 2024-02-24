from flask import Flask, jsonify, send_from_directory, abort
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

import requests
import os

app = Flask(__name__)
CORS(app)

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

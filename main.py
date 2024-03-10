from flask import Flask, jsonify, send_from_directory, abort, request
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

import requests
import os
import json
import functions_framework

import smtplib, ssl
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import io
from requests_toolbelt.multipart.encoder import MultipartEncoder
import base64

from google.cloud import tasks_v2

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://risingstarsaustin.com"}})

@app.route("/api/send-application", methods=['POST'])
@cross_origin(origin='https://risingstarsaustin.com',headers=['Content- Type','Authorization'])
def send_application() -> tasks_v2.Task:
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(os.environ.get('PROJECT_ID'), os.environ.get('LOCATION'), os.environ.get('QUEUE_NAME'))
    
    data_fields = {
        'name': request.form.get('name'),
        'phone': request.form.get('phoneNumber'),
        'email': request.form.get('email'),
        'childName': request.form.get('childName'),
        'childAge': request.form.get('childAge'),
        'date': request.form.get('date'),
        'message': request.form.get('message')
    }
    file_fields = [{'fileName' : file.filename, 'data' : base64.b64encode(file.read()).decode('utf-8')} for file in request.files.getlist('files')]
    fields = {**data_fields, **{'files' : file_fields}}
    
    task = tasks_v2.Task(
         http_request=tasks_v2.HttpRequest(
              http_method=tasks_v2.HttpMethod.POST,
              url="https://us-central1-rising-stars-backend.cloudfunctions.net/send_app_handler",
              headers={"Content-type": "application/json"},
              body=json.dumps(fields).encode()
         )
    )
    
    # Create and send application task
    response = client.create_task(
        tasks_v2.CreateTaskRequest(parent=parent, task=task)
    )

    print(f"Created mail task {response.name}")
    return jsonify({"message": "Success"}), 200

@functions_framework.http
def send_app_handler(data):
        data = data.json
        print(data)
        
        message = MIMEMultipart()
        message["From"] = os.environ.get('RS_BOT_EMAIL_USERNAME')
        message["To"] = os.environ.get('RS_BOT_RECIPIENT')
        message["Subject"] = "Enrollment Application"
        
        client_information = ("Name: " + data['name'] +
                        "\nPhone Number: " + data['phone'] + 
                        "\nEmail: " + data['email'] + 
                        "\nChild's Name: " + data['childName'] + 
                        "\nChild's Age: " + data['childAge'] + 
                        "\nDesired Start Date: " + data['date'] + 
                        "\nMessage: " + data['message'] + "\n")
        
        client_info_attachment = MIMEText(client_information)
        message.attach(client_info_attachment)

        allowed_extensions = [".zip", ".pdf"]

        for file in data['files']:
            file_name = file['fileName']
            _, file_extension = os.path.splitext(file_name)
            if file_extension.lower() in allowed_extensions:
                file_content = base64.b64decode(file['data'].encode('utf-8'))
                print(f"Adding Attachment: {file_name}")
                
                attachment = MIMEApplication(file_content)
                attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {file_name}",
                )

                message.attach(attachment)

        with smtplib.SMTP_SSL(
            host="smtp.gmail.com", port=465, context=ssl.create_default_context()
        ) as server:
            server.login(os.environ.get('RS_BOT_EMAIL_USERNAME'), os.environ.get('RS_BOT_EMAIL_PASSWORD'))

            server.sendmail(
                from_addr=os.environ.get('RS_BOT_EMAIL_USERNAME'),
                to_addrs=os.environ.get('RS_BOT_RECIPIENT'),
                msg=message.as_string()
            )

        print(f"Application Task completed")
        return jsonify({"message": "Success"}), 200


@app.route("/api/send-mail", methods=['POST'])
@cross_origin(origin='https://risingstarsaustin.com',headers=['Content- Type','Authorization'])
def send_mail() -> tasks_v2.Task:
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(os.environ.get('PROJECT_ID'), os.environ.get('LOCATION'), os.environ.get('QUEUE_NAME'))
    payload = request.json
    task =  tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url="https://us-central1-rising-stars-backend.cloudfunctions.net/send_mail_handler",
            headers={"Content-type": "application/json"},
            body=json.dumps(payload).encode(),
        )
    )

    response = client.create_task(
        tasks_v2.CreateTaskRequest(parent=parent, task=task)
    )

    print(f"Created mail task {response.name}")
    return jsonify({"message": "Success"}), 200

@functions_framework.http
def send_mail_handler(data): 
    usr_data = data.json
    message = MIMEMultipart()

    message["From"] = os.environ.get('RS_BOT_EMAIL_USERNAME')
    message["To"] = os.environ.get('RS_BOT_RECIPIENT')
    message["Subject"] = f"{usr_data['contactInfo']} {usr_data['name']}"

    client_message = MIMEText(usr_data['message'])
    message.attach(client_message)

    with smtplib.SMTP_SSL(
        host="smtp.gmail.com", port=465, context=ssl.create_default_context()
    ) as server:
        server.login(os.environ.get('RS_BOT_EMAIL_USERNAME'), os.environ.get('RS_BOT_EMAIL_PASSWORD'))

        server.sendmail(
            from_addr=os.environ.get('RS_BOT_EMAIL_USERNAME'),
            to_addrs=os.environ.get('RS_BOT_RECIPIENT'),
            msg=message.as_string()
        )

    print(f"Mail Task completed")
    return jsonify({"message": "Success"}), 200

@app.route("/api/send-text", methods=['POST', 'GET'])
@cross_origin(origin='https://risingstarsaustin.com',headers=['Content- Type','Authorization'])
def send_txt() -> tasks_v2.Task:
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(os.environ.get('PROJECT_ID'), os.environ.get('LOCATION'), os.environ.get('QUEUE_NAME'))
    payload = request.json
    task =  tasks_v2.Task(
            http_request=tasks_v2.HttpRequest(
                http_method=tasks_v2.HttpMethod.POST,
                url="https://us-central1-rising-stars-backend.cloudfunctions.net/send_text_handler",
                headers={"Content-type": "application/json"},
                body=json.dumps(payload).encode(),
            )
    )
    response = client.create_task(
        tasks_v2.CreateTaskRequest(parent=parent, task=task)
    )

    print(f"Created text task {response.name}")
    return jsonify({"message": "Success"}), 200

@functions_framework.http
def send_text_handler(data): 
        bot_token = os.environ.get('RS_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        user_id = os.environ.get('RS_BOT_ID')
        user_data = data.json
        
        message = {
            "chat_id": user_id,
            "text": "Name: " + user_data['name'] + "\n" + 
                    "Number: " + user_data['contactInfo'] + "\n" + 
                    "Message: " + user_data['message']
        }
        response = requests.post(url, data=message)
        print(f"Text Task completed")
        return jsonify({"status_code": response.status_code})


@app.route("/api/reviews", methods=['GET'])
@cross_origin(origin='https://risingstarsaustin.com',headers=['Content- Type','Authorization'])
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

app.config["CLIENT_PDFS"] = os.path.join(os.getcwd(), 'client', 'documents', 'pdfs')

@app.route("/api/get-pdf/<string:file_name>")
def get_pdf(file_name):
    
    try:
        return send_from_directory(app.config["CLIENT_PDFS"], path=file_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
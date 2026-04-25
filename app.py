from flask import Flask, request
from flask_cors import CORS
import requests

import scikit_trainer as st


app = Flask(__name__)
CORS(app)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()

    links = data.get('links')
    text_content = data.get('text')
    subject = data.get('subject')

    #print("Received subject: ", subject)
    #print("Received links: ", links)
    #print("Received text content: ", text_content)

    trainer = st.scikit_trainer()
    prediction = trainer.predict(subject, text_content)

    return {"message": "Scan completed successfully!", "prediction": prediction}


app.run(port=8080,debug=True)
from flask import Flask, request
from flask_cors import CORS

import backend.Predicters.scikit_predicter as sp
import backend.Predicters.torch_predicter as tp
import backend.Predicters.bert_predicter as bp


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

    scikit_prediction = scikit_predicter.predict(subject, text_content)
    deep_learning_prediction = deep_learning_predicter.predict(subject, text_content)
    bert_prediction = bert_predicter.predict(subject, text_content)

    w1 = scikit_prediction['Accuracy'] / (scikit_prediction['Accuracy'] + deep_learning_prediction['Accuracy'] + bert_prediction['Accuracy'])
    w2 = deep_learning_prediction['Accuracy'] / (scikit_prediction['Accuracy'] + deep_learning_prediction['Accuracy'] + bert_prediction['Accuracy'])
    w3 = bert_prediction['Accuracy'] / (scikit_prediction['Accuracy'] + deep_learning_prediction['Accuracy'] + bert_prediction['Accuracy'])

    final_prob = w1 * scikit_prediction['probability_phishing'] + w2 * deep_learning_prediction['probability_phishing'] + w3 * bert_prediction['probability_phishing']
    prediction = 1 if final_prob >= 0.5 else 0

    payload = {
        "scikit_weight": w1,
        "deep_learning_weight": w2,
        "bert_weight": w3,
        "weighted_probability_phishing": final_prob,
        "final_prediction": prediction
    }

    return {"message": "Scan completed successfully!", "scikit_randomforest_prediction": scikit_prediction, "deep_learning_prediction": deep_learning_prediction, "bert_prediction": bert_prediction, "Overall_Results": payload}

scikit_predicter = sp.scikit_predicter()
deep_learning_predicter = tp.torch_predicter()
bert_predicter = bp.bert_predicter()

app.run(port=8080,debug=True)
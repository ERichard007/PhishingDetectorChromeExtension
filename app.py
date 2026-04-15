from flask import Flask, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    links = data.get('links')
    text_content = data.get('text')

    print("Received links: ", links)
    print("Received text content: ", text_content)

    return {"message": "Scan completed successfully!"}


app.run(port=8080,debug=True)
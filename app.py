from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan():
    return {"message": "Scan completed successfully!"}


app.run(port=8080,debug=True)
# server.py - Flask web API if needed
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Smart Photo Finder Web API"

if __name__ == "__main__":
    app.run(debug=True)
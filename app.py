from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungle


@app.route('/')
def home():
   return render_template('index.html')

if __name__ == '__main__':  
   app.run('0.0.0.0', port=5001, debug=True)
from pymongo import MongoClient
import jwt
import datetime
import hashlib

from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask.json.provider import JSONProvider

app = Flask(__name__)


client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.books                        # 'jungle'라는 이름의 db를 만듭니다.



@app.route('/')
def home():
   return render_template('login.html')

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)

from pymongo import MongoClient
import jwt
import datetime
import hashlib

from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify, request, redirect, url_for, session

from bson import ObjectId

from flask.json.provider import JSONProvider

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.books                        # 'jungle'라는 이름의 db를 만듭니다.

@app.route('/')
def home():

   #db.users.insert_one({'id':'ghkdgo868','password':'dddd','name':'최우성'})
   #db.books.insert_one({'book_name':'신비한 동물사전','book_comment':'이 책은 대단합니다.','book_image':'test.jpg','user_row_id':'test'})
   #db.rental.insert_one({'rental_place':'교육관 1층','rental_period':'대여 기간','rental_time':'약속 시간','user_row_id':'test', 'book_row_id':'testbook'})
   return render_template('index.html')


@app.route('/mypage/<userId>', methods=['GET'])
def mypage(userId):
   print(userId)

   users = list( db.users.find({'user_id': userId} ) )

   if len(users) > 0 :

      book = list( db.books.find({'user_id': userId} ) )

      rental = []

      for tempBook in book :
         tempRental = list( db.rental.find( {'book_row_id': str(tempBook['_id']) ,'rental_status':'대여 요청' } ) )
         rental.append(tempRental)
      

      #print('rental : ' , rental)
      #print('book : ' , book)

      return render_template('mypage.html', name=userId, book=book,rental=rental)
   else  :
      return render_template('mypage.html', error='No user')
   

   #db.users.insert_one({'id':'ghkdgo868','password':'dddd','name':'최우성'})
   #db.books.insert_one({'book_name':'신비한 동물사전','book_comment':'이 책은 대단합니다.','book_image':'test.jpg','user_row_id':'test'})
   #db.rental.insert_one({'rental_place':'교육관 1층','rental_period':'대여 기간','rental_time':'약속 시간','user_row_id':'test', 'book_row_id':'testbook'})


@app.route('/mypage/<userId>/rental', methods=['POST'])
def mypageRental(userId):
   id = request.form['objId']

   rental = list( db.rental.find({'_id': ObjectId(id)} ) )

   for i in rental :
      i['_id'] = str(i['_id'])


   book = list( db.books.find({'_id':ObjectId(rental[0]['book_row_id'])}) ) 

   for i in book :
      i['_id'] = str(i['_id'])


   return jsonify({'result': book, 'rental':rental})

@app.route('/mypage/<userId>/bookEdit', methods=['POST'])
def bookEdit(userId):
   id = request.form['objId']

   books = list( db.books.find({'_id': ObjectId(id)} ) )

   for i in books :
      i['_id'] = str(i['_id'])



   return jsonify({'result': books}) 

@app.route('/mypage/<userId>/join', methods=['POST'])
def join(userId):
   id = request.form['objId']

   result = db.rental.update_one( {'_id':ObjectId(id)}, {'$set': {'rental_status':'수락'} } )


   if result.deleted_count == 1:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})    







if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)


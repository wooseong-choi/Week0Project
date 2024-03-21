from pymongo import MongoClient
import jwt
import hashlib
import os

from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify, request, redirect, url_for, session

from bson import ObjectId

from flask.json.provider import JSONProvider

from functools import wraps

import hashlib
import math


from flask import flash


app = Flask(__name__)

app.config['SECRET_KEY'] = 'f1fb0b3154444c53b7aa815e013f7f4f'

#client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.

client = MongoClient('mongodb://test:test@43.202.1.195',27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.week0Project                        # 'jungle'라는 이름의 db를 만듭니다.

@app.route('/')
def home():
   if not session.get('logged_in'):
      return render_template('login.html')
   else:
      return redirect('/books/list')
   
   # db.users.insert_one({'id':'asd','password':'123','name':'asd'})
   # db.books.insert_one({'book_name':'asd','book_comment':'asd','book_image':'asd','user_row_id':'asd'})
   # db.rental.insert_one({'rental_place':'교육관 1층','rental_period':'대여 기간','rental_time':'약속 시간','user_row_id':'test', 'book_row_id':'testbook'})

@app.route('/books/list', methods=['GET'])
def show_books():

   if session['logged_in'] == False : 
      return redirect('/') 

   page = request.args.get('page', 1, type=int)
   limit = 6
   all_books = list(db.book.find({}).sort('_id', -1).skip((page - 1) * limit).limit(limit)  )
   
   tot_count = db.book.count_documents({})
   
   last_page_num = math.ceil(tot_count / limit)
   
   start_page = 1
   end_page = start_page+limit-1

   if end_page > last_page_num: 
      end_page = last_page_num



   return render_template('list.html', all_books=all_books,page=page,limit=limit,last_page_num=last_page_num,tot_count=tot_count,start_page=start_page,end_page=end_page)

@app.route('/books/upload', methods=['GET'])
def goUpload():
   if session['logged_in'] == False : 
      return redirect('/') 
   return render_template('upload.html')

@app.route('/books/upload', methods=['POST'])
def upload():
   title_receive = request.form["title_give"]
   text_receive = request.form["text_give"]
   
   image = request.files["image_give"]
   
   userId = session['user_id']

   # static 폴더에 저장될 파일 이름 생성하기 
   today = datetime.now()
   mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
   filename = f'image-{mytime}'
   # 확장자 나누기
   extension = image.filename.split('.')[-1]
   # static 폴더에 저장
   save_to = os.path.join('static', f'{filename}.{extension}')
   image.save(save_to)
   
   # DB에 저장
   doc = {
         'title': title_receive,
         'text': text_receive,
         'image': f'{filename}.{extension}',
         'user_id':userId
   }
   db.book.insert_one(doc)

   return jsonify({'msg': '업로드 완료!'})

@app.route('/mypage', methods=['GET'])
def mypage():
   
   
   if session['logged_in'] == False : 
      return render_template('mypage.html', error='No session')   
   
   
   userId = session['user_id']

   users = list( db.users.find({'user_id': userId} ) )

   if len(users) > 0 :

      book = list( db.book.find({'user_id': userId} ) )

      rental = []

      for tempBook in book :
         #tempRental = list( db.rental.find( {'book_row_id': str(tempBook['_id']) ,'rental_status':'대여 요청' } ) )
         tempRental = list( db.rental.find( {'book_row_id': str(tempBook['_id'])  } ) )
         rental.append(tempRental)
      

      rental_request = list( db.rental.find( { 'take_user_id': userId } ) )


      return render_template('mypage.html', name=userId, book=book,rental=rental, rental_request=rental_request)
   else  :
      return render_template('mypage.html', error='No user')   

@app.route('/mypage/rental', methods=['POST'])
def mypageRental():
   id = request.form['objId']

   rental = list( db.rental.find({'_id': ObjectId(id)} ) )

   for i in rental :
      i['_id'] = str(i['_id'])


   book = list( db.book.find({'_id':ObjectId(rental[0]['book_row_id'])}) ) 

   for i in book :
      i['_id'] = str(i['_id'])


   return jsonify({'result': book, 'rental':rental})

@app.route('/mypage/bookEdit', methods=['POST'])
def bookEdit():
   id = request.form['objId']

   books = list( db.book.find({'_id': ObjectId(id)} ) )

   for i in books :
      i['_id'] = str(i['_id'])



   return jsonify({'result': books})
  


@app.route('/mypage/join', methods=['POST'])
def join():
   id = request.form['objId']
   result = db.rental.update_one( {'_id':ObjectId(id)}, {'$set': {'rental_status':'수락'} } )
   print(result)
   if result.modified_count > 0:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})    
@app.route('/mypage/reject', methods=['POST'])
def reject():
   id = request.form['objId']
   result = db.rental.update_one( {'_id':ObjectId(id)}, {'$set': {'rental_status':'거절'} } )
   print(result)
   if result.modified_count > 0:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})    



@app.route('/mypage/editBook', methods=['POST'])
def editBook():
   id = request.form['objId']
   title = request.form['title']
   content = request.form['content']
   result = db.book.update_one( {'_id':ObjectId(id)}, {'$set': {'title':title,'text':content} } )
   print(result)
   if result.modified_count > 0:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})    
   
@app.route('/mypage/delBook', methods=['POST'])
def delBook():
   id = request.form['objId']
   result = db.book.delete_one( {'_id':ObjectId(id) } )
   print(result)
   if result.deleted_count > 0:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})   


@app.route( '/mypage/reqBookRental' , methods=['POST'] )
def reqBookRental():
   if session['logged_in'] == False : 
      return render_template('mypage.html', error='No session')   

   bookId = request.form['objId']

   reqUserId = session['user_id']

   book = db.book.find_one({'_id':ObjectId(bookId)})

   rentalData = list(db.rental.find( {'book_row_id':bookId, 'rental_status': { '$in': [ '대여 신청','대여 수락' ] } } ))
   
   # 이미 신청중인 사람이 있을 때
   if len(rentalData) > 0:
      return jsonify({'result':'already'})
   

   rental = {
            'rental_place': request.form['rental_place'],
            'rental_period': request.form['rental_period'],
            'rental_time': request.form['rental_time'],
            'book_row_id': bookId,
            'book_name': book['title'],
            'take_user_id': reqUserId,
            'user_id': book['user_id'],
            'book_image': book['image'],
            'rental_status': '대여 신청',
            'notification':True
         }

   try:
      db.rental.insert_one(rental)
      return jsonify({'result': 'success'})
   except:
      return jsonify({'result': 'failure'})    


@app.route('/mypage/updateNotification', methods=['POST'])
def updateNotification():
   rentalId = request.form['objId']
   db.rental.update_one({'_id':ObjectId(rentalId)}, {'$set': {'notification':False} } )
   return jsonify({'result': 'success'})

#'Logged' #session.clear()
#로그아웃
#@app.route('/', methods=['POST'])
@app.route('/logout', methods=['POST'])
def logout():
   session['logged_in'] = False
   session.pop('user_id',None)
   return render_template('login.html') 


@app.route('/register', methods=['POST'])
def register():
   return render_template('register.html') 


@app.route('/login', methods=['POST'])
def login():
   username_receive = request.form['user_id']
   password_receive = request.form['password']  # 유저가 아이디 pw 입력

   pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()  # 유저가 입력한 pw를 해쉬화
   result = db.users.find_one({'user_id': username_receive, 'password': pw_hash}) 
    # 아이디와 유저가 입력한 해쉬화된 pw가 DB에 저장되어 있는 해쉬화된 pw와 일치하는지 확인 

   id_mac = db.users.find_one({'user_id': username_receive})

   #  if (username_receive == id_mac):
   #     return None

   #  if username_receive == "":
   #     return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
   #  if password_receive == "":
   #     return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

   if result is not None:  # 일치한다면
      session['logged_in'] = True
      session['user_id'] = username_receive
      # token = jwt.encode({
      #       'user': request.form['user_id'],
      #       'expiration': str(datetime.utcnow() + timedelta(seconds=10))}, app.config['SECRET_KEY'])
      return jsonify({'result':'success'})    
   else:
      return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']

    id_mac = db.users.find_one({'user_id': username_receive})

    if id_mac is not None:  # 사용자가 이미 존재하는 경우
        return jsonify({'result': 'false'})
    else:                   # 사용자가 존재하지 않는 경우
        password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest() # password 해쉬화 함수
        doc = {
            "user_id": username_receive,  # 아이디
            "password": password_hash,  # 비밀번호
            "name": nickname_receive,  # 닉네임
        }
        db.users.insert_one(doc) # 유저가 입력한 아이디 pw 닉네임을 DB에 저장    
        return jsonify({'result': 'success','msg':id_mac})


@app.route('/check_duplicate_username', methods=['POST'])
def check_duplicate_username():
    username = request.form['username']
    existing_user = db.users.find_one({'user_id': username})
    return jsonify({'exists': existing_user is not None})


if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)


from pymongo import MongoClient
import jwt
import hashlib

from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify, request, redirect, url_for, session

from bson import ObjectId

from flask.json.provider import JSONProvider

from functools import wraps

import hashlib

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.books                        # 'jungle'라는 이름의 db를 만듭니다.

@app.route('/')
def home():
   if not session.get('logged_in'):
      return render_template('login.html')
   else:
      return render_template('index.html')
   #db.users.insert_one({'id':'ghkdgo868','password':'dddd','name':'최우성'})
   #db.books.insert_one({'book_name':'신비한 동물사전','book_comment':'이 책은 대단합니다.','book_image':'test.jpg','user_row_id':'test'})
   #db.rental.insert_one({'rental_place':'교육관 1층','rental_period':'대여 기간','rental_time':'약속 시간','user_row_id':'test', 'book_row_id':'testbook'})

@app.route('/books/list', methods=['GET'])
def show_books():
    all_books = list(db.book.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'all_books': all_books})

@app.route('/books/upload', methods=['GET'])
def goUpload():
   return render_template('upload.html')

@app.route('/books/upload', methods=['POST'])
def upload():
    title_receive = request.form["title_give"]
    text_receive = request.form["text_give"]
    image = request.files["image_give"]
    # static 폴더에 저장될 파일 이름 생성하기 
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'image-{mytime}'
    # 확장자 나누기
    extension = image.filename.split('.')[-1]
    # static 폴더에 저장
    save_to = f'static/{filename}.{extension}'
    image.save(save_to)

    # DB에 저장
    doc = {
        'title': title_receive,
        'text': text_receive,
        'image': f'{filename}.{extension}'
    }
    db.book.insert_one(doc)

    return jsonify({'msg': '업로드 완료!'})

@app.route('/mypage/<userId>', methods=['GET'])
def mypage(userId):
   print(userId)

   users = list( db.users.find({'user_id': userId} ) )

   if len(users) > 0 :

      book = list( db.books.find({'user_id': userId} ) )

      rental = []

      for tempBook in book :
         #tempRental = list( db.rental.find( {'book_row_id': str(tempBook['_id']) ,'rental_status':'대여 요청' } ) )
         tempRental = list( db.rental.find( {'book_row_id': str(tempBook['_id'])  } ) )
         rental.append(tempRental)
      

      #print('rental : ' , rental)
      #print('book : ' , book)

      return render_template('mypage.html', name=userId, book=book,rental=rental)
   else  :
      return render_template('mypage.html', error='No user')   

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
   print(result)
   if result.modified_count > 0:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})    
@app.route('/mypage/<userId>/reject', methods=['POST'])
def reject(userId):
   id = request.form['objId']
   result = db.rental.update_one( {'_id':ObjectId(id)}, {'$set': {'rental_status':'거절'} } )
   print(result)
   if result.modified_count > 0:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'failure'})    


#'Logged' #session.clear()
    

# 토큰이 있는지 확인하고 인증을 처리하는 데코레이터
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error' : 'Token is missing!'}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error' : 'Token is expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error' : 'Invalid Token!'}), 401
        return func(*args, **kwargs)
    return decorated





# 공개 페이지
@app.route('/public')
def public():
    return 'For Public'

# 인증된 페이지
@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome dashboard'

#로그아웃
#@app.route('/', methods=['POST'])
@app.route('/logout', methods=['POST'])
def logout():
    session['logged_in'] = False
    return render_template('login.html') #session.clear(), 


@app.route('/register', methods=['POST'])
def register():
    return render_template('register.html') 


@app.route('/login', methods=['POST'])
def login():
    username_receive = request.form['username']
    password_receive = request.form['password']  # 유저가 아이디 pw 입력

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()  # 유저가 입력한 pw를 해쉬화
    result = db.users.find_one({'username': username_receive, 'password': pw_hash}) 
    # 아이디와 유저가 입력한 해쉬화된 pw가 DB에 저장되어 있는 해쉬화된 pw와 일치하는지 확인 

    if result is not None:  # 일치한다면
        session['logged_in'] = True
        token = jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(seconds=10))}, app.config['SECRET_KEY'])
        return jsonify({'token': token})    
    
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
    

# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest() # password 해쉬화 함수
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc) # 유저가 입력한 아이디 pw 닉네임을 DB에 저장
    return jsonify({'result': 'success'})


if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)


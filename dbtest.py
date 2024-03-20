from bson.objectid import ObjectId
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.week0Project

def home():

   #db.users.insert_one({'user_id':'ghkdgo868','password':'dddd','name':'최우성'})

   #db.books.insert_one({'book_name':'신비한 동물사전','book_comment':'이 책은 대단합니다.','book_image':'test.jpg','user_id':'ghkdgo868' })
   #db.rental.insert_one({'rental_place':'교육관 1층','rental_period':'대여 기간','rental_time':'약속 시간','user_row_id':'test', 'book_row_id':'65f92f7ba31552634ff5638c'})    
   #db.rental.update_one( {'_id':ObjectId('65f969149dff939a81d4cef6')}, {'$set': {'user_row_id':'65f9306e2b8cd2a6b8d19851', 'user_id':'ghkdgo868','take_user_id':'test','book_name':'신비한 동물사전'} } )
   #db.rental.update_one( {'_id':ObjectId('65f969149dff939a81d4cef6')}, {'$set': {'rental_status':'대여 요청'} } )
   #db.book.insert_one({'book_name':'신비한 동물사전','book_comment':'이 책은 대단합니다.','book_image':'test.jpg','user_id':'jjr7181' })
   # db.rental.insert_one({'rental_place':'교육관 1층','rental_period':'대여 기간','rental_time':'약속 시간','user_row_id':'test', 'book_row_id':'65f92f7ba31552634ff5638c'})    
   # db.rental.update_one( {'_id':ObjectId('65f969149dff939a81d4cef6')}, {'$set': {'user_row_id':'65f9306e2b8cd2a6b8d19851', 'user_id':'ghkdgo868','take_user_id':'test','book_name':'신비한 동물사전'} } )

   rentalData = list(db.rental.find({'book_row_id':'65fa7c14ff4a499ed849c9d9', 'rental_status': { '$in': [ '대여 신청','대여 수락' ] } } ))
   print(rentalData)
   print('완료: ')


if __name__ == '__main__':  
    # 기존의 movies 콜렉션을 삭제하기
    #db.users.drop()
    #db.books.drop()
    #db.rental.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
    home()    


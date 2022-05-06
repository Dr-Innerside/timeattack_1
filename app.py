from flask import Flask, render_template,request,jsonify

from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.timeattack_1

import hashlib

import datetime

import jwt

SECRET_KEY = 'goldvedio'

app = Flask(__name__)


@app.route('/')
def home():
    token_receive = request.args.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'email': payload['email']})

        return render_template('board.html', email=user_info['email'])
    except jwt.ExpiredSignatureError:
        return render_template('index.html', msg='로그인 시간이 만료되었습니다.')
    except jwt.exceptions.DecodeError:
        return render_template('index.html', msg='로그인 정보가 존재하지 않습니다.')

# 과제 1. 회원가입, 로그인, 로그아웃

# 회원가입 API
#
# 사용자 요청
#   이메일, 패스워드
#   email_give, pw_give
# API 처리
#   패스워드는 hashlib으로 암호화하여 DB저장
# 응답 데이터
#   성공, 메시지

@app.route('/signup', methods=['POST'])
def make_signup():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    doc = {
        'email': email_receive,
        'pw': pw_hash
    }
    db.users.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '회원가입에 성공하였습니다!'})

# 로그인 API
#
# 사용자 요청
#   유저 아이디 비밀번호
#   email_give pw_give
# API 처리
#   값 조회 후 페이로드에 jwt토큰
# 응답 데이터
#   토큰 보내기

@app.route('/login', methods=['POST'])
def make_login():
    email_receive = request.form['email_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find_one({'email': email_receive, 'pw': pw_hash})
    print(result)

    if result is not None:
        payload = {
            'email': email_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=50)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result':'success', 'token':token})
    else:
        return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 다릅니다'})


# 유저 정보 확인 API
#
# 사용자 요청
#   토큰 token_give
# API 처리
#   토큰을 디코딩하고 프린트
#   페이로드의 이메일이 일치하는지 DB에서 조회
#   있다면 로그인 트루
#   없거나, 만료되면 거짓
# 응답 데이터
#   성공 상태와 참거짓, 메시지

@app.route('/valid', methods=['GET'])
def valid_login():
    token_receive = request.args.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # if db.users.find_one({'email':payload['email']},{'_id':0}) is not None:
        return jsonify({'result': 'success'})
    except jwt.ExpiredSignatureError:
        return  jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다'})
    except jwt.exceptions.DecodeError:
        return  jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다'})




# 과제 2.로그인 게시판 등록
# 과제 3. 페이지네이션


if __name__ == '__main__':

    app.run('0.0.0.0', port=5000, debug=True)



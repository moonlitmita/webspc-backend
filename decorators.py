#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from flask import request,jsonify
import jwt
from utils import MyJwt
from functools import wraps

def verify_token(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        auth = request.headers.get('Authorization')
        if auth and auth.startswith('Bearer'):
            mj = MyJwt()
            token = auth[7:].strip('"')
            try:
                payload = mj.decode(token)          # 这里如果抛异常会被 except 捕获
            except jwt.ExpiredSignatureError as e:
                return jsonify(code=401, msg='令牌已过期'), 401
            except jwt.InvalidTokenError as e:
                return jsonify(code=401, msg='无效令牌'), 401
            except Exception as e:
                return jsonify(code=500, msg='服务器错误'), 500
            userid = payload['data']['id'] if 'data' in payload else None
            if userid:
               kwargs['userid'] = userid if userid else None
               return func(*args, **kwargs)
            else:
               return jsonify({'code': 401, 'data': {'message': '无效令牌! Invalid token!'}})
        else:
            return jsonify({'code': 401, 'data': {'message':  '令牌消失或格式错误,请重新登录!Token not Found or invalid format,please login again'}})
    return wrapper
            

            
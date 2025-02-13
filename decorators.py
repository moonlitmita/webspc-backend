#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from flask import request,jsonify
from utils import MyJwt
from functools import wraps

def verify_token(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer'):
           mj = MyJwt()
           decoded_token = mj.decode(token[7:].strip('"'))
           userid = decoded_token['data']['id'] if 'data' in decoded_token else None
           if userid:
              kwargs['userid'] = userid if userid else None
              return func(*args, **kwargs)
           else:
              return jsonify({'code': 401, 'data': {'message': '无效令牌! Invalid token!'}})
        else:
            return jsonify({'code': 401, 'data': {'message':  '令牌消失或格式错误,请重新登录!Token not Found or invalid format,please login again'}})
    return wrapper
            

            
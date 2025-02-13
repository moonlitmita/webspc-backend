#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import jwt 
import datetime
from flask import jsonify

class MyJwt:
    def __init__(self,secret='1234'):
        self.secret = secret
    def encode_time(self,userinfo,lifetime=24):
        payload = {
            'exp':(datetime.datetime.now()+datetime.timedelta(hours=lifetime)).timestamp(),
            'data': userinfo
        }
        res = jwt.encode(payload,self.secret,algorithm='HS256')
        return res
    def encode(self,userinfo):
        res = jwt.encode(userinfo,self.secret,algorithm='HS256')
        return res
    def decode(self,jwt_str):
        try:
            res = jwt.decode(jwt_str,self.secret,algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired(utils)'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token(utils)'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        return res
  
   
    
#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import jwt 
import os
import datetime
from flask import jsonify

jwt_secret = os.getenv('JWT_SECRET', 'webspc_123')

class MyJwt:
    def __init__(self,secret=jwt_secret):
        self.secret = secret
    def encode_time(self,userinfo,lifetime=720):
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'exp':now + datetime.timedelta(minutes=lifetime),
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
  
   
    
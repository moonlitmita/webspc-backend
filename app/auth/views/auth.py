#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app.models.local_models import Department
from utils import MyJwt
from flask.views import MethodView
from decorators import verify_token
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/backend/auth')
class GetMenu(MethodView):
    __menu_all = [
        {
            'path': '/home',
            'name': 'home',
            'label': '首页',
            'icon': 'House',
            'url': 'home/Home',
        },
        {
            'path': '/user',
            'name': 'user',
            'label': '用户管理',
            'icon': 'User',
            'url': 'user/User'
        },
        {
            'path': '/department',
            'name': 'department',
            'label': '部门管理',
            'icon': 'OfficeBuilding',
            'url': 'department/Department'
        },
        {
            'path': '/process',
            'name': 'process',
            'label': '制程管理',
            'icon': 'Operation',
            'url': 'process/Process'
        },
        {
            'path': '/project',
            'name': 'project',
            'label': '项目管理',
            'icon': 'Histogram',
            'url': 'project/Project'
        },
        {
            'path': '/tasks',
            'name': 'tasks',
            'label': '动态任务管理',
            'icon': 'Clock',
            'url': 'tasks/TaskManagement'
        },
        {
            'path': '/llm',
            'name': 'llm',
            'label': 'LLM管理',
            'icon': 'Cpu',
            'url': 'llm/ModelSelector'
        },
        {
            'path': '/mcp',
            'name': 'mcp',
            'label': 'MCP_Config',
            'icon': 'Tools',
            'url': 'mcp/MCPConfig'
        }
        ]
    __menu_part = [
        {
            'path': '/home',
            'name': 'home',
            'label': '首页',
            'icon': 'House',
            'url': 'home/Home'
        },
        {
            'path': '/process',
            'name': 'process',
            'label': '制程管理',
            'icon': 'Operation',
            'url': 'process/Process'
        },
        {
            'path': '/project',
            'name': 'project',
            'label': '项目管理',
            'icon': 'Histogram',
            'url': 'project/Project'
        },
        {
            'path': '/tasks',
            'name': 'tasks',
            'label': '动态任务管理',
            'icon': 'Clock',
            'url': 'tasks/TaskManagement'
        },
        {
            'path': '/llm',
            'name': 'llm',
            'label': 'LLM管理',
            'icon': 'Cpu',
            'url': 'llm/ModelSelector'
        },
        {
            'path': '/mcp',
            'name': 'mcp',
            'label': 'MCP_Config',
            'icon': 'Tools',
            'url': 'mcp/MCPConfig'
        }
        ]
    @verify_token
    def get(self, userid):
        dbsession = request._db_session
        user=dbsession.query(User).get(userid)
        res_all = {
            'code': 200,
            'data': {
                'menu': GetMenu.__menu_all,
                'message': '刷新获取成功'
            }
        }
        res_part = {
            'code': 200,
            'data': {
                'menu': GetMenu.__menu_part,
                'message': '刷新获取成功'
            }
        }
        if user:
            if user.is_super_user:
                return jsonify(res_all)
            else:
                return jsonify(res_part)
    def post(self):
        dbsession = request._db_session
        username = request.json.get('username')
        password_origin = request.json.get('password')
        user = dbsession.query(User).filter_by(username=username).first()
        user_dict = user.to_dict() if user else None
        password_hash = user_dict['password']
        mj=MyJwt()
        jwt_str = mj.encode_time({"id":user_dict["id"]})
        data_all = {
            'code': 200,
            'data':{
                "menu": GetMenu.__menu_all,
                "token": jwt_str,
                "message": '全部菜单获取成功'
            }
            }
        data_part = {
            'code': 200,
            'data': {
                "menu": GetMenu.__menu_part,
                "token": jwt_str,
                "message": '部分菜单获取成功'
            }
        }
        if user and check_password_hash(password_hash,password_origin):
            user.last_login = datetime.now()
            if datetime.now() - user.last_login > timedelta(days=30):
                user.is_active = False
            dbsession.commit()
            if user_dict["is_super_user"]=="True":
                return jsonify(data_all)
            else:
                return jsonify(data_part)
        else:
            return jsonify({"code":403,'data':{"message":"用户名或密码错误!Incorrect username or password!"}})
bp.add_url_rule("/getMenu",view_func=GetMenu.as_view("get_menu"))
class UserView(MethodView):
    @verify_token
    def get(self, userid):
        dbsession = request._db_session
        searchInfo = request.args.get('searchInfo', None)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 5, type=int)
        offset = (page-1)*page_size
        if searchInfo:
            results = dbsession.query(User).outerjoin(Department).filter(or_(
                Department.department.ilike('%{}%'.format(searchInfo)),
                User.username.ilike('%{}%'.format(searchInfo))
            ))
            users_pagination = results.order_by(User.id).slice(offset, offset + page_size)
            total_count = results.count()
        else:
            users_pagination = dbsession.query(User).order_by(User.id).slice(offset, offset + page_size).all()
            total_count = dbsession.query(User).count()
        user_dicts = [user.to_dict() for user in users_pagination]
        users_data = {
            'code': 200,
            'data': {
                "list": user_dicts,
                "total": total_count,
                "message": '获取成功'
            }
        }
        return jsonify(users_data)
    @verify_token
    def post(self, userid):
        dbsession = request._db_session
        realname = request.json.get('realname', None)
        gender = request.json.get('gender',None)
        username = request.json.get('username',None)
        dep = request.json.get('dep', None)
        department = dbsession.query(Department).filter_by(department = dep).first()
        password = request.json.get('password',None)
        #以下为测试用代码
        # realname = request.form.get('realname', None)
        # print('realname', realname)
        # gender = request.form.get('gender', None)
        # username = request.form.get('username', None)
        # department_id = request.form.get('department_id', None)
        # password = request.form.get('password', None)
        # user_map = {"1": True, "0": False}
        # is_super_user = user_map.get(request.form.get('is_super_user', None))
        # is_staff = user_map.get(request.form.get('is_staff', None))
        # is_active = user_map.get(request.form.get('is_active', None))

        # user = User(realname=realname,gender=gender,username=username,department_id=department_id,
        #             password=generate_password_hash(password),is_super_user=is_super_user,
        #             is_staff=is_staff,is_active=is_active)
        
        user_map = {"1": True, "0": False}
        is_super_user = user_map.get(request.json.get('is_super_user',None))
        is_staff = user_map.get(request.json.get('is_staff',None))
        is_active = user_map.get(request.json.get('is_active',None))
        user = User(realname=realname,gender=gender,username=username,department_id=department.id,
                    password=generate_password_hash(password),is_super_user=is_super_user,
                    is_staff=is_staff,is_active=is_active)
        dbsession.add(user)
        dbsession.commit()
        add_info = {
            'code': 200,
            'data': {"message": "用户添加成功! User added successfully!"}
        }
        return jsonify(add_info)
    @verify_token
    def delete(self,userid):
        dbsession = request._db_session
        user_id = request.json.get('id',None)
        user = dbsession.query(User).get(user_id)
        if user is None:
            return jsonify({"errcode":1,"msg":"User is not exsist"})
        else:
            dbsession.delete(user)
            dbsession.commit()
            delete_info = {
                    'code': 200,
                    'data': {'message': 'User delete successfully'}
            }
            return jsonify(delete_info)
    @verify_token
    def put(self, userid):
        dbsession = request._db_session
        user_map = {'1': True, '是': True, '0': False, '否': False}
        _id = request.json.get('id',None)
        realname = request.json.get('realname',None)
        gender = request.json.get('gender',None)
        username = request.json.get('username',None)
        dep = request.json.get('dep', None)
        is_super_user = request.json.get('is_super_user',None)
        is_staff = request.json.get('is_staff', None)
        is_active = request.json.get('is_active',None)
        user = dbsession.query(User).get(_id)
        if user is None:
            return jsonify({"code":404,'data':{"message":"用户不存在! User not exist!"}})
        else:
            user.realname = realname
            user.gender = gender
            user.username = username
            user.dep = dep
            user.is_super_user = user_map.get(is_super_user)
            user.is_staff = user_map.get(is_staff)
            user.is_active = user_map.get(is_active)
            dbsession.commit()
            upd_info = {
                'code': 200,
                'data': {'message': '用户修改成功！ User edit successfully!'}
            }
            return jsonify(upd_info)
bp.add_url_rule("/user",view_func=UserView.as_view("user_view"))  
    



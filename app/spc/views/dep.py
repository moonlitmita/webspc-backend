#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy import or_, select
from decorators import verify_token
from app.models import User, Department, Process, Project, Data
import pandas as pd
import numpy as np
from mystat import f_oneway_variance, normality_test

bp = Blueprint('spc', __name__, url_prefix='/backend/spc')
class DepView(MethodView):
    @verify_token
    def get(self, userid):
        dbsession = request._db_session
        user = dbsession.query(User).get(userid)
        getAll = request.args.get('getAll', None)
        searchInfo = request.args.get('dep', None)
        page = request.args.get('page', 1 ,type=int)
        page_size = request.args.get('pageSize', 1, type=int)
        offset = (page-1)*page_size
        if user.is_super_user:
            deps_all = dbsession.query(Department).order_by(Department.id).all()
        else:
            deps_all = dbsession.query(Department).filter(Department.id == user.department_id)
        dicts_all = [dep.to_dict() for dep in deps_all]
        if searchInfo:
            results = dbsession.query(Department).filter(Department.department.ilike('%{}%'.format(searchInfo)))
            deps_pagination = results.order_by(Department.id).slice(offset, offset + page_size)
            dicts_pagination = [dep.to_dict() for dep in deps_pagination]
            total_count = results.count()
        else:
            deps_pagination = dbsession.query(Department).order_by(Department.id).slice(offset, offset + page_size)
            dicts_pagination = [dep.to_dict() for dep in deps_pagination]
            total_count = dbsession.query(Department).count()
        data_pagination = {
            'code': 200,
            'data': {
                'list': dicts_pagination,
                'total': total_count,
                'message': '分页数据获取成功！'
            }
        }
        data_all = {
            'code': 200,
            'data': {
                'all': dicts_all,
                'message': '全部数据获取成功！'
            }
        }
        if getAll == 'false':
            return jsonify(data_pagination)
        else:
            return jsonify(data_all)
    @verify_token
    def post(self, userid):
        dbsession = request._db_session
        dep = request.json.get('dep', None)
        #以下为测试用代码
        # dep = request.form.get('department', None)
        department = Department(department=dep)
        dbsession.add(department)
        dbsession.commit()
        add_info = {
            'code': 200,
            'data': {
            'message': '部门添加成功! Department added successfully!'
            }
        }
        return jsonify(add_info)
    @verify_token
    def put(self, userid):
        dbsession = request._db_session
        _id = request.json.get('id', None)
        dep = request.json.get('dep', None)
        department = dbsession.query(Department).get(_id)
        if department is None:
            return jsonify({'code': 404, 'data': {'message': '部门不存在! Department not exist!'}})
        else:
            department.department = dep
            dbsession.commit()
            upd_info = {
                'code': 200,
                'data': {'message': '部门修改成功! Department edit successfully!'}
            }
            return jsonify(upd_info)
    @verify_token
    def delete(self, userid):
        dbsession = request._db_session
        _id = request.json.get('id', None)
        department = dbsession.query(Department).get(_id)
        if department is None:
            return jsonify({'code': 404, 'data': {'message': '部门不存在! Department not exist!' }})
        else:
            dbsession.delete(department)
            dbsession.commit()
            delete_info = {
                'code': 200,
                'data': {
                    'message': '部门删除成功! Department delete sucessfully!'
                }
            }
            return jsonify(delete_info)
bp.add_url_rule("/dep", view_func=DepView.as_view("dep_view"))
class ProcessView(MethodView):
    @verify_token
    def get(self, userid):
        dbsession = request._db_session
        user = dbsession.query(User).get(userid)
        department = dbsession.query(Department).filter_by(id=user.department_id).first()
        getAll = request.args.get('getAll', None)
        searchInfo = request.args.get('searchInfo', None)
        page = request.args.get('page', 1 ,type=int)
        page_size = request.args.get('pageSize', 1, type=int)
        offset = (page-1)*page_size
        if searchInfo:
            if user.is_super_user:
                results = dbsession.query(Process).outerjoin(Department).filter(or_(
                    Department.department.ilike('%{}%'.format(searchInfo)),
                    Process.process.ilike('%{}%'.format(searchInfo))
                ))
                processes_pagination = results.order_by(Process.id).slice(offset, offset + page_size)
                total_count = results.count()
                processes_all = dbsession.query(Process).order_by(Process.id).all()
            else:
                results = dbsession.query(Process).outerjoin(Department).filter(or_(
                    Department.department.ilike('%{}%'.format(searchInfo)),
                    Process.process.ilike('%{}%'.format(searchInfo))
                )).filter(Department.id==department.id)
                processes_pagination = results.order_by(Process.id).slice(offset, offset + page_size)
                total_count = results.count()
                processes_all = dbsession.query(Process).filter(Department.id==department.id)
        else:
            if user.is_super_user:
                processes_pagination = dbsession.query(Process).order_by(Process.id).slice(offset, offset + page_size)
                total_count = dbsession.query(Process).count()
                processes_all = dbsession.query(Process).order_by(Process.id).all()
            else:
                processes_results = dbsession.query(Process).filter_by(department_id=department.id)
                processes_pagination = processes_results.order_by(Process.id).slice(offset, offset + page_size)
                total_count = processes_results.count()
                processes_all = dbsession.query(Process).filter(Department.id==department.id)
        dicts_pagination = [process.to_dict() for process in processes_pagination]
        dicts_all = [process.to_dict() for process in processes_all]
        data_pagination = {
            'code': 200,
            'data': {
                'list': dicts_pagination,
                'total': total_count,
                'message': '分页数据获取成功！'
            }
        }
        data_all = {
            'code': 200,
            'data': {
                'all': dicts_all,
                'message': '全部数据获取成功！'
            }
        }
        if getAll == 'false':
            return jsonify(data_pagination)
        else:
            return jsonify(data_all)
    @verify_token
    def post(self, userid):
        dbsession = request._db_session
        process = request.json.get('process', None)
        dep = request.json.get('dep')
        department = dbsession.query(Department).filter_by(department=dep).first()
        process = Process(process=process, department_id=department.id)
        dbsession.add(process)
        dbsession.commit()
        add_info = {
            'code': 200,
            'data': {
                'message': '制程添加成功! Process added successfully!'
            }
        }
        return jsonify(add_info)
    @verify_token
    def put(self, userid):
        dbsession = request._db_session
        process_id = request.json.get('id', None)
        dep = request.json.get('dep',None)
        department = dbsession.query(Department).filter_by(department=dep).first()
        get_process = request.json.get('process', None)
        process = dbsession.query(Process).get(process_id)
        if process is None:
            return jsonify({'code': 404, 'data': {'message': '该制程不存在！ Process not existc!'}})
        else:
            process.department_id = department.id
            process.process = get_process
            dbsession.commit()
            upd_info = {
                'code': 200,
                'data': {
                    'message': '制程修改成功! Process edit successfully!'
                }
            }
            return jsonify(upd_info)
    @verify_token
    def delete(self, userid):
        dbsession = request._db_session
        process_id = request.json.get('id', None)
        process = dbsession.query(Process).get(process_id)
        if process is None:
            return jsonify({'code': 404, 'data': {'message': '该制程不存在! This process not exist!'}})
        else:
            dbsession.delete(process)
            dbsession.commit()
            delete_info = {
                'code': 200,
                'data': {
                    'message': '制程删除成功! Process delete successfully!'
                }
            }
            return jsonify(delete_info)
bp.add_url_rule("/process", view_func=ProcessView.as_view("process_view"))
class ProjectView(MethodView):
    @verify_token
    def get(self, userid):
        dbsession = request._db_session
        user = dbsession.query(User).get(userid)
        searchInfo = request.args.get('searchInfo', None)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 1, type=int)
        offset = (page-1)*page_size
        if searchInfo:
            results = dbsession.query(Project).outerjoin(Process).outerjoin(Department).filter(or_(
                    Process.process.ilike('%{}%'.format(searchInfo)),
                    Project.project.ilike('%{}%'.format(searchInfo)),
                    Department.department.ilike('%{}%'.format(searchInfo))
                ))
            if user.is_super_user:
                projects_pagination = results.order_by(Project.id).slice(offset, offset + page_size)
                total_count = results.count()
            else:
                projects_filtered = results.filter(Department.id==user.department_id)
                total_count = projects_filtered.count()
        else:
            if user.is_super_user:
                results = dbsession.query(Project).order_by(Project.id)
                projects_pagination = results.slice(offset, offset + page_size)
                total_count = results.count()
            else:
                results = dbsession.query(Project).join(Process).filter(Process.department_id == user.department_id)
                projects_pagination = results.slice(offset, offset + page_size)
                total_count = results.count()
        dicts_pagination = [project.to_dict() for project in projects_pagination]
        project_data = {
            'code': 200,
            'data': {
                'list' : dicts_pagination,
                'total': total_count,
                'message': '项目数据获取成功！'
            }
        }
        return jsonify(project_data)
    @verify_token
    def post(self, userid):
        dbsession = request._db_session
        product = request.json.get('product', None)
        project = request.json.get('project', None)
        spcType1 = request.json.get('spcType1', None)
        spcType2 = request.json.get('spcType2', None)
        spcType3 = request.json.get('spcType3', None)
        sampleSize = request.json.get('sampleSize', None)
        USL = request.json.get('USL', None)
        LSL = request.json.get('LSL', None)
        selectedChecks = request.json.get('selectedChecks', None)
        selectedChecks_str = ",".join(value for value in selectedChecks)
        dataCollectionType = request.json.get('dataCollectionType', None)
        get_process = request.json.get('process')
        process = dbsession.query(Process).filter_by(process=get_process).first()
        project = Project(product=product, project=project, spcType1=spcType1, spcType2=spcType2, spcType3=spcType3,
                          sampleSize=sampleSize, USL=USL, LSL=LSL, selectedChecks=selectedChecks_str, 
                          dataCollectionType=dataCollectionType, process_id=process.id)
        dbsession.add(project)
        dbsession.commit()
        add_info = {
            'code': 200,
            'data': {
                'message': '项目添加成功! Project added successfully!'
            }
        }
        return jsonify(add_info)
    @verify_token
    def put(self, userid):
        dbsession = request._db_session
        project_id = request.json.get('id', None)
        product = request.json.get('product', None)
        get_project = request.json.get('project', None)
        spcType1 = request.json.get('spcType1', None)
        spcType2 = request.json.get('spcType2', None)
        spcType3 = request.json.get('spcType3', None)
        sampleSize = request.json.get('sampleSize', None)
        USL = request.json.get('USL', None)
        LSL = request.json.get('LSL', None)
        selectedChecks = request.json.get('selectedChecks', None)
        selectedChecks_str = ",".join(value for value in selectedChecks)
        get_process = request.json.get('process', None)
        process = dbsession.query(Process).filter_by(process=get_process).first()
        project = dbsession.query(Project).get(project_id)
        if project is None:
            return jsonify({'code': 404, 'data': {'message': '该项目不存在! Project not exsit!'}})
        else:
            project.process_id = process.id
            project.product = product
            project.project = get_project
            project.spcType1 = spcType1
            project.spcType2 = spcType2
            project.spcType3 = spcType3
            project.sampleSize = sampleSize
            project.USL = USL
            project.LSL = LSL
            project.selectedChecks = selectedChecks_str
            dbsession.commit()
            upd_info = {
                'code': 200,
                'data': {
                    'message': '项目修改成功! Project edit successfully!'
                }
            }
            return jsonify(upd_info)
    @verify_token
    def delete(self, userid):
        dbsession = request._db_session
        project_id = request.json.get('id', None)
        project = dbsession.query(Project).get(project_id)
        if project is None:
            return jsonify({'code': 404, 'data': {'message': '该项目不存在! Project not exsist!'}})
        else:
            dbsession.delete(project)
            dbsession.commit()
            delete_info = {
                'code': 200,
                'data': {
                    'message': '项目删除成功! Project delete successfully!'
                }
            }
            return jsonify(delete_info)
bp.add_url_rule("/project", view_func=ProjectView.as_view("project_view"))
class HomeView(MethodView):
    @verify_token
    def get(self, userid):
        dbsession = request._db_session
        project_id = request.args.get('project_id', None)
        getAll = request.args.get('getAll', None)
        start_date_str = request.args.get('startDate', None)
        end_date_str = request.args.get('endDate', None)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 1, type=int)
        offset = (page-1)*page_size
        project = dbsession.query(Project).get(project_id)
        if not project:
            return jsonify({
                'code': 400,
                'data': {
                    'message': '项目信息丢失，请重新登陆项目管理页面选择项目！'
                }
            })
        else:
            start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
            end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
            # 0. 最多一个日期条件
            date_condition = None
            if start_date and end_date:
                date_condition = Data.add_date.between(start_date, end_date)
            elif start_date:
                date_condition = Data.add_date >= start_date
            elif end_date:
                date_condition = Data.add_date <= end_date

            # 1. data_all 子查询
            sub_base = (select(Data.id)
                        .where(Data.project_id == project_id)
                        .order_by(Data.id.desc())
                        .limit(1000))
            if date_condition is not None:
                sub_base = sub_base.where(date_condition)

            sub = sub_base.subquery()
            stmt_all = (select(Data)
                        .join(sub, Data.id == sub.c.id)
                        .order_by(Data.id.asc()))
            data_all = dbsession.execute(stmt_all).scalars().all()

            # 2. data_pagination base_query
            base_query = dbsession.query(Data).filter_by(project_id=project_id)
            if date_condition is not None:
                base_query = base_query.filter(date_condition)

            total_count = base_query.count()
            data_pagination = (base_query.order_by(Data.id)
                            .offset(offset)
                            .limit(page_size)
                            .all())
            dicts_pagination = [data.to_dict() for data in data_pagination]
            dicts_all = [data.to_dict() for data in data_all]
            dicts_all_averages = [np.mean(d['samples']) for d in dicts_all]
            normality_test_result = normality_test(dicts_all_averages)
            variance_component = f_oneway_variance(dicts_all, project.sampleSize)
            details_all = {
                'code': 200,
                'data': {
                    'all': dicts_all,
                    'test_name': normality_test_result['test_name'],
                    'p_value': normality_test_result['p_value'],
                    'variance_within': variance_component['组内方差分量'],
                    'variance_between': variance_component['组间方差分量'],
                    'message': '全部数据获取成功！'
                }
            }
            details_pagination = {
                'code': 200,
                'data': {
                    'list': dicts_pagination,
                    'total': total_count,
                    'message': '分页数据获取成功!'
                }
            }
            if getAll=='true':
                return jsonify(details_all)
            else:
                return jsonify(details_pagination)
    @verify_token
    def post(self, userid):
        dbsession = request._db_session
        content_type = request.headers.get('Content-Type').strip()
        if content_type and content_type.startswith('multipart/form-data'):
            data_type = request.form.get('dataType', None)
            if 'dataType' in request.form and data_type == 'batch':
                if 'file' in request.files:
                    try:
                        file = request.files['file']
                        project_id = request.form.get('project_id', None)
                        sample_size = int(request.form.get('sample_size', None))
                        df = pd.read_excel(file, sheet_name=0)
                        for index, row in df.iterrows():
                            samples_list = []
                            for i in range(1, sample_size + 1):
                                column_name = f'n{i}'
                                if column_name in df.columns:
                                    samples_list.append(str(row[column_name]))
                            samples_str = ",".join(samples_list)
                            new_item = Data(project_id = project_id, samples = samples_str)
                            dbsession.add(new_item)
                        dbsession.commit()
                        return jsonify({
                            'code': 200,
                            'data': {
                                'message': 'File uploaded and processed successfully! 文件上传并且处理成功！'
                            }
                        })
                    except Exception as e:
                        return jsonify({
                            'code': 500,
                            'data': {
                                'error': str(e)
                            }
                        })
                else:
                    return jsonify({
                        'code': 400,
                        'data': {
                            'error': 'No file part in the request! 请求中无文件！'
                        }
                    })
        elif content_type == 'application/json':
            try:
                data = request.json
                data_type = data.get('dataType', None)
                if data_type == 'single':
                    project_id = data.get('project_id', None)
                    project = dbsession.query(Project).filter_by(id=project_id).first()
                    values = [data.get(f"n{i}") for i in range(1, project.sampleSize + 1)]
                    values_str = ','.join(str(value) for value in values)
                    data = Data(project_id = project_id, samples = values_str)
                    dbsession.add(data)
                    dbsession.commit()
                    add_info = {
                        'code': 200,
                        'data': {
                            'message': 'Data added successfully! 数据添加成功！'
                        }
                    }
                    return jsonify(add_info)
                else:
                    return jsonify({
                        'code': 400,
                        'error': 'Unsupported data type for JSON request! JSON数据中文件类型错误!'
                    })
            except ValueError:
                return jsonify({
                    'code': 400,
                    'data': {
                        'error': 'Invalid JSON data! 无效的JSON数据!'
                    }
                })
        else:
            return jsonify({
                'code': 415,
                'data': {
                    'error': 'Unsupported content type! 无效的内容类型!'
                }
            })
    @verify_token
    def put(self, userid):
        dbsession = request._db_session
        res = request.json
        data_id = res.get('id', None)
        project_id = res.get('project_id', None)
        project = dbsession.query(Project).filter_by(id=project_id).first()
        values = [res.get(f"n{i}") for i in range(1, project.sampleSize + 1)]
        values_str = ','.join(str(value) for value in values)
        data = dbsession.query(Data).get(data_id)
        if data is None:
            return jsonify({'code': 404, 'data': {'message': "该数据不存在! Data not exsist!"}})
        else:
            data.project_id = project_id
            data.samples = values_str
            dbsession.commit()
            upd_info = {
                'code': 200,
                'data': {
                    'message': '数据修改成功! Data edit successfully!'
                }
            }
            return jsonify(upd_info)
    @verify_token
    def delete(self, userid):
        dbsession = request._db_session
        data_id = request.json.get('id', None)
        data = dbsession.query(Data).get(data_id)
        if data is None:
            return jsonify({'code': 404, 'data': {'message': '该数据不存在! Data not exsist!'}})
        else:
            dbsession.delete(data)
            dbsession.commit()
            delete_info = {
                'code': 200,
                'data': {
                    'message': "数据删除成功! Data delete successfully!"
                }
            }
            return jsonify(delete_info)
bp.add_url_rule("/data", view_func=HomeView.as_view("home_view"))
    





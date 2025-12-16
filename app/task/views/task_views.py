# Copyright 2025-present Yu Wang. All Rights Reserved.
#
# Distributed under MIT license.
# See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from flask import Blueprint, request, jsonify, current_app
import json
from decorators import verify_token
from app.models.local_models import PeriodicTask, User, Process, Project

bp = Blueprint('task_manager', __name__)

@bp.route('/backend/tasks', methods=['GET'])
@verify_token
def get_tasks(userid):
    """
    获取所有周期性任务
    """
    session = request._db_session
    try:
        user = session.query(User).get(userid)
        searchInfo = request.args.get('searchInfo', None)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 1, type=int)
        offset = (page-1)*page_size
        if searchInfo:
            results = session.query(PeriodicTask).filter(
                PeriodicTask.name.ilike('%{}%'.format(searchInfo))
                )
            if user.is_super_user:
                periodicTasks_pagination = results.order_by(PeriodicTask.id).slice(offset, offset + page_size)
                total_count = results.count()
            else:
                periodicTasks_filtered = results.join(Project).filter(
                    Project.process_id == Process.id,
                    Process.department_id == user.department_id)
                total_count = periodicTasks_filtered.count()
        else:
            if user.is_super_user:
                results = session.query(PeriodicTask).order_by(PeriodicTask.id)
                periodicTasks_pagination = results.slice(offset, offset + page_size)
                total_count = results.count()
            else:
                results = session.query(PeriodicTask).join(Project).filter(
                    Project.process_id == Process.id,
                    Process.department_id == user.department_id)
                periodicTasks_pagination = results.slice(offset, offset + page_size)
                total_count = results.count()
        dicts_pagination = [task.to_dict() for task in periodicTasks_pagination]
        periodicTasks_data = {
            'code': 200,
            'data': {
                'task_list' : dicts_pagination,
                'total': total_count,
                'message': '任务列表获取成功！'
            }
        }
        return jsonify(periodicTasks_data)
    except Exception as e:
        session.rollback()
        return jsonify({
            'code': 500,
            'data': {
                'message': str(e)
            }
        }), 500

@bp.route('/backend/tasks', methods=['POST'])
@verify_token
def add_task(userid):
    """
    添加周期性任务
    """
    session = request._db_session
    try:
        data = request.get_json()
        print(f'data: {data}')

        # 验证必要参数
        required_fields = ['name', 'project_id', 'task', 'schedule_type', 'schedule_value']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'data': {
                        'message': f'缺少必要参数: {field}'
                    }
                }), 400
        
        # 验证项目数据采集类型是否为自动采集
        project = session.query(Project).filter(Project.id == data['project_id']).one_or_none()
        if project is None:
            raise ValueError("项目不存在")
        if project.dataCollectionType != "自动采集":
            raise ValueError("仅允许为'自动采集'项目创建周期任务")
        
        # 检查任务名称是否已存在
        existing_task = session.query(PeriodicTask).filter(PeriodicTask.name == data['name']).first()
        if existing_task:
            return jsonify({
                'code': 400,
                'data': {
                    'message': f'任务名称已存在: {data["name"]}'
                }
            }), 400

        # 创建新任务
        new_task = PeriodicTask(
            name=data['name'],
            project_id=data['project_id'],
            task=data['task'],
            enabled=data.get('enabled', True),
            schedule_type=data['schedule_type'],
            schedule_value=json.dumps(data['schedule_value']),
            args=json.dumps(data.get('args', [])) if data.get('args') else None,
            kwargs=json.dumps(data.get('kwargs', {})) if data.get('kwargs') else None
        )

        # 在提交前将新任务数据转换为字典，避免提交后访问对象导致的session问题
        new_task_data = new_task.to_dict()
        session.add(new_task)
        session.commit()

        # 更新Celery的beat schedule
        celery_app = current_app.extensions["celery"]
        celery_app.update_beat_schedule()

        return jsonify({
            'code': 200,
            'data': {
                'new_task': new_task_data,
                'message': '任务添加成功'
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'code': 500,
            'data': {
                'message': str(e)
            }
        }), 500

@bp.route('/backend/tasks/<int:task_id>', methods=['PUT'])
@verify_token
def update_task(task_id, userid):
    """
    更新周期性任务
    """
    session = request._db_session
    try:
        data = request.get_json()
        task = session.query(PeriodicTask).filter(PeriodicTask.id == task_id).first()

        if not task:
            return jsonify({
                'code': 404,
                'data': {
                    'message': '任务不存在'
                }
            }), 404

        # 更新任务信息
        if 'name' in data:
            task.name = data['name']
        if 'task' in data:
            task.task = data['task']
        if 'enabled' in data:
            task.enabled = data['enabled']
        if 'schedule_type' in data:
            task.schedule_type = data['schedule_type']
        if 'schedule_value' in data:
            task.schedule_value = json.dumps(data['schedule_value'])
        if 'args' in data:
            task.args = json.dumps(data['args']) if data['args'] else None
        if 'kwargs' in data:
            task.kwargs = json.dumps(data['kwargs']) if data['kwargs'] else None

        # 在提交前将任务数据转换为字典，避免提交后访问对象导致的session问题
        updated_task_data = task.to_dict()
        session.commit()

        # 更新Celery的beat schedule
        celery_app = current_app.extensions["celery"]
        celery_app.update_beat_schedule()

        return jsonify({
            'code': 200,
            'data': {
                'update_task': updated_task_data,
                 'message': '任务更新成功'
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'code': 500,
            'data': {
                'message': str(e)
            }
        }), 500


@bp.route('/backend/tasks/<int:task_id>', methods=['DELETE'])
@verify_token
def delete_task(task_id, userid):
    """
    删除周期性任务
    """
    session = request._db_session
    try:
        task = session.query(PeriodicTask).filter(PeriodicTask.id == task_id).first()

        if not task:
            return jsonify({
                'code': 404,
                'data': {
                    'message': '任务不存在'
                }
            }), 404

        session.delete(task)
        session.commit()

        # 更新Celery的beat schedule
        celery_app = current_app.extensions["celery"]
        celery_app.update_beat_schedule()

        return jsonify({
            'code': 200,
            'data': {
                'message': '任务删除成功'
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'code': 500,
            'data': {
                'message': str(e)
            }
        }), 500
   

@bp.route('/backend/tasks/<int:task_id>/toggle', methods=['PUT'])
@verify_token
def toggle_task(task_id, userid):
    """
    启用/禁用周期性任务
    """
    session = request._db_session
    try:
        task = session.query(PeriodicTask).filter(PeriodicTask.id == task_id).first()

        if not task:
            return jsonify({
                'code': 404,
                'data': {
                    'message': '任务不存在'
                }
            }), 404

        # 切换任务状态
        new_status = not task.enabled
        task.enabled = new_status

        # 在提交前保存任务数据，避免提交后访问对象导致的session问题
        toggle_task_data = task.to_dict()
        session.commit()

        # 更新Celery的beat schedule
        celery_app = current_app.extensions["celery"]
        celery_app.update_beat_schedule()

        return jsonify({
            'code': 200,
            'data': {
                'toggle_task': toggle_task_data,
                'message': f'任务已{"启用" if new_status else "禁用"}'
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'code': 500,
            'data': {
                'message': str(e)
            }
        }), 500


@bp.route('/backend/tasks/refresh', methods=['POST'])
@verify_token
def refresh_schedules(userid):
    """强制刷新调度配置"""
    try:
        # 获取Celery实例并调用其更新方法
        celery_app = current_app.extensions["celery"]
        celery_app.update_beat_schedule()
        
        return jsonify({
            'code': 200,
            'data': {
                'message': '任务调度配置已刷新'
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'data': {
                'message': str(e)
            }
        }), 500
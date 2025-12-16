#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os
from celery import Celery
from flask import Flask
from .celeryconfig import task_module
from celery_task import celeryconfig
from datetime import timedelta

def make_celery(app: Flask) -> Celery:
    app_name = app.import_name if app else __name__
    broker_url = os.environ.get('CELERY_BROKER_URL', celeryconfig.BROKER_URL)
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', celeryconfig.RESULT_BACKEND)
    celery_app = Celery(app_name, broker=broker_url, backend=result_backend, include=task_module)

    # 初始配置，不包含静态的beat_schedule
    base_config = {k: v for k, v in celeryconfig.CELERY_CONFIG.items() if k != 'beat_schedule'}
    celery_app.conf.update(**base_config)

    TaskBase = celery_app.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery_app.Task = ContextTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    celery_app.autodiscover_tasks()

    # 添加动态任务更新方法
    def update_beat_schedule():
        """从数据库加载并更新beat schedule"""
        with app.app_context():
            from app.models.local_models import PeriodicTask
            session = app.extensions['sqlalchemy']['local_session']

            # 创建新的调度配置
            new_schedule = {}

            # 添加静态任务（如果有）
            if 'beat_schedule' in celeryconfig.CELERY_CONFIG:
                new_schedule.update(celeryconfig.CELERY_CONFIG['beat_schedule'])

            # 从数据库读取启用的任务
            active_tasks = session.query(PeriodicTask).filter(PeriodicTask.enabled == True).all()

            for task in active_tasks:
                schedule_config = {
                    'task': task.task,
                }

                # 解析调度类型和值
                if task.schedule_type == 'interval':
                    import json
                    interval_data = json.loads(task.schedule_value)
                    # 修正：如果是字典格式，取every字段；如果是数字，直接使用
                    if isinstance(interval_data, dict):
                        every_seconds = interval_data.get('every', 30)
                    else:
                        every_seconds = int(interval_data)
                    schedule_config['schedule'] = timedelta(seconds=every_seconds)
                elif task.schedule_type == 'crontab':
                    import json
                    from celery.schedules import crontab
                    crontab_data = json.loads(task.schedule_value)
                    schedule_config['schedule'] = crontab(
                        minute=crontab_data.get('minute', '*'),
                        hour=crontab_data.get('hour', '*'),
                        day_of_week=crontab_data.get('day_of_week', '*'),
                        day_of_month=crontab_data.get('day_of_month', '*'),
                        month_of_year=crontab_data.get('month_of_year', '*')
                    )

                # 解析任务参数
                if task.args:
                    import json
                    schedule_config['args'] = tuple(json.loads(task.args))

                if task.kwargs:
                    import json
                    schedule_config['kwargs'] = json.loads(task.kwargs)

                new_schedule[task.name] = schedule_config

            # 更新Celery配置
            celery_app.conf.beat_schedule = new_schedule

    # 添加方法到celery_app实例
    celery_app.update_beat_schedule = update_beat_schedule

    return celery_app
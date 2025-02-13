#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os
from celery import Celery
from flask import Flask
from .celeryconfig import task_module
from celery_task import celeryconfig

def make_celery(app: Flask) -> Celery:
    app_name = app.import_name if app else __name__
    broker_url = os.environ.get('CELERY_BROKER_URL', celeryconfig.BROKER_URL)
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', celeryconfig.RESULT_BACKEND)
    celery_app = Celery(app_name, broker=broker_url, backend=result_backend, include=task_module)
    celery_app.conf.update(**celeryconfig.CELERY_CONFIG)
    TaskBase = celery_app.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery_app.Task = ContextTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    celery_app.autodiscover_tasks()
    return celery_app
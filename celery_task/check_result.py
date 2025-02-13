#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from celery.result import AsyncResult

def check_task_result(task_id, celery_app):
    async_result = AsyncResult(task_id, app=celery_app)
    if async_result.ready():
        status = 'SUCCESS'
        result = async_result.get()
    else:
        status = 'PENDING'
        result = None
    return status, result


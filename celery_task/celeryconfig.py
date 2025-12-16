#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os

BROKER_URL = 'redis://127.0.0.1:6379/0'
RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

BROKER_URL = os.environ.get('CELERY_BROKER_URL', BROKER_URL)
RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', RESULT_BACKEND)

task_module = [
    'celery_task.periodic_task'
]
# 从数据库库中加载周期性任务，以下静态任务暂时不需要了
# dict_filters = {'shift': 'a'}
# dict_filters_json = json.dumps(dict_filters)
CELERY_CONFIG = {
    "broker_url": BROKER_URL,
    "result_backend": RESULT_BACKEND,
    "task_serializer": 'json',
    "accept_content": ['json'],
    "timezone": 'Asia/Shanghai',
    "enable_utc": False,
    "result_expires": 1*60*60,
    "broker_connection_retry_on_startup": True,
    # "beat_schedule": {
    # 'fetch-every-nine-seconds': {
    #     'task': 'celery_task.periodic_task.fetch_data_from_third_party',
    #     'schedule': timedelta(seconds=9),
    #     'args': (dict_filters_json, 5, 3),
    #     }
    # }
}
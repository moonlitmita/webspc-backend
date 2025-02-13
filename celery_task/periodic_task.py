#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from datetime import datetime
from celery import shared_task
from flask import current_app
import json
import time
from sqlalchemy import desc
from app.models.external_models import FirstExternalModel
from app.models.local_models import Data

@shared_task(ignore_result=False)
def fetch_data_from_third_party(dict_filters, project_id, sample_size):
    with current_app.app_context():
        filters = json.loads(dict_filters)
        third_party_session1 = current_app.extensions['sqlalchemy']['third_party_session1']
        local_session = current_app.extensions['sqlalchemy']['local_session']
        data_info = local_session.query(Data).order_by(desc(Data.add_date)).first()
        if data_info is None or data_info.add_date is None:
            query_start_time = datetime.now()
        else:
            query_start_time = data_info.add_date
        query = third_party_session1.query(FirstExternalModel)
        for field, value in filters.items():
            query = query.filter(getattr(FirstExternalModel, field) == value)
        res = query.filter(FirstExternalModel.add_date > query_start_time).limit(sample_size).all()
        if len(res) == sample_size:
            dicts_all = [data.to_dict() for data in res]
            data_list = [round(item['resistance'], 2) for item in dicts_all]
            data_str = ', '.join(map(str, data_list))
            new_item = Data(project_id = project_id, samples = data_str)
            local_session.add(new_item)
            local_session.commit()
            data_all = {
                'code': 200,
                'data': {
                    'import_data': dicts_all,
                    'message': 'data get successfully!'
                }
            }
            return data_all
        else:
            return None
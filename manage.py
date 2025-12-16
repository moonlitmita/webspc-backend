#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from RealProject import create_app
from dotenv import load_dotenv

load_dotenv()

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

if __name__ == '__main__':
    # 开发状态
    # flask_app.run(port=5000, debug=True)
    # 生产状态
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

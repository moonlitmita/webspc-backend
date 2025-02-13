#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from RealProject import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

if __name__ == '__main__':
    # flask_app.run(port=5000, debug=True)
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import os
from flask import Flask, jsonify, request
from sqlalchemy import QueuePool, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from RealProject.settings import Config, DevelopmentConfig, ProductionConfig
from flask_cors import CORS
from app.models.local_models import metadata_local
from app.models.external_models import metadata_external1
from celery_task.celery import make_celery

def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True,resources={r"/*": {"origins": "*"}})
    if test_config is not None:
        app.config.from_mapping(test_config)
    config_name = os.getenv('FLASK_ENV')
    if config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                           poolclass=QueuePool,
                           pool_size=app.config['SQLALCHEMY_POOL_SIZE'],
                           max_overflow=app.config['SQLALCHEMY_MAX_OVERFLOW'],
                           pool_timeout=app.config['SQLALCHEMY_POOL_TIMEOUT'],
                           pool_recycle=app.config['SQLALCHEMY_POOL_RECYCLE'],
                           pool_pre_ping=True,
                           pool_use_lifo=True,
                           echo=True)
    metadata_local.bind = engine
    engine1 = create_engine(app.config['FIRST_DATABASE_URI'],
                            poolclass=QueuePool,
                            pool_size=app.config['SQLALCHEMY_POOL_SIZE'],
                            max_overflow=app.config['SQLALCHEMY_MAX_OVERFLOW'],
                            pool_timeout=app.config['SQLALCHEMY_POOL_TIMEOUT'],
                            pool_recycle=app.config['SQLALCHEMY_POOL_RECYCLE'],
                            pool_pre_ping=True,
                            pool_use_lifo=True,
                            echo=True)
    metadata_external1.bind = engine1
    Session = scoped_session(sessionmaker(bind=engine))
    Session1 = scoped_session(sessionmaker(bind=engine1))
    app.extensions['sqlalchemy'] = {
        'local_session': Session,
        'third_party_session1': Session1
    }
    @app.before_request
    def before_request():
        db_session = Session()
        request._db_session = db_session
    @app.after_request
    def after_request(response):
        db_session = getattr(request, '_db_session', None)
        if db_session is not None:
            try:
                db_session.commit()
            except Exception as e:
                db_session.rollback()
                return jsonify({
                    'code': 500,
                    'data': {
                        'error': str(e)
                    }
                })
            finally:
                Session.remove()
        return response
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        Session.remove()
        Session1.remove()

    make_celery(app)
    from app.spc import views as spc
    app.register_blueprint(spc.bp)
    from app.auth import views as auth
    app.register_blueprint(auth.bp)
    from app.models.local_models import User, Department, Process, Project, Data
    from app.models.external_models import FirstExternalModel
    return app

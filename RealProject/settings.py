#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
class Config:
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_POOL_RECYCLE = 3600
    @staticmethod
    def get_db_uri(dbname):
        return f'mysql+pymysql://root:123456@localhost/{dbname}'
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', Config.get_db_uri('spc_db'))
    FIRST_DATABASE_URI = os.environ.get('FIRST_DATABASE_URI', Config.get_db_uri('first_external'))
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', Config.get_db_uri('spc_db'))
    FIRST_DATABASE_URI = os.environ.get('FIRST_DATABASE_URI', Config.get_db_uri('first_external'))

    



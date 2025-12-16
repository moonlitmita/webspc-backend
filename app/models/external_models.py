#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from sqlalchemy import Column, Float, Integer, MetaData, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

metadata_external1 = MetaData()
Base_external1 = declarative_base(metadata=metadata_external1)

class BaseModel(Base_external1):
    __abstract__ = True
    add_date = Column(DateTime, nullable=False, default=datetime.now) 

class FirstExternalModel(BaseModel):
    __tablename__ = "resistance"
    id = Column(Integer, primary_key=True)
    shift = Column(String(128), nullable=False)
    resistance = Column(Float, nullable=False)
    def __init__(self, shift, resistance):
        self.shift = shift
        self.resistance = resistance
    
    def to_dict(self):
        return {
            "id": self.id,
            "shift": self.shift,
            "resistance": self.resistance
        }


        
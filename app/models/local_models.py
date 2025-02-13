#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

metadata_local = MetaData()
Base_local = declarative_base(metadata=metadata_local)

class BaseModel(Base_local):
    __abstract__ = True
    add_date = Column(DateTime, nullable=False, default=datetime.now) 
    upd_date = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False) 
class Department(BaseModel):
    __tablename__ = "department"
    id = Column(Integer, primary_key=True)
    department = Column(String(128), nullable=False)
    users = relationship("User", backref="department")
    processes = relationship("Process", backref="department")
    def __init__(self, department):
        self.department = department
    def to_dict(self):
        return {
            "id": self.id,
            "dep": self.department,
            "add_date": self.add_date.strftime("%d %b %Y %H:%M:%S"),
            "upd_date": self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }
class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    realname = Column(String(128), unique=False, nullable=False)
    gender = Column(String(80), nullable=False)
    username = Column(String(128), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))
    password = Column(String(320), nullable=False)
    is_super_user = Column(Boolean, default=False, nullable=False)         
    is_staff = Column(Boolean, default=False, nullable=False) 
    is_active = Column(Boolean, default=False, nullable=False)  
    last_login = Column(DateTime, default=datetime.now, nullable=True) 
    def __init__(self, realname, gender, username, department_id, password, is_super_user, is_staff, is_active):
        self.realname = realname
        self.gender = gender
        self.username = username
        self.department_id = department_id
        self.password = password
        self.is_super_user = is_super_user
        self.is_staff = is_staff
        self.is_active = is_active
    def to_dict(self):
        return {
            'id': self.id,
            'realname': self.realname,
            'gender': self.gender,
            'username': self.username,
            'dep': self.department.department if self.department else None,
            'password': self.password,
            'is_super_user': str(self.is_super_user),
            'is_staff': str(self.is_staff),
            'is_active': str(self.is_active),
            'add_date' : self.add_date.strftime("%d %b %Y %H:%M:%S"),
            'upd_date': self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }  
class Process(BaseModel):
    __tablename__ = "process"
    id = Column(Integer, primary_key=True)
    process = Column(String(128), nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))
    projects = relationship("Project", backref="process")

    def __init__(self, process, department_id):
        self.process = process
        self.department_id = department_id
    def to_dict(self):
        return {
            "id": self.id,
            "process": self.process,
            "dep": self.department.department,
            "add_date": self.add_date.strftime("%d %b %Y %H:%M:%S"),
            "upd_date": self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }
class Project(BaseModel):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    product = Column(String(128), nullable=False)
    project = Column(String(128), nullable=False)
    spcType1 = Column(String(80), nullable=False)
    spcType2 = Column(String(80), nullable=True)
    spcType3 = Column(String(80), nullable=True)
    sampleSize = Column(Integer, nullable=False)
    USL = Column(Float, nullable=False)
    LSL = Column(Float, nullable=False)
    selectedChecks = Column(String(80), default='')
    dataCollectionType = Column(String(80), nullable=False)
    process_id = Column(Integer, ForeignKey("process.id"))
    datas = relationship("Data", backref="project")
    def __init__(self, product, project, spcType1, spcType2, spcType3, sampleSize, USL, LSL, process_id, selectedChecks, dataCollectionType):
        self.product = product
        self.project = project
        self.spcType1 = spcType1
        self.spcType2 = spcType2
        self.spcType3 = spcType3
        self.sampleSize = sampleSize
        self.USL = USL
        self.LSL = LSL
        self.process_id = process_id
        self.selectedChecks = selectedChecks
        self.dataCollectionType = dataCollectionType
    def to_dict(self):
        selected_check_list = [],
        if self.selectedChecks is not None:
            if isinstance(self.selectedChecks, str):
                selected_check_list = list(self.selectedChecks.split(','))
        return {
            "id": self.id,
            "product": self.product,
            "project": self.project,
            "spcType1": self.spcType1,
            "spcType2": self.spcType2,
            "spcType3": self.spcType3,
            "sampleSize": self.sampleSize,
            "USL": self.USL,
            "LSL": self.LSL,
            "process": self.process.process,
            "dep": self.process.department.department,
            "selectedChecks": selected_check_list,
            "dataCollectionType": self.dataCollectionType,
            "add_date": self.add_date.strftime("%d %b %Y %H:%M:%S"),
            "upd_date": self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }
class Data(BaseModel):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"))
    samples = Column(String(128), nullable=False)

    def __init__(self, project_id, samples):
        self.project_id = project_id
        self.samples = samples

    def to_dict(self): 
        return {
            "id": self.id,
            "project_id": self.project_id,
            "samples": list(map(float, self.samples.split(','))),
            "add_date": self.add_date.strftime("%d %b %Y %H:%M:%S"),
            "upd_date": self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }

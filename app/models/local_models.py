#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import re

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
    datas = relationship("Data", backref="project", cascade="all, delete-orphan")
    task = relationship("PeriodicTask", back_populates="project", uselist=False, cascade="all, delete-orphan")
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
            "process": self.process.process if self.process else None,
            "dep": self.process.department.department if self.process and self.process.department else None,
            "selectedChecks": selected_check_list,
            "dataCollectionType": self.dataCollectionType,
            "add_date": self.add_date.strftime("%d %b %Y %H:%M:%S"),
            "upd_date": self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }
    
class Data(BaseModel):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    samples = Column(String(128), nullable=False)

    def __init__(self, project_id, samples):
        self.project_id = project_id
        # 验证并清理 samples 数据
        self.samples = self._validate_samples(samples)

    def _validate_samples(self, samples):
        """
        验证 samples 数据，确保所有值都是有效的数字
        如果任何值无效，则抛出异常拒绝整条数据
        """
        if not samples:
            raise ValueError("samples 不能为空")
        
        samples_str = str(samples).strip()
        if not samples_str:
            raise ValueError("samples 不能为空字符串")
        
        valid_samples = []
        raw_values = samples_str.split(',')
        
        for i, s in enumerate(raw_values):
            s = s.strip()
            # 不允许空字符串
            if not s:
                raise ValueError(
                    f"samples 数据格式错误：第{i+1}个值为空。"
                    f"原始数据: '{samples_str}'"
                )
            
            # 必须是有效数字
            try:
                float_val = float(s)
                valid_samples.append(str(float_val))  # 标准化为字符串
            except ValueError:
                raise ValueError(
                    f"samples 数据格式错误：第{i+1}个值 '{s}' 不是有效数字。"
                    f"原始数据: '{samples_str}'"
                )
        
        if not valid_samples:
            raise ValueError("samples 中没有有效的数字")
        
        return ','.join(valid_samples)

    def to_dict(self):
        # 处理 samples 字段，过滤空字符串和无效值
        sample_list = []
        if self.samples:
            for s in self.samples.split(','):
                s = s.strip()
                if s:  # 跳过空字符串
                    try:
                        sample_list.append(float(s))
                    except ValueError:
                        # 如果无法转换为 float，跳过该值
                        pass
        
        return {
            "id": self.id,
            "project_id": self.project_id,
            "samples": sample_list,
            "add_date": self.add_date.strftime("%d %b %Y %H:%M:%S"),
            "upd_date": self.upd_date.strftime("%d %b %Y %H:%M:%S")
        }
    
class PeriodicTask(BaseModel):
    """
    周期性任务配置模型
    """
    __tablename__ = 'periodic_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, comment='任务名称')
    task = Column(String(255), nullable=False, comment='任务函数路径')
    enabled = Column(Boolean, default=True, comment='是否启用')
    schedule_type = Column(String(50), nullable=False, comment='调度类型 (interval/crontab)')
    schedule_value = Column(Text, nullable=False, comment='调度参数 (JSON格式)')
    args = Column(Text, comment='任务参数 (JSON格式)')
    kwargs = Column(Text, comment='任务关键字参数 (JSON格式)')
    project_id = Column(Integer,
                        ForeignKey("project.id", ondelete="CASCADE"),
                        nullable=False)
    project = relationship("Project", back_populates="task")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'task': self.task,
            'enabled': self.enabled,
            'schedule_type': self.schedule_type,
            'schedule_value': self.schedule_value,
            'args': self.args,
            'kwargs': self.kwargs,
            'add_date': self.add_date.isoformat() if self.add_date else None,
            'upd_date': self.upd_date.isoformat() if self.upd_date else None
        }

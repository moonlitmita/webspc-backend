#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from celery.beat import Scheduler, ScheduleEntry
from celery.utils.log import get_logger
import json
from datetime import timedelta, datetime
from time import time

logger = get_logger(__name__)

class DatabaseScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        self._schedule = {}
        self._last_updated = datetime.min
        self._last_timestamp = time()
        self.app = kwargs.get('app')
        super().__init__(*args, **kwargs)
        # 初始化时从数据库加载任务
        self.update_from_db()

    def update_from_db(self):
        """从数据库更新调度配置"""
        try:
            # 获取Flask应用上下文
            if self.app and hasattr(self.app, 'extensions'):
                # 在Celery Beat进程中使用
                app = self.app
                self._update_schedule_internal(app)
            else:
                # 创建临时应用上下文
                from RealProject import create_app
                temp_app = create_app()
                with temp_app.app_context():
                    self._update_schedule_internal(temp_app)
        except Exception as e:
            logger.error(f"更新调度配置失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _update_schedule_internal(self, app):
        """内部更新调度配置方法"""
        try:
            from app.models.local_models import PeriodicTask

            # 检查app.extensions是否包含sqlalchemy
            if 'sqlalchemy' not in app.extensions:
                logger.error("SQLAlchemy extension not found in app extensions")
                return

            session = app.extensions['sqlalchemy']['local_session']

            # 查询所有启用的任务 - 使用autocommit模式避免不必要的事务
            db_tasks = session.query(PeriodicTask).filter(PeriodicTask.enabled == True).all()

            new_schedule = {}
            for db_task in db_tasks:
                task_schedule = self._get_schedule_from_db_task(db_task)
                if task_schedule:
                    new_schedule[db_task.name] = task_schedule

            self._schedule = new_schedule
            self._last_updated = datetime.now()
            logger.info(f"成功更新 {len(new_schedule)} 个调度任务")

        except Exception as e:
            logger.error(f"内部更新调度配置失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _get_schedule_from_db_task(self, db_task):
        """从数据库任务对象创建Celery调度对象"""
        try:
            schedule_value = json.loads(db_task.schedule_value)
            
            task_schedule = None
            if db_task.schedule_type == 'interval':
                # 解析间隔调度
                if isinstance(schedule_value, dict):
                    interval_seconds = int(schedule_value.get('every', 30))
                else:
                    interval_seconds = int(schedule_value)  # 假设是简单数字
                task_schedule = timedelta(seconds=interval_seconds)
            elif db_task.schedule_type == 'crontab':
                # 解析crontab调度
                from celery.schedules import crontab
                task_schedule = crontab(
                    minute=schedule_value.get('minute', '*'),
                    hour=schedule_value.get('hour', '*'),
                    day_of_week=schedule_value.get('day_of_week', '*'),
                    day_of_month=schedule_value.get('day_of_month', '*'),
                    month_of_year=schedule_value.get('month_of_year', '*')
                )
            else:
                logger.error(f"未知的调度类型: {db_task.schedule_type}")
                return None

            # 解析任务参数
            args = tuple()
            kwargs = {}
            if db_task.args:
                args = tuple(json.loads(db_task.args))
            if db_task.kwargs:
                kwargs = json.loads(db_task.kwargs)

            # 创建调度条目
            entry = ScheduleEntry(
                name=db_task.name,
                task=db_task.task,
                schedule=task_schedule,
                args=args,
                kwargs=kwargs,
                options={},
                last_run_at=self.app.now() if self.app else None,
            )
            return entry
        except Exception as e:
            logger.error(f"解析任务调度配置失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def tick(self, *args, **kwargs):
        """重写tick方法以支持动态更新"""
        # 检查是否需要更新调度（例如，每分钟检查一次）
        now = datetime.now()
        if (now - self._last_updated).seconds > 30:  # 每30秒检查更新
            self.update_from_db()
        return super().tick(*args, **kwargs)

    @property
    def schedule(self):
        return self._schedule

    def should_sync(self):
        """检查是否需要同步"""
        return (datetime.now() - self._last_updated).seconds > 30
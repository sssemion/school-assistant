import sqlalchemy

from sqlalchemy import orm
from data.db_session import SqlAlchemyBase

class Student(SqlAlchemyBase):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    vk_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    school_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    login_data = sqlalchemy.Column(sqlalchemy.String)
    dialogue_point = sqlalchemy.Column(sqlalchemy.String)
    daily_hometask = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    mailing_time = sqlalchemy.Column(sqlalchemy.Time)
    new_marks_alerts = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    debts_alerts = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    marks = orm.relation('Mark', back_populates='student', lazy='subquery')
    sessions = orm.relation('ApiSession', back_populates='student', lazy='subquery')

    def __repr__(self):
        return f"<Student> id:{self.id} vk:{self.vk_id}"

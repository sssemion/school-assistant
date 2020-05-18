import sqlalchemy

from sqlalchemy import orm
from bot_app.data.db_session import SqlAlchemyBase


class Student(SqlAlchemyBase):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    vk_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    school_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    login_data = sqlalchemy.Column(sqlalchemy.String)
    dialogue_point = sqlalchemy.Column(sqlalchemy.String)
    daily_hometask = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    sessions = orm.relation('ApiSession', back_populates='student', lazy='subquery')

    def __repr__(self):
        return f"<Student> id:{self.id} vk:{self.vk_id}"

    def __eq__(self, other):
        return self.id == other.id

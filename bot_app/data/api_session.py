import sqlalchemy
from sqlalchemy import orm

from bot_app.data.db_session import SqlAlchemyBase


class ApiSession(SqlAlchemyBase):
    __tablename__ = 'api_sessions'

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('students.id'))
    session_id = sqlalchemy.Column(sqlalchemy.String)
    expires = sqlalchemy.Column(sqlalchemy.DateTime)

    student = orm.relation('Student', foreign_keys=[student_id])

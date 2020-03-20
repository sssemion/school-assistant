import sqlalchemy
from sqlalchemy import orm

from bot_app.data.db_session import SqlAlchemyBase


class Mark(SqlAlchemyBase):
    __tablename__ = 'marks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('students.id'))
    subject_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('subjects.id'))
    mark = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.Date)
    description = sqlalchemy.Column(sqlalchemy.String)

    student = orm.relation('Student', foreign_keys=[student_id])
    subject = orm.relation('Subject', foreign_keys=[subject_id])

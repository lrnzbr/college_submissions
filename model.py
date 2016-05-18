from sqlalchemy import Column,Integer,String, DateTime, ForeignKey, Text

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    email = Column(String(255), unique=True)
    applications = relationship("Application", back_populates="student")
    password_hash = Column(String(255))
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Application(Base):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    school = Column(String(80))
    timestamp = Column(DateTime, default=func.now())
    confirmation = Column(String, unique=True)
    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student", back_populates="applications")
    essay = Column(Text)

engine = create_engine('sqlite:///SixUp.db')
Base.metadata.create_all(engine)

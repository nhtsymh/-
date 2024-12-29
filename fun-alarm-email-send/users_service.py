import json
import urllib.parse
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from custom_json_encoder import DateTimeEncoder

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(255))
    port = Column(Integer)
    username = Column(String(255))
    password = Column(String(255))
    sender = Column(String(255))
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

def get_db_connection():
    DB_HOST = 'pc-bp1nmlh4yr4q80681.rwlb.rds.aliyuncs.com'
    DB_PORT = 3306
    DB_USER = 'synx_2022090917012'
    DB_PASSWORD = 'feng_2005'
    DB_NAME = 'db_message_2022090917012'
    
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    return Session()

async def register_user(data) -> Dict[str, Any]:
    """
    注册用户
    """
    with get_db_connection() as session:
        try:
            user = User(
                host=data['host'],
                port=data['port'],
                username=data['username'],
                password=data['password'],
                sender=data['sender']
            )
            session.add(user)
            session.commit()
            return {"message": "User registered successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}

async def update_user(data) -> Dict[str, Any]:
    """
    更新用户
    """
    with get_db_connection() as session:
        try:
            user_id = data.get("id", None)
            if not user_id:
                raise ValueError("User_id is required")

            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            for key in ['host', 'port', 'username', 'password', 'sender']:
                if key in data:
                    setattr(user, key, data[key])

            session.commit()
            return {"message": "User updated successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}
async def delete_user(data) -> Dict[str, Any]:
    """
    删除用户
    """
    with get_db_connection() as session:
        try:
            user_id = data.get("id", None)
            if not user_id:
                raise ValueError("User_id is required")

            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            session.delete(user)
            session.commit()
            return {"message": "User deleted successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}

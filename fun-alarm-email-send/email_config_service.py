import json
import urllib.parse
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from custom_json_encoder import DateTimeEncoder

Base = declarative_base()

class Config(Base):
    __tablename__ = 'tbl_config'
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
async def create_config(data) -> Dict[str, Any]:
    """
    创建配置
    """
    with get_db_connection() as session:
        try:
            config = Config(
                host=data['host'],
                port=data['port'],
                username=data['username'],
                password=data['password'],
                sender=data['sender']
            )
            session.add(config)
            session.commit()
            return {"message": "Config created successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}
async def read_config(data) -> Dict[str, Any]:
    """
    读取配置，简化查询
    """
    with get_db_connection() as session:
        try:
            config = session.query(Config).first()
            if config:
                config_dict = {
                    "id": config.id,
                    "host": config.host,
                    "port": config.port,
                    "username": config.username,
                    "password": config.password,
                    "sender": config.sender,
                    "create_time": config.create_time,
                    "update_time": config.update_time,
                }
                return config_dict
        except SQLAlchemyError as e:
            return {"error": str(e)}
async def update_config(data) -> Dict[str, Any]:
    """
    更新配置
    """
    with get_db_connection() as session:
        try:
            config_id = data.get("id", None)
            if not config_id:
                raise ValueError("id is required")

            config = session.query(Config).filter(Config.id == config_id).first()
            if not config:
                raise ValueError("Config not found")

            for key in ['host', 'port', 'username', 'password', 'sender']:
                if key in data:
                    setattr(config, key, data[key])

            session.commit()
            return {"message": "Config updated successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}
async def delete_config(data) -> Dict[str, Any]:
    """
    删除配置
    """
    with get_db_connection() as session:
        try:
            config_id = data.get("id", None)
            if not config_id:
                raise ValueError("id is required")

            config = session.query(Config).filter(Config.id == config_id).first()
            if not config:
                raise ValueError("Config not found")

            session.delete(config)
            session.commit()
            return {"message": "Config deleted successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            return {"error": str(e)}

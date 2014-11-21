"""
SQLAlchemy module for mapper configuration.
Similar to SQLAlchemy class from flask.ext.sqlalchemy.
"""
import config
config_dict = config.__dict__

from sqlalchemy import create_engine, engine_from_config, func, ForeignKey, \
	Column, Boolean, DateTime, Enum, SmallInteger, Integer, BigInteger, String
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


Model = declarative_base()

prefix = 'sqlalchemy_'
engine = engine_from_config(
	{ key: config_dict[key] for key in config_dict if key.startswith(prefix) }, 
	prefix=prefix)

Session = sessionmaker(bind=engine)
# session = None # Session()

create_all = lambda: Model.metadata.create_all(engine)
drop_all = lambda: Model.metadata.drop_all(engine)

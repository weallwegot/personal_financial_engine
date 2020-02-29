# coding: utf-8
"""
connector class and methods for ORM sqlalchemy
"""

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

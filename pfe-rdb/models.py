# coding: utf-8
"""
ORM models for sqlalchemy
generated using sqlacodegen

"""
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AccountItem(Base):
    __tablename__ = 'AccountItems'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"AccountItems_id_seq\"'::regclass)"))
    name = Column(String)
    balance = Column(Float(53))
    type = Column(Enum('Credit', 'Checking', 'Saving', name='accounttype'))


class User(Base):
    __tablename__ = 'Users'

    id = Column(String, primary_key=True)
    is_paying = Column(Boolean)
    email = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Simulation(Base):
    __tablename__ = 'Simulations'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('Users.id'))
    created_at = Column(DateTime)

    user = relationship('User')


class BudgetItem(Base):
    __tablename__ = 'BudgetItems'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"BudgetItems_id_seq\"'::regclass)"))
    user_id = Column(ForeignKey('Users.id'))
    amount = Column(Float(53))
    description = Column(String)
    transaction_type = Column(Enum('Income', 'Expense', 'Transfer', name='transactiontype'))
    frequency = Column(Integer)
    sample_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime)
    simulation_id = Column(ForeignKey('Simulations.id'))

    simulation = relationship('Simulation')
    user = relationship('User')


class ForecastedDay(Base):
    __tablename__ = 'ForecastedDays'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('Users.id'))
    forecast_day = Column(Date)
    total = Column(Float(53))
    account_totals = Column(JSON)
    simulation_id = Column(ForeignKey('Simulations.id'))

    simulation = relationship('Simulation')
    user = relationship('User')

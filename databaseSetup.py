#!/usr/bin/env python
"""
Udacity Item Catalog Project

Author: Efren Aguilar

Python Version 3.7.2 used when created

This module is used to intialize the database used for this project as well
as declare the implementations of the tables of said database using the
sqlalchemy object relational mapper
"""

import sys

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """The User class used to create the user table in the database

    Attributes:
        __tablename__ (str): The name of the table made (user)
        id (Column): An integer column, used as the primary key
        name (Column): A String(250) column, contains the name of the user
        email (Column): A String(250) column, contains the email of the user
        picture (Column): A String(250) column, contains link to user image
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """The Category class used to create the category table in the database

    Attributes:
        __tablename__ (str): The name of the table made (category)
        id (Column): An integer column, used as the primary key
        name (Column): A String(80) column, contains name of the Category
    """

    __tablename__ = "category"  #: The name of the table

    id = Column(Integer, primary_key=True)

    name = Column(String(80), nullable=False, unique=True)

    @property
    def serialize(self):
        """dict: Returns object data in easily serializable format"""
        return{
            "id": self.id,
            "name": self.name
        }


class Item(Base):
    """The Item class used to create the item table in the database

    Attributes:
        __tablename__ (str): The name of the table made (item)
        cat_id (Column): An integer column, a foreign key to category table
        description (Column): A String(250) column, contains Item description
        id (Column): An integer column, used as the primary key
        title (Column): A String(80) column, contains title/name of the Item
        user_id (Column): An integer column, a foreign key to the user table
    """
    __tablename__ = "item"

    cat_id = Column(Integer, ForeignKey("category.id"))

    description = Column(String(250))

    id = Column(Integer, primary_key=True)

    title = Column(String(80), nullable=False)

    category = relationship(Category)

    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship(User)

    UniqueConstraint('cat_id', 'title')

    @property
    def serialize(self):
        """dict: Returns object data in easily serializable format"""
        return{
            "cat_id": self.cat_id,
            "description": self.description,
            "id": self.id,
            "title": self.title
        }

engine = create_engine("sqlite:///itemCatalog.db")

Base.metadata.create_all(engine)

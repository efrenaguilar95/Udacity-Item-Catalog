#!/usr/bin/env python
"""
Udacity Item Catalog Project

Author: Efren Aguilar

Python Version 3.7.2 used when created

This module is used to populate the database for this
project with a small set of example data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databaseSetup import Category, Item, Base, User

engine = create_engine('sqlite:///itemCatalog.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Data for fake users
User1 = User(name="Eli Benson", email="elibenson@fake.net",
             picture=("https://pbs.twimg.com/profile_images"
                      "/2671170543/"
                      "18debd694829ed78203a5a36dd364160_400x400.png"))

User2 = User(name="Shaun Wells", email="swells@false.com",
             picture=("https://pbs.twimg.com/profile_images"
                      "/2671170543/"
                      "18debd694829ed78203a5a36dd364160_400x400.png"))

# Data for Soccer
soccer = Category(name="Soccer")

soccerItem1 = Item(user_id=1, title="Two Shinguards",
                   description="Two pairs of shinguards", category=soccer)

soccerItem2 = Item(user_id=1, title="Shinguards",
                   description="A pair of shinguards", category=soccer)

soccerItem3 = Item(user_id=1, title="Jersey",
                   description="A soccer jersey", category=soccer)

soccerItem4 = Item(user_id=1, title="Soccer Cleats",
                   description="A pair of soccer cleats", category=soccer)

# Data for Basketball
basketball = Category(name="Basketball")

# Data for Baseball
baseball = Category(name="Baseball")

baseballItem1 = Item(user_id=1, title="Bat",
                     description="A baseball bat", category=baseball)

# Data for Frisbee
frisbee = Category(name="Frisbee")

frisbeeItem1 = Item(user_id=1, title="Frisbee",
                    description="A frisbee", category=frisbee)

# Data for Snowboarding
snowboarding = Category(name="Snowboarding")

snowboardingItem1 = Item(user_id=2, title="Goggles",
                         description=("Snowboarding goggles used"
                                      " to protect the eyes from snow"),
                         category=snowboarding)

snowboardingItem2 = Item(user_id=2, title="Snowboard",
                         description="A snowboard", category=snowboarding)

# Data for Rock Climbing
rockClimbing = Category(name="Rock Climbing")

# Data for Foosball
foosball = Category(name="Foosball")

# Data for Skating
skating = Category(name="Skating")

# Data for Hockey
hockey = Category(name="Hockey")

hockeyItem1 = Item(user_id=2, title="Stick",
                   description="A hockey stick", category=hockey)

dataToCommit = [User1, User2, soccer, soccerItem1, soccerItem2,
                soccerItem3, soccerItem4, basketball, baseball, baseballItem1,
                frisbee, frisbeeItem1, snowboarding, snowboardingItem1,
                snowboardingItem2, rockClimbing, foosball,
                skating, hockey, hockeyItem1]

for data in dataToCommit:
    session.add(data)
    session.commit()

print("Database populated!")

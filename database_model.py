from sqlalchemy import create_engine

engine = create_engine('sqlite:///storage.db')

from sqlalchemy import Column, Integer, Text, MetaData, Table, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ArrowType
import arrow

Base = declarative_base()


class Politician(Base):
    __tablename__ = 'politicians'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fraction = Column(String)
    twitter_handle = Column(String)
    tweets = relationship("Tweet", back_populates="politician")
    start_date = Column(ArrowType)
    end_date = Column(ArrowType)


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    date = Column(ArrowType)
    text = Column(String)
    politician_id = Column(Integer, ForeignKey('politicians.id'))
    politician = relationship("Politician", back_populates="tweets")
    hashtags = relationship("Hashtag", back_populates="tweet")
    links = relationship("Link", back_populates="tweet")
    nlikes = Column(Integer)
    nreplie = Column(Integer)
    nretweets = Column(Integer)


class Hashtag(Base):
    __tablename__ = 'hashtags'

    id = Column(Integer, primary_key=True)
    tag = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    tweet = relationship("Tweet", back_populates="hashtags")


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    link_original = Column(String)
    link_followed = Column(String)
    base_url = Column(String)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    Lin_cCategoization = relationship("LinkCategory")
    tweet = relationship("Tweet", back_populates="links")
    # TODO remove unused columns in database


class LinkCategory(Base):
    __tablename__ = 'linkcategorys'

    id = Column(Integer, primary_key=True)
    link_original = Column(String, ForeignKey('links.link_original'))
    link_followed = Column(String)
    base_url = Column(String)


def get_session(**kwargs):
    Session = sessionmaker(bind=engine)
    session = Session(**kwargs)
    return session


if __name__ == "__main__":
    Base.metadata.create_all(engine)




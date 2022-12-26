from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base

class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256) , index=True,nullable=False)
    password = Column(String(256),default="MyPassword@11")
    csrf_token = Column(String(256),default="MyCsrfToken")

class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, index=True)
    insta_user_name = Column(String)
    message = Column(String, default="")
    following_names = Column(String, default="")
    progress = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    following_success_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)
    celebrity = relationship("Following", back_populates="follower")


class Following(Base):
    __tablename__ = "followings"

    id = Column(Integer, primary_key=True,unique=True, index=True)
    instagram_id = Column(String)
    username = Column(String)
    full_name = Column(String)
    profile_link = Column(String)
    avatar_pic = Column(String)
    followed_by_viewer = Column(Boolean)
    is_varified = Column(Boolean)
    followers_count = Column(Integer)
    following_count = Column(Integer)
    biography = Column(String)
    public_email = Column(String)
    posts_count = Column(Integer)
    phone_country_code = Column(String)
    phone_number = Column(String)
    city = Column(String)
    address = Column(String)
    is_private = Column(Boolean)
    is_business = Column(Boolean)
    external_url = Column(String)
    description = Column(String)
    follower_id = Column(Integer, ForeignKey("influencers.id"))

    follower = relationship("Influencer", back_populates="celebrity")



class Csv(Base):
    __tablename__ = "csvs"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(256) , index=True,nullable=True,default="")
    file_path = Column(String(256),nullable=True,default="")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="csvs")
from sqlalchemy.orm import Session

from models import insta
from schemas import schemas


def get_influencer_by_id(db: Session, influencer_id: int):
    return db.query(models.Influencer).filter(models.Influencer.id == influencer_id).first()


def get_influencer_by_insta_user_name(db: Session, insta_user_name: str):
    return db.query(insta.Influencer).filter(insta.Influencer.insta_user_name == insta_user_name).first()


def get_influencer(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Influencer).offset(skip).limit(limit).all()


def create_influencer(db: Session, insta_user_name: str):
    db_user = insta.Influencer(insta_user_name=insta_user_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def creat_bot(db: Session, bot: schemas.BotBase):
    db_bot = models.Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot


def get_bot_by_id(db: Session, bot_id: int):
    return db.query(insta.Bot).filter(insta.Bot.id == bot_id).first()

def get_bot_list(db: Session):
    return db.query(insta.Bot).all()


def get_following(db: Session, skip: int = 0, limit: int = 100):
    return db.query(insta.Following).offset(skip).limit(limit).all()


def create_influencer_following(db: Session, following: schemas.FollowingCreate):
    db_item = insta.Following(**following.dict(), id=following.follower_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item.id

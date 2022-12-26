from pydantic import BaseModel

class BotBase(BaseModel):
    name: str = None
    password: str = None
    csrf_token: str =   None

class FollowingBase(BaseModel):

    instagram_id: str = None
    username: str = None
    full_name: str = None
    profile_link: str = None
    avatar_pic: str = None
    followed_by_viewer: bool = None
    is_varified: bool = None
    followers_count: int = None
    following_count: int = None
    biography: str = None
    public_email: str = None
    posts_count: int = None
    phone_country_code: str = None
    phone_number: str = None
    city: str = None
    address: str = None
    is_private: bool = None
    is_business: bool = None
    external_url: str = None
    description: str = None
    follower_id: int = None

class FollowingCreate(FollowingBase):
    pass


class Following(FollowingBase):
    id: int
    # class Config:
    #     orm_mode = True


class InfluencerBase(BaseModel):
    insta_user_name: str = None
    message: str = None
    following_names: str = None
    progress: int = None
    attempts: int = None
    completed: bool  = None
    following_success_count: int    = None
    is_active: bool     = None


class InfluencerCreate(InfluencerBase):
    pass

class Influencer(InfluencerBase):
    id: int
    is_active: bool
    following: list[Following] = []

    class Config:
        orm_mode = True

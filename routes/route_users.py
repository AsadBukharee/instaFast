
from fastapi import APIRouter
from fastapi import Depends

from controllers.users import create_new_user
from database import get_db
from schemas.users import ShowUser
from schemas.users import UserCreate
from sqlalchemy.orm import Session

router = APIRouter(tags=["User Activity"])


@router.post("/", response_model=ShowUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user = create_new_user(user=user, db=db)
    return user

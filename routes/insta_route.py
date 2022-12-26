import random
import time

import redis
from fastapi import APIRouter ,Depends,  HTTPException,Request,Form
from starlette.templating import Jinja2Templates
import crud
from database import get_db
from schemas import schemas
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
templates = Jinja2Templates(directory="templates")
redis_client= redis.Redis(host='127.0.0.1', port=6379, db=0)

router = APIRouter(tags=["Instagram Activity"])




@router.post("/add_bot/", response_model=schemas.BotBase)
def create_bot(bot: schemas.BotBase, db: Session = Depends(get_db)):
    crud.creat_bot(db, bot)
    return {"message": "Bot added successfully"}

@router.get("/list_bot/", response_model=schemas.BotBase)
def get_bot(db: Session = Depends(get_db)):
    return crud.get_bot_list(db)

@router.post("/create_influencer/", response_model=schemas.Influencer)
def create_influencer(influencer: schemas.InfluencerCreate, db: Session = Depends(get_db)):
    db_user = crud.get_influencer_by_insta_user_name(db, insta_user_name=influencer.insta_user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="user with this insta name already exists.")
    return crud.create_influencer(db=db, insta_user_name=influencer.insta_user_name)


@router.get("/influencer/", response_model=list[schemas.Influencer])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_influencer(db, skip=skip, limit=limit)
    return users


@router.get("/influencer/{influencer_id}", response_model=schemas.Influencer)
def read_user(influencer_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_influencer_by_id(db, influencer_id=influencer_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/create-following/", response_model=schemas.Following)
def create_item_for_user( following: schemas.FollowingCreate, db: Session = Depends(get_db)
):
    id = crud.create_influencer_following(db=db, following=following)
    return {"id": id}


@router.get("/followings/", response_model=list[schemas.Following])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_following(db, skip=skip, limit=limit)
    return items










@router.get("/progress")
async def progress_update():
    return {"progress": random.randint(0, 100)}


@router.get("/")
async def render_form(request: Request):
    return templates.TemplateResponse("index.html",context={"request": request})

# from fastapi.security.utils import get_authorization_scheme_param
from celery_worker import email_sender,insta_scraper
@router.post("/insta-scrap")
async def set_influencers(name: str = Form(), email: str = Form(), influencers: str = Form(), request: Request = None,db: Session = Depends(get_db)):
    print(name, email, influencers)
    # bots = crud.get_bot_list(db)
    token = "HVLfB6ZiZtWSmcJZFAgqdmL9xOnYlJqs"#bots[0].csrf_token
    task = email_sender.delay(name, email, influencers)
    insta_task = insta_scraper.delay(influencers,name,token)
    print("TASK ID IS : ",task.id,"  ",insta_task)
    return templates.TemplateResponse("index.html", context={"request": request})
    # return {"success": True, "message": "Influencers added successfully","status_code":status.HTTP_200_OK}






async def logGenerator(request):

    while(True):
        if await request.is_disconnected():
            print("client disconnected!!!")
            break
        if redis_client.get("tester"):
            done,total = redis_client.get("tester").decode().split(',')
            progress = round((int(done)/int(total))*100,2)
            yield str(progress)#str(random.randint(0, 100))
        else:
            yield str(0)
        time.sleep(1)

@router.get('/stream-logs')
async def runStatus(request: Request):
    event_generator = logGenerator(request)
    return EventSourceResponse(event_generator)
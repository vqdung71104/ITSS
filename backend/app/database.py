from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import env
from models.user_model import User
from models.task_model import Task
from models.project_model import Project
from models.group_model import Group
from models.evaluation_model import Evaluation
from pymongo.errors import OperationFailure
import logging

async def init_db():
  try:
    client = AsyncIOMotorClient(f"{env.MONGO_URI}?authSource=admin")
    db = client[env.DATABASE_NAME]
    await init_beanie(database=db, document_models=[User,Task, Project,Group,Evaluation])  
    logging.info("Connected to MongoDB")
  except OperationFailure as e:
    logging.error("Connect fail: %s", e)
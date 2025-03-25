from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import env
from models.user_model import User
from pymongo.errors import OperationFailure
import logging

async def init_db():
  try:
    client = AsyncIOMotorClient(env.MONGO_URI)
    db = client[env.DATABASE_NAME]
    await init_beanie(database=db, document_models=[User])  
    logging.info("Connected to MongoDB")
  except OperationFailure as e:
    logging.error(e)
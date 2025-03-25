import os
from dotenv import load_dotenv

load_dotenv()

class Env:
  MONGO_URI: str = os.getenv("MONGO_URI")
  DATABASE_NAME: str = os.getenv("DATABASE_NAME")
  PORT: int = int(os.getenv("PORT"))
  HOST: str = os.getenv("HOST")

env = Env()
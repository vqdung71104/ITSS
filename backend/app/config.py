import os
from dotenv import load_dotenv

load_dotenv()

class Env:
  MONGO_URI: str = os.getenv("MONGO_URI")
  DATABASE_NAME: str = os.getenv("DATABASE_NAME")
  PORT: int = int(os.getenv("PORT"))  
  HOST: str = os.getenv("HOST") 
  SECRET_KEY: str = os.getenv("SECRET_KEY")
  ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
  ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

env = Env()
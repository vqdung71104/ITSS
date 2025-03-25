from fastapi import APIRouter, HTTPException
from models.user_model import User
from schemas.user_schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
  user = User(**user_data.dict()) 
  await user.insert()
  return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
  user = await User.get(user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user_model import User
from outh2 import get_current_user, get_password_hash,verify_password
from token_handler import create_access_token
from schemas.user_schemas import UserCreate, UserResponse
from config import env

#Tạo router 
router = APIRouter(
    prefix = "/users",
    tags = ["users"],
    responses = {404: {"description": "Not found"}},
)

#kiểm tra người dùng có phải addmin không
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin privileges required",
        )
    return current_user

#kiểm tra người dùng có phải mentor không
async def get_current_mentor(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["mentor", "admin"]:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Mentor privileges required",
        )
    return current_user

# routes
@router.post("/register", response_model = UserResponse)
async def register_user(user: UserCreate):
    existing_user = await User.find_one({"email": user.email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    #Tao nguoi dung moi
    hashed_password = get_password_hash(user.password)
    
    new_user = User(
        HoDem= user.HoDem,
        Ten=user.Ten,
        email=user.email,
        role=user.role,
        password=hashed_password
    )
    
    await new_user.insert()
    return new_user

@router.post('/login', response_model = UserResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    #tìm người dùng theo email
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    #Tạo token chứa thông tin email và user_id
    access_token_expires = timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from services.user_service import UserService

router = APIRouter()

@router.get("/users/")
def read_users(db: Session = Depends(get_db)):
    try:
        users = UserService.get_all_users(db)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}
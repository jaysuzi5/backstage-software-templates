from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from framework.db import get_db
from models.user import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from framework.db import get_db
from models.user import User, UserCreate
from datetime import datetime, UTC
from fastapi import Body 

router = APIRouter()

def serialize_sqlalchemy_obj(obj):
    """Convert SQLAlchemy model instance to dict with all columns."""
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


@router.get("/api/v1/users")
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    try:
        offset = (page - 1) * limit
        users = db.query(User).offset(offset).limit(limit).all()
        return [serialize_sqlalchemy_obj(user) for user in users]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/api/v1/users")
def create_user(
    user_data: UserCreate = Body(...),
    db: Session = Depends(get_db)
):
    try:
        # Optionally check uniqueness constraints for username/email here
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")

        # Convert Pydantic model to dict, excluding unset values
        data = user_data.model_dump(exclude_unset=True)

        # Create new User instance with dynamic fields
        new_user = User(**data)
        new_user.create_date = datetime.now(UTC)
        new_user.update_date = datetime.now(UTC)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return serialize_sqlalchemy_obj(new_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from framework.db import get_db
from models.${{values.app_name}} import ${{values.app_name}}, ${{values.app_name}}Create
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from framework.db import get_db
from datetime import datetime, UTC
from fastapi import Body 

router = APIRouter()

def serialize_sqlalchemy_obj(obj):
    """Convert SQLAlchemy model instance to dict with all columns."""
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


@router.get("/api/v1/${{values.app_name}}")
def list_${{values.app_name}}(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    try:
        offset = (page - 1) * limit
        ${{values.app_name}}_records = db.query(${{values.app_name}}).offset(offset).limit(limit).all()
        return [serialize_sqlalchemy_obj(item) for item in ${{values.app_name}}_records]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/api/v1/${{values.app_name}}")
def create_record(
    ${{values.app_name}}_data: ${{values.app_name}}Create = Body(...),
    db: Session = Depends(get_db)
):
    try:
        # Optionally check uniqueness constraints
        # if db.query(${{values.app_name}}).filter(${{values.app_name}}.field == ${{values.app_name}}.field).first():
        #     raise HTTPException(status_code=400, detail="field already exists")

        # Convert Pydantic model to dict, excluding unset values
        data = ${{values.app_name}}_data.model_dump(exclude_unset=True)

        # Create new ${{values.app_name}} instance with dynamic fields
        new_record = ${{values.app_name}}(**data)
        new_record.create_date = datetime.now(UTC)
        new_record.update_date = datetime.now(UTC)

        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return serialize_sqlalchemy_obj(new_record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
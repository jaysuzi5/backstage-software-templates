import models
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, List
from framework.db import get_db

router = APIRouter()

def serialize_model(instance: Any) -> dict:
    return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}

@router.get("/api/v1/{table_name}")
def list_records(
    table_name: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        model_class = getattr(models, table_name.capitalize(), None)
        if not model_class:
            raise HTTPException(status_code=404, detail=f"Table {table_name} not found")

        offset = (page - 1) * limit
        records = db.query(model_class).offset(offset).limit(limit).all()

        return [serialize_model(record) for record in records]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

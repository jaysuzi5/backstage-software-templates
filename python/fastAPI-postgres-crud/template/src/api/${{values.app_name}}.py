from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from framework.db import get_db
from models.${{values.app_name}} import ${{values.app_name_capitalized}}, ${{values.app_name_capitalized}}Create
from datetime import datetime, UTC

router = APIRouter()

def serialize_sqlalchemy_obj(obj):
    """
    Convert a SQLAlchemy ORM model instance into a dictionary.

    Args:
        obj: SQLAlchemy model instance.

    Returns:
        dict: Dictionary containing all column names and their values.
    """
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


@router.get("/api/v1/${{values.app_name}}")
def list_${{values.app_name}}(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of ${{values.app_name_capitalized}} records.

    Args:
        page (int): Page number starting from 1.
        limit (int): Maximum number of records to return per page.
        db (Session): SQLAlchemy database session.

    Returns:
        list[dict]: A list of serialized ${{values.app_name_capitalized}} records.
    """
    try:
        offset = (page - 1) * limit
        ${{values.app_name}}_records = db.query(${{values.app_name}}).offset(offset).limit(limit).all()
        return [serialize_sqlalchemy_obj(item) for item in ${{values.app_name}}_records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/v1/${{values.app_name}}")
def create_record(
    ${{values.app_name}}_data: ${{values.app_name_capitalized}}Create = Body(..., description="Data for the new record"),
    db: Session = Depends(get_db)
):
    """
    Create a new ${{values.app_name_capitalized}} record.

    Args:
        ${{values.app_name}}_data (${{values.app_name_capitalized}}Create): Data model for the record to create.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The newly created ${{values.app_name_capitalized}} record.
    """
    try:
        data = ${{values.app_name}}_data.model_dump(exclude_unset=True)
        new_record = ${{values.app_name_capitalized}}(**data)
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


@router.get("/api/v1/${{values.app_name}}/{id}")
def get_${{values.app_name}}_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single ${{values.app_name_capitalized}} record by ID.

    Args:
        id (int): The ID of the record.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The matching ${{values.app_name_capitalized}} record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(${{values.app_name_capitalized}}).filter(${{values.app_name_capitalized}}.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"${{values.app_name_capitalized}} with id {id} not found")
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/api/v1/${{values.app_name}}/{id}")
def update_${{values.app_name}}_full(
    id: int,
    ${{values.app_name}}_data: ${{values.app_name_capitalized}}Create = Body(..., description="Updated data for the record"),
    db: Session = Depends(get_db)
):
    """
    Fully update an existing ${{values.app_name_capitalized}} record (all fields required).

    Args:
        id (int): The ID of the record to update.
        ${{values.app_name}}_data (${{values.app_name_capitalized}}Create): Updated record data (all fields).
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The updated ${{values.app_name_capitalized}} record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(${{values.app_name_capitalized}}).filter(${{values.app_name_capitalized}}.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"${{values.app_name_capitalized}} with id {id} not found")

        data = ${{values.app_name}}_data.model_dump(exclude_unset=False)
        for key, value in data.items():
            setattr(record, key, value)

        record.update_date = datetime.now(UTC)
        db.commit()
        db.refresh(record)
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/api/v1/${{values.app_name}}/{id}")
def update_${{values.app_name}}_partial(
    id: int,
    ${{values.app_name}}_data: ${{values.app_name_capitalized}}Create = Body(..., description="Partial updated data for the record"),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing ${{values.app_name_capitalized}} record (only provided fields are updated).

    Args:
        id (int): The ID of the record to update.
        ${{values.app_name_capitalized}}_data (${{values.app_name_capitalized}}Create): Partial updated data.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The updated ${{values.app_name_capitalized}} record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(${{values.app_name_capitalized}}).filter(${{values.app_name_capitalized}}.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"${{values.app_name_capitalized}} with id {id} not found")

        data = ${{values.app_name}}_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(record, key, value)

        record.update_date = datetime.now(UTC)
        db.commit()
        db.refresh(record)
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/api/v1/${{values.app_name}}/{id}")
def delete_${{values.app_name}}(id: int, db: Session = Depends(get_db)):
    """
    Delete a ${{values.app_name_capitalized}} record by ID.

    Args:
        id (int): The ID of the record to delete.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(${{values.app_name_capitalized}}).filter(${{values.app_name_capitalized}}.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"${{values.app_name_capitalized}} with id {id} not found")

        db.delete(record)
        db.commit()
        return {"detail": f"${{values.app_name_capitalized}} with id {id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

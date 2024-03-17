from fastapi import (
    APIRouter, 
    HTTPException, 
    status, 
    Depends)

from ..config.db import get_db

from ..models import Event as EventDbModel

from ..schemas import BaseEvent, Event, EventPreview

from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete

from typing import List

router = APIRouter(
    prefix="/api/events",
    tags=["API"]
)

@router.get("/", response_description="List of all events", response_model=List[EventPreview], status_code=status.HTTP_200_OK)
def get_all_events(db: Session=Depends(get_db)):

    stmt = select(EventDbModel.id, EventDbModel.type, EventDbModel.description)
    events = db.execute(stmt).fetchall()

    if events == []:
        execute_on_exception(db, status.HTTP_404_NOT_FOUND, f"Nothing found")
    return events


@router.get("/id/{id}", response_description="Get event by id", response_model=Event, status_code=status.HTTP_200_OK)
def get_event_by_id(id: int, db: Session=Depends(get_db)):

    stmt = select(EventDbModel).where(EventDbModel.id == id).limit(1)
    event = db.execute(stmt).scalar()

    if event is None:
        execute_on_exception(db, status.HTTP_404_NOT_FOUND, f"Nothing found")

    return event


@router.post("/", response_description="Create new event", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: BaseEvent, db: Session=Depends(get_db)):

    try:
        new_event = db.execute(
            insert(EventDbModel).returning(EventDbModel), 
            [{**event.model_dump()}]
        ).scalar()

    except:
        execute_on_exception(db, status.HTTP_403_FORBIDDEN, f"Error occuring while creating new event")
    else:
        db.commit()
        return new_event

@router.post("/list/", response_description="Create list of events", response_model=List[EventPreview], status_code=status.HTTP_201_CREATED)
def create_list_of_events(events: List[BaseEvent], db:Session=Depends(get_db)):

    try:
        events_to_add = []
        for i in range(len(events)):
            new_event = db.execute(
                insert(EventDbModel).returning(EventDbModel), 
                [{**events[i].model_dump()}]
            ).scalar()
            events_to_add.append(new_event)
    except:
        execute_on_exception(db, status.HTTP_400_BAD_REQUEST, f"Error occuring while adding list of events")
    else:

        db.commit()
        return events_to_add

@router.delete("/id/{id}", response_description="Delete event by id", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_event_by_id(id:int, db:Session=Depends(get_db)):
    try:
        db.execute(delete(EventDbModel).where(EventDbModel.id==id))
    except:
        execute_on_exception(db, status.HTTP_404_NOT_FOUND, f"event with id {id} not found")
    else:
        db.commit()

@router.delete("/", response_description="Delete all events", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
def delete_all_events(db:Session=Depends(get_db)):
    try:
        db.execute(delete(EventDbModel))
    except:
        execute_on_exception(db, status.HTTP_404_NOT_FOUND, f"no events")
    else:
        db.commit()

@router.get("/type/{type}", response_description="Get events by type", response_model=List[EventPreview], status_code=status.HTTP_200_OK)
def get_events_by_type(type:str, db:Session=Depends(get_db)):

    statement = select(EventDbModel.id, EventDbModel.type, EventDbModel.description).where(EventDbModel.type==type) 
    events = db.execute(statement).fetchall()
    if events==[]:
        execute_on_exception(db,status.HTTP_404_NOT_FOUND, f"there are no events with {type} type")
    else:
        return events


def execute_on_exception(db:Session, status_code,details):
    db.rollback()
    raise HTTPException(status_code, details)
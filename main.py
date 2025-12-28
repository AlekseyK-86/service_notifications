from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import select
from typing import List
from uuid import uuid4, UUID

from database import engine, Base, get_db
from models import Notification
from schema import NotificationCreate, NotificationResponse, NotificationUpdate


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification Service API.")


@app.post(
        "/notifications",
        response_model=NotificationResponse,
        status_code=status.HTTP_201_CREATED
    )
def create_notification(note: NotificationCreate, db=Depends(get_db)):
    db_note = Notification(
        id=uuid4(),
        user_id=note.user_id,
        notification=note.notification,
        send_at=note.send_at
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@app.get("/notifications", response_model=List[NotificationResponse])
def get_all_notifications(db=Depends(get_db)):
    query = select(Notification)
    notifications = db.scalars(query).all()
    return notifications


@app.get("/notifications/{note_id}", response_model=NotificationResponse)
def get_notification(note_id: UUID, db=Depends(get_db)):
    # note = session.get(Notification, note_id)
    get_note = select(Notification).where(Notification.id == note_id)
    result = db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return note


@app.put("/notifications/{note_id}", response_model=NotificationResponse)
def update_notification_full(
    note_id: UUID,
    item: NotificationCreate,
    db=Depends(get_db)
):
    get_note = select(Notification).where(Notification.id == note_id)    
    result = db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    note.user_id = item.user_id
    note.notification = item.notification
    note.send_at = item.send_at
    db.commit()
    db.refresh(note)
    return note


@app.patch("/notifications/{note_id}", response_model=NotificationResponse)
def update_notification_partial(
    note_id: UUID,
    item: NotificationUpdate,
    db=Depends(get_db)
):
    get_note = select(Notification).where(Notification.id == note_id)

    update_data = item.model_dump(exclude_unset=True)
    result = db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in update_data.items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note


@app.delete("/notifications/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(note_id: UUID, db=Depends(get_db)):
    get_note = select(Notification).where(Notification.id == note_id)
    result = db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(note)
    db.commit()
    return {"message": "Deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

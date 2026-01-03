from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends, Response
from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import uuid4, UUID

from database import engine, Base, get_db
from models import Notification
from schema import NotificationCreate, NotificationResponse, NotificationUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Асинхронное создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notification Service API.", lifespan=lifespan)


@app.post(
        "/notifications",
        response_model=NotificationResponse,
        status_code=status.HTTP_201_CREATED
    )
async def create_notification(note: NotificationCreate, db=Depends(get_db)):
    db_note = Notification(
        id=uuid4(),
        user_id=note.user_id,
        notification=note.notification,
        send_at=note.send_at
    )
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@app.get("/notifications", response_model=List[NotificationResponse])
async def get_all_notifications(db=Depends(get_db)):
    query = select(Notification)
    note = await db.scalars(query)
    notifications = note.all()
    return notifications


@app.get("/notifications/{note_id}", response_model=NotificationResponse)
async def get_notification(note_id: UUID, db=Depends(get_db)):
    get_note = select(Notification).where(Notification.id == note_id)
    # get_note = db.get(Notification, note_id)
    result = await db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return note


@app.put("/notifications/{note_id}", response_model=NotificationResponse)
async def update_notification_full(
    note_id: UUID,
    item: NotificationCreate,
    db=Depends(get_db)
):
    get_note = select(Notification).where(Notification.id == note_id)    
    result = await db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    note.user_id = item.user_id
    note.notification = item.notification
    note.send_at = item.send_at
    await db.commit()
    await db.refresh(note)
    return note


@app.patch("/notifications/{note_id}", response_model=NotificationResponse)
async def update_notification_partial(
    note_id: UUID,
    item: NotificationUpdate,
    db=Depends(get_db)
):
    get_note = select(Notification).where(Notification.id == note_id)

    update_data = item.model_dump(exclude_unset=True)
    result = await db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in update_data.items():
        if isinstance(value, datetime) and value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)
    return note


@app.delete("/notifications/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(note_id: UUID, db=Depends(get_db)):
    get_note = select(Notification).where(Notification.id == note_id)
    # get_note = db.get(Notification, note_id)
    result = await db.execute(get_note)
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.delete(note)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

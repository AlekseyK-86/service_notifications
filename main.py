from fastapi import FastAPI, HTTPException, status
from typing import List
from uuid import uuid4, UUID
from schema import NotificationCreate, NotificationResponse, NotificationUpdate
from database import db

app = FastAPI(title="Notification Service API.")


@app.post(
        "/notifications",
        response_model=NotificationResponse,
        status_code=status.HTTP_201_CREATED
    )
async def create_notification(note: NotificationCreate):
    new_note = NotificationResponse(id=uuid4(), **note.model_dump())
    db.append(new_note)
    return new_note


@app.get("/notifications", response_model=List[NotificationResponse])
async def get_all_notifications():
    return db


@app.get("/notifications/(note_id)", response_model=NotificationResponse)
async def get_notification(note_id: UUID):
    for note in db:
        if note.id == note_id:
            return note
    raise HTTPException(status_code=404, detail="Notification not found")


@app.put("/notifications/{note_id}", response_model=NotificationResponse)
async def update_notification_full(note_id: UUID, item: NotificationCreate):
    for index, note in enumerate(db):
        if note.id == note_id:
            update_note = NotificationResponse(id=note_id, **item.model_dump())
            db[index] = update_note
            return update_note
    raise HTTPException(status_code=404, detail="Notification not found")


@app.patch("/notifications/{note_id}", response_model=NotificationResponse)
async def update_notification_partial(note_id: UUID, item: NotificationUpdate):
    for index, note in enumerate(db):
        if note.id == note_id:
            update_data = item.model_dump(exclude_unset=True)
            updated_note = note.model_copy(update=update_data)
            db[index] = updated_note
            return updated_note
    raise HTTPException(status_code=404, detail="Notification not found")


@app.delete("/notifications/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(note_id: UUID):
    for index, note in enumerate(db):
        if note.id == note_id:
            db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Notification not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

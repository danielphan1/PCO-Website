from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # MVP stub; later: validate PDF, save to storage, write DB row
    return {"uploaded": True, "filename": file.filename}


@router.delete("/{event_id}")
def delete_event(event_id: int):
    return {"deleted": True, "event_id": event_id}

from fastapi import APIRouter, File, UploadFile, HTTPException, Path
from fastapi.responses import StreamingResponse
from minio import Minio
import io
import logging
# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    responses={404: {"description": "Not found"}} 
)

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET_NAME = "documents"

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)


@router.post("/tasks/{task_id}/upload-file/")
async def upload_file(task_id: str = Path(...), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        object_name = f"{task_id}/{file.filename}"

        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            data=io.BytesIO(contents),
            length=len(contents),
            content_type=file.content_type
        )
        return {"message": f"File '{file.filename}' uploaded to task '{task_id}' successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/list-files/")
def list_files(task_id: str = Path(...)):
    try:
        objects = minio_client.list_objects(BUCKET_NAME, prefix=f"{task_id}/")
        file_list = [
            {
                "filename": obj.object_name[len(task_id)+1:],
                "uploaded_at": obj.last_modified.strftime("%Y-%m-%d %H:%M:%S")
            }
            for obj in objects
        ]
        return {"task_id": task_id, "files": file_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}/download-file/{filename}")
def download_file(task_id: str = Path(...), filename: str = Path(...)):
    object_name = f"{task_id}/{filename}"
    try:
        response = minio_client.get_object(BUCKET_NAME, object_name)
        file_data = response.read()
        response.close()
        response.release_conn()

        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="routerlication/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")

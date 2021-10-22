from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form
from scripts import im2sql
from uuid import uuid4
import aiofiles
import settings
import os

router = APIRouter(prefix="/sqlify", tags=["Image2SQL"])


@router.post("/make", status_code=status.HTTP_201_CREATED)
async def make_table(typecheck: bool = Form(...), columns: int = Form(...), table_name: str = Form(...), includes_schema: bool = Form(...), uploadfile: UploadFile = File(...)):
    try:
        fname: str = f"{uuid4().hex}.png"
        floc: str = f"{settings.MEDIA_DIR}{fname}"

        async with aiofiles.open(floc, 'wb') as out_file:
            content = await uploadfile.read()
            await out_file.write(content)

        cmds, chks = im2sql.driver("/usr/bin/tesseract", floc, columns=columns, tablename=table_name.upper(), typecheck=typecheck, includes_schema=includes_schema)

        os.remove(floc)

        return {
            # "file_size": len(uploadfile),
            # "token": token,
            "status": status.HTTP_202_ACCEPTED,
            "file_content_type": uploadfile.content_type,
            "commands": cmds,
            "checks": chks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )
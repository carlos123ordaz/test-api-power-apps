from fastapi import FastAPI
from pydantic import BaseModel
import base64

app = FastAPI()


class Attachment(BaseModel):
    fileName: str
    contentType: str
    fileBase64: str
    emailFrom: str | None = None
    subject: str | None = None


@app.post("/saludar")
def saludar_post(data: Attachment):
    base64_str = data.fileBase64
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]

    file_bytes = base64.b64decode(base64_str)

    with open(data.fileName, "wb") as f:
        f.write(file_bytes)

    return {
        "mensaje": "Archivo recibido correctamente",
        "archivo": data.fileName
    }

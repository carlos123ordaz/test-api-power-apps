from fastapi import FastAPI
from pydantic import BaseModel
import base64

app = FastAPI(title="API de Saludo", version="1.0.0")


class Attachment(BaseModel):
    fileName: str
    contentType: str
    fileBase64: str
    emailFrom: str | None = None
    subject: str | None = None


@app.post("/saludar")
def saludar_post(data: Attachment):
    file_bytes = base64.b64decode(data.fileBase64)
    with open(data.fileName, "wb") as f:
        f.write(file_bytes)

    print(f"Archivo recibido: {data.fileName}")
    print(f"Correo de: {data.emailFrom}")

    return {
        "mensaje": "Archivo recibido correctamente",
        "archivo": data.fileName
    }

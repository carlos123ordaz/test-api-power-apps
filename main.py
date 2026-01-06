from fastapi import FastAPI
from pydantic import BaseModel
import base64
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Attachment(BaseModel):
    fileName: str
    contentType: str
    fileBase64: str
    emailFrom: str | None = None
    subject: str | None = None


@app.post("/saludar")
def saludar_post(data: Attachment):
    try:
        base64_str = data.fileBase64.strip()
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]
        base64_str = base64_str.encode(
            'ascii', errors='ignore').decode('ascii')
        base64_str = base64_str.replace(
            '\n', '').replace('\r', '').replace(' ', '')

        padding = len(base64_str) % 4
        if padding:
            base64_str += '=' * (4 - padding)

        file_bytes = base64.b64decode(base64_str)
        with open(data.fileName, "wb") as f:
            f.write(file_bytes)

        logger.info(
            f"Archivo recibido: {data.fileName} ({len(file_bytes)} bytes)")

        return {
            "mensaje": "Archivo recibido correctamente",
            "archivo": data.fileName,
            "tamaño": len(file_bytes)
        }

    except Exception as e:
        logger.error(f"Error procesando archivo: {str(e)}")
        return {
            "error": f"Error procesando archivo: {str(e)}",
            "archivo": data.fileName
        }, 400

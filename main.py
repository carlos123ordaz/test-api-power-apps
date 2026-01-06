from fastapi import FastAPI
from pydantic import BaseModel
import base64
import logging
from typing import List

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Attachment(BaseModel):
    fileName: str
    contentType: str
    fileBase64: str
    emailFrom: str | None = None
    subject: str | None = None


class BatchAttachments(BaseModel):
    attachments: List[Attachment]


def decode_base64(base64_str: str) -> bytes:
    base64_str = base64_str.strip()

    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]

    base64_str = base64_str.encode('ascii', errors='ignore').decode('ascii')
    base64_str = base64_str.replace(
        '\n', '').replace('\r', '').replace(' ', '')

    padding = len(base64_str) % 4
    if padding:
        base64_str += '=' * (4 - padding)

    return base64.b64decode(base64_str)


@app.post("/process/batch")
def saludar_batch(data: BatchAttachments):
    results = []
    errors = []

    email_info = f"De: {data.attachments[0].emailFrom}, Asunto: {data.attachments[0].subject}" if data.attachments else "Sin información"
    logger.info(f"Procesando {len(data.attachments)} archivos | {email_info}")

    for i, attachment in enumerate(data.attachments):
        try:
            file_bytes = decode_base64(attachment.fileBase64)

            with open(attachment.fileName, "wb") as f:
                f.write(file_bytes)

            results.append({
                "archivo": attachment.fileName,
                "tamaño": len(file_bytes),
                "estado": "éxito"
            })

            logger.info(
                f"✓ Archivo {i+1}: {attachment.fileName} ({len(file_bytes)} bytes) | De: {attachment.emailFrom} | Asunto: {attachment.subject}")

        except Exception as e:
            error_msg = f"Error procesando {attachment.fileName}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

    return {
        "mensaje": f"Procesados {len(results)} archivos correctamente",
        "archivos": results,
        "errores": errors if errors else None,
        "totalProcesado": len(results),
        "totalErrores": len(errors)
    }

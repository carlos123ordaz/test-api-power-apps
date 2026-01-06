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
    """Decodificar base64 de forma robusta"""
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


@app.post("/saludar/batch")
def saludar_batch(data: BatchAttachments):
    """Recibe múltiples archivos en un solo request"""
    results = []
    errors = []

    logger.info(f"Procesando {len(data.attachments)} archivos")

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
                f"✓ Archivo {i+1}: {attachment.fileName} ({len(file_bytes)} bytes)")

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


# Endpoint para recibir un solo archivo (compatible con tu flujo anterior)
@app.post("/saludar")
def saludar_post(data: Attachment):
    try:
        file_bytes = decode_base64(data.fileBase64)

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

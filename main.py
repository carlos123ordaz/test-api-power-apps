from fastapi import FastAPI

app = FastAPI(title="API de Saludo", version="1.0.0")


@app.get("/")
def root():
    return {"mensaje": "¡Bienvenido a la API de Saludo!"}


@app.post("/saludar")
def saludar_post():
    print("Saludo recibido")
    return {
        "mensaje": f"Recibimos tu saludo",
    }

import os
import uvicorn
import hashlib
import time
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage

# Importaciones de tus archivos locales
from models.usuario import Usuario
from services.usuario_service import UsuarioService

app = FastAPI(title="AI360 Backend", description="Backend para plataforma AI360")

# CONFIGURACIÓN DE CORS REFORZADA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

usuario_service = UsuarioService()
BUCKET_NAME = "usuarios_plataforma_ai360"

# --- MODELOS DE DATOS ---

def generar_hash_sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class LoginRequest(BaseModel):
    username: str
    password: str

class AltaUsuarioRequest(BaseModel):
    nuevo_usuario: Usuario

class ModificarUsuarioRequest(BaseModel):
    admin_user: str
    admin_password: str
    username: str  # Usuario objetivo
    updates: dict

class BajaUsuarioRequest(BaseModel):
    admin_user: str
    admin_password: str
    target_user: str # Nombre sincronizado con el Frontend

class CaptureRequest(BaseModel):
    username: str
    dashboard_type: str
    dashboard_url: str

# --- ENDPOINTS ---

@app.post("/login", tags=["Usuarios"])
def login(request: LoginRequest):
    valido, rol = usuario_service.verificar_usuario(request.username, request.password)
    if not valido:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Login exitoso", "rol": rol}

@app.get("/listar_usuarios", tags=["Admin"])
def listar_usuarios(admin_user: str, admin_password: str):
    try:
        usuarios = usuario_service.listar_usuarios(admin_user, admin_password)
        return {"usuarios": usuarios}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post("/modificar_usuario", tags=["Admin"])
def modificar_usuario(request: ModificarUsuarioRequest):
    try:
        exito = usuario_service.modificar_usuario(
            request.admin_user,
            request.admin_password,
            request.username,
            request.updates
        )
        if exito:
            return {"message": "Usuario actualizado correctamente"}
        raise HTTPException(status_code=400, detail="Error en la actualización")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/baja_usuario", tags=["Admin"])
def baja_usuario(request: BajaUsuarioRequest):
    try:
        exito = usuario_service.baja_usuario(
            request.admin_user,
            request.admin_password,
            request.target_user
        )
        if exito:
            return {"message": f"Usuario {request.target_user} eliminado"}
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generar_captura", tags=["Capturas"])
def generar_captura(request: CaptureRequest):
    try:
        nombre_archivo = f"cap_{request.username}_{int(time.time())}.png"
        contenido_binario = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff'
            b'\x3f\x00\x05\xfe\x02\xfe\x0dc\x44\xaf\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        client = storage.Client()
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob(f"capturas/{nombre_archivo}")
        blob.upload_from_string(contenido_binario, content_type='image/png')

        return Response(
            content=contenido_binario,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

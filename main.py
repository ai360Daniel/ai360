import os
import uvicorn
import hashlib
import time
from fastapi import FastAPI, HTTPException, Response  # Añadimos Response
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage  # Conexión real a Google Cloud

# Importaciones de tus archivos locales
from models.usuario import Usuario
from services.usuario_service import UsuarioService

app = FastAPI(title="AI360 Backend", description="Backend para plataforma AI360")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

usuario_service = UsuarioService()
# NOMBRE DE TU BUCKET CONFIRMADO
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
    username: str
    updates: dict

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

@app.post("/alta_usuario", tags=["Usuarios"])
def alta_usuario(request: AltaUsuarioRequest):
    try:
        password_plana = request.nuevo_usuario.password_hash
        request.nuevo_usuario.password_hash = generar_hash_sha256(password_plana)
        usuario_service.alta_usuario(request.nuevo_usuario)
        return {"message": "Usuario creado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ENDPOINT MODIFICADO PARA DESCARGA REAL Y SUBIDA AL BUCKET
@app.post("/generar_captura", tags=["Capturas"])
def generar_captura(request: CaptureRequest):
    try:
        # 1. Simulación de captura (Aquí Daniel integrará Puppeteer)
        time.sleep(1)
        nombre_archivo = f"cap_{request.username}_{int(time.time())}.png"
        contenido_binario = b"Contenido de captura AI360 para " + request.username.encode()

        # 2. SUBIDA REAL AL BUCKET usuarios_plataforma_ai360
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"capturas/{nombre_archivo}")
        
        blob.upload_from_string(
            contenido_binario,
            content_type='image/png'
        )

        # 3. RESPUESTA PARA DESCARGA AUTOMÁTICA EN PC DEL CLIENTE
        return Response(
            content=contenido_binario,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={nombre_archivo}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en bucket o captura: {str(e)}")

@app.get("/servicios/{username}", tags=["Servicios"])
def obtener_servicios(username: str):
    servicios = usuario_service.obtener_servicios_usuario(username)
    return {"username": username, "servicios": servicios}

@app.get("/servicios/{username}/{servicio}", tags=["Servicios"])
def verificar_acceso_servicio(username: str, servicio: str):
    tiene_acceso = usuario_service.validar_acceso_servicio(username, servicio)
    if not tiene_acceso:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return {"username": username, "servicio": servicio, "acceso": True}

@app.put("/modificar_usuario", tags=["Admin"])
def modificar_usuario(request: ModificarUsuarioRequest):
    try:
        usuario_service.modificar_usuario(request.admin_user, request.admin_password, request.username, request.updates)
        return {"message": "Usuario modificado exitosamente"}
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.delete("/baja_usuario", tags=["Admin"])
def baja_usuario(admin_user: str, admin_password: str, username: str):
    try:
        usuario_service.baja_usuario(admin_user, admin_password, username)
        return {"message": "Usuario eliminado exitosamente"}
    except (PermissionError, ValueError) as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/listar_usuarios", tags=["Admin"])
def listar_usuarios(admin_user: str, admin_password: str):
    try:
        usuarios = usuario_service.listar_usuarios(admin_user, admin_password)
        return {"usuarios": usuarios}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

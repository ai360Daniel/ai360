import os
import uvicorn
import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Importaciones de tus archivos locales
from models.usuario import Usuario
from services.usuario_service import UsuarioService

app = FastAPI(title="AI360 Backend", description="Backend para plataforma AI360")

usuario_service = UsuarioService()

# Función para encriptar contraseñas (Hash SHA256)
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
        # Hasheamos la contraseña antes de mandarla al servicio
        password_plana = request.nuevo_usuario.password_hash
        request.nuevo_usuario.password_hash = generar_hash_sha256(password_plana)
        
        usuario_service.alta_usuario(request.nuevo_usuario)
        return {"message": "Usuario creado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

# --- CONFIGURACIÓN PARA GOOGLE CLOUD RUN ---
if __name__ == "__main__":
    # Importante: Cloud Run inyecta el puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

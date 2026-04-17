from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from models.usuario import Usuario
from services.usuario_service import UsuarioService
import uvicorn
import os

app = FastAPI(title="AI360 Backend", description="Backend para plataforma AI360")

usuario_service = UsuarioService()

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

@app.post("/login")
def login(request: LoginRequest):
    valido, rol = usuario_service.verificar_usuario(request.username, request.password)
    if not valido:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Login exitoso", "rol": rol}

@app.post("/alta_usuario")
def alta_usuario(request: AltaUsuarioRequest):
    try:
        usuario_service.alta_usuario(request.nuevo_usuario)
        return {"message": "Usuario creado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/servicios/{username}")
def obtener_servicios(username: str):
    servicios = usuario_service.obtener_servicios_usuario(username)
    return {"username": username, "servicios": servicios}

@app.get("/servicios/{username}/{servicio}")
def verificar_acceso_servicio(username: str, servicio: str):
    tiene_acceso = usuario_service.validar_acceso_servicio(username, servicio)
    if not tiene_acceso:
        raise HTTPException(status_code=403, detail="Acceso denegado al servicio solicitado")
    return {"username": username, "servicio": servicio, "acceso": True}

@app.put("/modificar_usuario")
def modificar_usuario(request: ModificarUsuarioRequest):
    try:
        usuario_service.modificar_usuario(request.admin_user, request.admin_password, request.username, request.updates)
        return {"message": "Usuario modificado exitosamente"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/baja_usuario")
def baja_usuario(admin_user: str, admin_password: str, username: str):
    try:
        usuario_service.baja_usuario(admin_user, admin_password, username)
        return {"message": "Usuario eliminado exitosamente"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/listar_usuarios")
def listar_usuarios(admin_user: str, admin_password: str):
    try:
        usuarios = usuario_service.listar_usuarios(admin_user, admin_password)
        return {"usuarios": usuarios}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

# --- ESTA ES LA CORRECCIÓN PARA GOOGLE CLOUD RUN ---
if __name__ == "__main__":
    # Cloud Run define automáticamente la variable PORT
    port = int(os.environ.get("PORT", 8080))
    # Es vital usar host 0.0.0.0 para que Google pueda dirigir tráfico a la app
    uvicorn.run(app, host="0.0.0.0", port=port)
